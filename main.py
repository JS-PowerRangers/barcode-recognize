# main.py (Barcode Scanner - Relevant Sections Modified)

import cv2
import time
import config
import requests
import threading
import queue
import json # For creating the JSON string for Flutter
import re   # For parsing price from string

from camera_handler import CameraHandler
from barcode_processor import process_barcodes
from display_utils import draw_all_barcodes, draw_fps
from db_handler import DBHandler
# from models import ScanResultPayload # We are NOT sending this complex payload to Flutter anymore

# --- Global Queue for sending POST requests ---
post_queue = queue.Queue()

# --- Worker Thread Function for Sending POST Requests (largely unchanged, ensure it sends raw JSON) ---
def http_post_worker(post_queue: queue.Queue, target_url: str):
    """
    Worker thread function that continuously checks the queue for data
    and sends it via HTTP POST.
    """
    print("HTTP POST worker thread started.")
    while True:
        payload_json_string = post_queue.get() # Expecting a JSON string directly

        if payload_json_string is None:
            print("HTTP POST worker thread received stop signal. Exiting.")
            break

        print(f"Worker thread received payload. Attempting to POST to {target_url}...")
        try:
            response = requests.post(
                target_url,
                data=payload_json_string, # Send the pre-formatted JSON string
                headers={'Content-Type': 'application/json'},
                timeout=getattr(config, 'POST_TIMEOUT', 10) # Add a default timeout
            )
            if 200 <= response.status_code < 300:
                print(f"[INFO] POST request successful ({response.status_code}). Response: {response.json()}")
            else:
                print(f"[ERROR] POST request failed ({response.status_code}). Response: {response.text}")
        except requests.exceptions.Timeout:
             print(f"[ERROR] POST request to {target_url} timed out.")
        except requests.exceptions.ConnectionError:
            print(f"[ERROR] POST request to {target_url} failed: Connection Error.")
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] An unexpected error occurred during POST request to {target_url}: {e}")
        except Exception as e:
            print(f"[ERROR] An unexpected error in POST worker: {e}")

# --- Main Scanner Function ---
def run_scanner():
    print("Starting barcode scanner application...")
    print(f"Press '{chr(config.EXIT_KEY)}' to exit.")
    print(f"Scanned product data will be POSTed to: {config.TARGET_POST_URL}")

    post_worker_thread = threading.Thread(
        target=http_post_worker,
        args=(post_queue, config.TARGET_POST_URL),
        daemon=True
    )
    post_worker_thread.start()
    print("Background HTTP POST worker thread started.")

    db_handler = DBHandler()
    db_connected = db_handler.is_connected()
    if not db_connected:
        print("Warning: Database not connected.")

    camera = CameraHandler()
    if not camera.is_opened():
        print("Failed to open camera. Exiting.")
        db_handler.close()
        return

    last_time = time.perf_counter()
    frame_count = 0
    display_fps = 0
    last_scanned_barcode_data = None

    print("Starting video stream...")
    while True:
        ret, frame = camera.read_frame()
        if not ret:
            break

        display_frame = frame.copy()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detected_barcodes, latency = process_barcodes(gray_frame)
        current_scanned_barcode_data = None

        if detected_barcodes:
            first_barcode = detected_barcodes[0]
            current_scanned_barcode_data = first_barcode['data']

            if current_scanned_barcode_data != last_scanned_barcode_data:
                print(f"[INFO] New barcode detected: {current_scanned_barcode_data}. Looking up...")

                flutter_payload_json = None # Initialize to None

                if db_connected:
                    product_details_from_db = db_handler.get_product_by_barcode(current_scanned_barcode_data)
                    if product_details_from_db:
                        product_name = product_details_from_db.get('ten_san_pham') or product_details_from_db.get('ten') # Adjust field name as per your DB
                        price_str = product_details_from_db.get('gia_ban') or product_details_from_db.get('gia') # Adjust field name

                        if product_name and price_str:
                            try:
                                # Attempt to parse price (e.g., "30,000 VND" or "30000")
                                price_match = re.search(r'([\d,]+(?:\.\d+)?)', str(price_str))
                                if price_match:
                                    numeric_price_str = price_match.group(1).replace(',', '')
                                    numeric_price = float(numeric_price_str) # Use float for price

                                    # Prepare the SIMPLIFIED payload for Flutter
                                    flutter_payload_dict = {
                                        "name": product_name,
                                        "price": numeric_price,
                                        "quantity": 1 # Default quantity to 1
                                    }
                                    flutter_payload_json = json.dumps(flutter_payload_dict)
                                    print(f"[INFO] Product for Flutter: {product_name}, Price: {numeric_price}")
                                else:
                                    print(f"[WARN] Could not parse price from '{price_str}' for '{product_name}'.")

                            except ValueError as e:
                                print(f"[WARN] Error parsing price for '{product_name}': {e}")
                            except Exception as e:
                                print(f"[ERROR] Unexpected error preparing Flutter payload: {e}")
                        else:
                            print(f"[WARN] Product '{current_scanned_barcode_data}' found in DB but missing 'name' or 'price' for Flutter.")
                    else:
                        print(f"[INFO] Barcode '{current_scanned_barcode_data}' not found in DB.")
                else:
                     print(f"[WARN] Barcode '{current_scanned_barcode_data}' detected, but DB not connected.")

                # Queue the simplified payload for Flutter if it was created
                if flutter_payload_json:
                    try:
                        post_queue.put_nowait(flutter_payload_json)
                        print(f"Queued for Flutter: {flutter_payload_json}")
                    except queue.Full:
                        print("[WARN] POST queue is full. Dropping payload.")
                    except Exception as e:
                         print(f"[ERROR] An unexpected error occurred during queuing for Flutter: {e}")

                last_scanned_barcode_data = current_scanned_barcode_data
        else:
             last_scanned_barcode_data = None

        draw_all_barcodes(display_frame, detected_barcodes)
        frame_count += 1
        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            display_fps = frame_count / elapsed_time
            frame_count = 0
            last_time = current_time
        draw_fps(display_frame, display_fps)
        cv2.imshow(config.WINDOW_NAME, display_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == config.EXIT_KEY:
            break

    camera.release()
    cv2.destroyAllWindows()
    db_handler.close()
    print("Signaling POST worker thread to stop...")
    post_queue.put(None)
    # post_worker_thread.join() # Wait for worker if not daemon or for graceful shutdown
    print("Application terminated.")

if __name__ == "__main__":
    run_scanner()