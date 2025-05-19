import cv2
import time
import config
import requests
import threading # Import threading for background POST requests
import queue     # Import queue for inter-thread communication

from camera_handler import CameraHandler
from barcode_processor import process_barcodes
from display_utils import draw_all_barcodes, draw_fps
from db_handler import DBHandler
from models import ScanResultPayload # Import the Pydantic model for the POST payload

# --- Global Queue for sending POST requests ---
# This queue will hold the JSON payloads to be sent.
# The main thread puts data into the queue, the worker thread takes data out.
post_queue = queue.Queue()

# --- Worker Thread Function for Sending POST Requests ---
def http_post_worker(post_queue: queue.Queue, target_url: str):
    """
    Worker thread function that continuously checks the queue for data
    and sends it via HTTP POST. Handles connection errors gracefully.
    """
    print("HTTP POST worker thread started.")
    while True:
        # Wait for a payload dictionary from the queue
        # block=True means it will wait here until an item is available
        # timeout=None means it waits indefinitely unless None is received
        payload_json_string = post_queue.get()

        # Check for the sentinel value (None) to signal shutdown
        if payload_json_string is None:
            print("HTTP POST worker thread received stop signal. Exiting.")
            post_queue.task_done() # Important if queue.join() is used
            break

        print(f"Worker thread received payload from queue. Attempting to POST to {target_url}...")

        try:
            # Send the POST request
            response = requests.post(
                target_url,
                data=payload_json_string, # Send JSON string as data
                headers={'Content-Type': 'application/json'}, # Specify content type
                timeout=config.POST_TIMEOUT # Use timeout from config
            )

            # Check the response status code
            if response.status_code >= 200 and response.status_code < 300:
                print(f"[INFO] POST request successful ({response.status_code}).")
                # Optional: Print a snippet of the response
                # print(f"  Server responded: {response.text[:200]}...")
            else:
                print(f"[ERROR] POST request failed ({response.status_code}). Response:")
                # print(f"  {response.text[:200]}...") # Print a snippet of the error response

        except requests.exceptions.Timeout:
             print(f"[ERROR] POST request to {target_url} timed out after {config.POST_TIMEOUT} seconds.")
        except requests.exceptions.ConnectionError as e:
            print(f"[ERROR] POST request to {target_url} failed: Connection Error. Server likely offline or unreachable.")
            # print(f"  Error details: {e}") # Optional: Print error details
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] An unexpected error occurred during POST request to {target_url}: {e}")
        except Exception as e:
            print(f"[ERROR] An unexpected error occurred in POST worker: {e}")


        # Indicate that the task for this item is done
        # post_queue.task_done() # Use if you call post_queue.join() later


