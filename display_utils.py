import cv2
import config # Get colors, font, etc.

FONT = cv2.FONT_HERSHEY_SIMPLEX

def draw_single_barcode(frame, barcode_info):
    """Draws bounding box and text for a single barcode."""
    (x, y, w, h) = barcode_info['rect']
    data = barcode_info['data']
    type = barcode_info['type']

    # Draw bounding box
    cv2.rectangle(frame, (x, y), (x + w, y + h), config.BOX_COLOR, config.BOX_THICKNESS)

    # Prepare text
    text = f"{data} ({type})"

    # Calculate text position slightly above the box
    text_y = y - 10 if y - 10 > 10 else y + h + 20 # Prevent drawing outside top edge

    # Draw text
    cv2.putText(frame, text, (x, text_y), FONT, config.FONT_SCALE,
                config.TEXT_COLOR, config.TEXT_THICKNESS, cv2.LINE_AA)

def draw_all_barcodes(frame, barcodes_list):
    """Draws all barcodes in the list onto the frame."""
    for bc_info in barcodes_list:
        draw_single_barcode(frame, bc_info)

def draw_fps(frame, fps_value):
    """Draws the FPS value on the frame."""
    if config.SHOW_FPS:
        fps_text = f"FPS: {fps_value:.2f}"
        cv2.putText(frame, fps_text, (10, 30), FONT, 0.7,
                    config.FPS_COLOR, 2, cv2.LINE_AA) # Use larger font, antialiasing