# --- Main Scanner Function ---
def run_scanner():
    """Main function to run the barcode scanner with DB lookup and HTTP POST."""
    print("Starting barcode scanner application (Modular Demo)...")
    print(f"Press '{chr(config.EXIT_KEY)}' to exit.")
    print(f"Scanned product data will be POSTed to: {config.TARGET_POST_URL}")

    # Initialize and start the background POST worker thread
    # This thread will run the http_post_worker function,
    # consuming items from the global post_queue.
    post_worker_thread = threading.Thread(
        target=http_post_worker,
        args=(post_queue, config.TARGET_POST_URL),
        daemon=True # Set as daemon so it exits automatically when main thread exits
                   # For clean shutdown, manage manually (daemon=False, then thread.join())
    )
    post_worker_thread.start()
    print("Background HTTP POST worker thread started.")


    # Initialize database handler
    db_handler = DBHandler()
    db_connected = db_handler.is_connected()
    if not db_connected:
        print("Warning: Database not connected. Running scanner without DB lookup capabilities.")


    # Initialize camera
    camera = CameraHandler()
    if not camera.is_opened():
        print("Failed to open camera. Exiting.")
        db_handler.close() # Close DB connection if camera fails
        # No need to explicitly stop daemon thread, it exits with main
        return # Exit if camera cannot be opened


    # Variables for FPS calculation
    last_time = time.perf_counter()
    frame_count = 0
    display_fps = 0

    print("Starting video stream. Look for barcodes...")

    # Keep track of the last successfully processed barcode data
    # To avoid sending duplicate POST requests for the same barcode in consecutive frames
    last_scanned_barcode_data = None
    # A small delay counter could be added here if you want to re-POST the same barcode
    # after a certain time, even if it's still in view.


    while True:
        # 1. Read frame from camera
        ret, frame = camera.read_frame()
        if not ret:
            print("Error: Cannot receive frame from camera. Exiting...")
            break

        # Prepare frames for display and processing
        display_frame = frame.copy()
        # Convert to grayscale for barcode processing as it's often more robust
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. Process barcodes using the grayscale frame
        detected_barcodes, latency = process_barcodes(gray_frame)

        # 3. Handle detected barcodes (lookup in DB and prepare payload)
        # We'll process the first detected barcode if any
        current_scanned_barcode_data = None # Data from the current frame scan


        if detected_barcodes:
            first_barcode = detected_barcodes[0]
            current_scanned_barcode_data = first_barcode['data']
            barcode_type = first_barcode['type']
            # Print detection info with processing latency
            # Only print INFO message for the first detection in a sequence
            if current_scanned_barcode_data != last_scanned_barcode_data:
                 print(f"--- Frame new --- Latency: {latency:.4f}s. Detected {barcode_type}: {current_scanned_barcode_data}")

            # Check if this is a new barcode or the first time seeing it in a sequence
            if current_scanned_barcode_data != last_scanned_barcode_data:
                print(f"[INFO] New barcode detected: {current_scanned_barcode_data}. Performing lookup and queuing POST.")

                product_details = None # Placeholder for DB result
                payload_data_dict = None # Data structure for the POST body

                if db_connected:
                    # Perform database lookup if connected
                    product_details = db_handler.get_product_by_barcode(current_scanned_barcode_data)

                    if product_details:
                        print(f"[INFO] Product found in DB: {product_details.get('ten')} - Gia: {product_details.get('gia'):,.0f} VND")
                        # Prepare success payload data
                        payload_data_dict = {
                            "status": "success",
                            "message": "Product found in database.",
                            "scanned_barcode": current_scanned_barcode_data,
                            "product_details": product_details # DB dict is fine here
                        }
                    else:
                        print(f"[INFO] Barcode '{current_scanned_barcode_data}' not found in DB.")
                        # Prepare not_found payload data
                        payload_data_dict = {
                            "status": "not_found",
                            "message": f"Barcode '{current_scanned_barcode_data}' scanned but not found in database.",
                            "scanned_barcode": current_scanned_barcode_data,
                            "product_details": None
                        }

                else:
                     # Handle case where DB is not connected but barcode is detected
                     print(f"[INFO] Barcode '{current_scanned_barcode_data}' detected, but database connection is not available. Cannot lookup details.")
                     # Prepare DB error payload data
                     payload_data_dict = {
                         "status": "db_error", # Use db_error status
                         "message": f"Barcode '{current_scanned_barcode_data}' detected, but database connection failed. Cannot lookup product details.",
                         "scanned_barcode": current_scanned_barcode_data,
                         "product_details": None
                     }

                # 4. Put the payload data (as JSON string) onto the queue for the worker thread
                if payload_data_dict:
                    try:
                         # Use the Pydantic model to create a validated payload object
                         payload_model = ScanResultPayload(**payload_data_dict)
                         # Convert Pydantic model to JSON string
                         payload_json_string = payload_model.model_dump_json() # or .json() for older pydantic

                         # Put the JSON string onto the queue. put_nowait() doesn't block.
                         post_queue.put_nowait(payload_json_string)
                         print(f"Queued POST payload for barcode: {current_scanned_barcode_data}")

                    except Exception as e:
                         print(f"[ERROR] An unexpected error occurred during payload creation/queuing: {e}")

                # Update last scanned barcode data AFTER queuing the POST attempt
                # This prevents spamming the queue with the same barcode if it stays in view.
                last_scanned_barcode_data = current_scanned_barcode_data


        else:
             # No barcode detected in this frame
             # Reset last scanned data so the next detection triggers a new POST attempt
             last_scanned_barcode_data = None


        # 5. Draw results on the display frame (bounding boxes and text)
        # Drawing still uses the detected barcodes list from the current frame
        draw_all_barcodes(display_frame, detected_barcodes)


        # 6. Calculate and draw FPS on the display frame
        frame_count += 1
        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            display_fps = frame_count / elapsed_time
            frame_count = 0
            last_time = current_time
        draw_fps(display_frame, display_fps)

        # 7. Display the frame in a window
        cv2.imshow(config.WINDOW_NAME, display_frame)

        # 8. Check for exit key press (e.g., 'q')
        key = cv2.waitKey(1) & 0xFF
        if key == config.EXIT_KEY:
            print(f"'{chr(config.EXIT_KEY)}' key pressed. Shutting down...")
            break

    # Cleanup resources upon exiting the loop
    camera.release() # Release camera resource
    cv2.destroyAllWindows() # Close all OpenCV windows
    db_handler.close() # Close database connection

    # Signal the worker thread to exit by putting None on the queue
    # If daemon=True, this is not strictly necessary as the thread will be killed,
    # but it's good practice for clean shutdown.
    # For non-daemon threads, you *must* put None and then post_worker_thread.join()
    # to wait for it to finish processing remaining items.
    print("Signaling POST worker thread to stop...")
    post_queue.put(None)
    # If using daemon=False, uncomment the next line to wait for the worker to finish:
    # post_worker_thread.join()

    print("Application terminated.")


if __name__ == "__main__":
    run_scanner()