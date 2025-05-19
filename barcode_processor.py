from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol
import time
import cv2 # Keep import in case future preprocessing is added

def process_barcodes(gray_frame):
    """
    Processes a grayscale frame to detect EAN-13 barcodes.

    Args:
        gray_frame: Grayscale image frame (NumPy array).

    Returns:
        tuple: (list_of_barcodes_info, latency)
            list_of_barcodes_info: List of dictionaries containing barcode info (data, type, rect).
                                   Returns empty list if no barcodes found.
            latency: Processing time in seconds.
    """
    start_time = time.perf_counter()

    # Specify to only look for EAN-13 symbols
    target_symbols = [ZBarSymbol.EAN13]

    # Decode barcodes. Pass the grayscale frame directly.
    # Add 'symbols' argument to restrict types.
    barcodes = pyzbar.decode(gray_frame, symbols=target_symbols)

    latency = time.perf_counter() - start_time

    processed_results = []
    if barcodes:
        for barcode in barcodes:
            # pyzbar returns bytes, decode to string
            try:
                barcode_data = barcode.data.decode('utf-8')
            except UnicodeDecodeError:
                 # Handle cases where data might not be UTF-8
                 barcode_data = str(barcode.data)
                 print(f"[Warning] UnicodeDecodeError for barcode data ({barcode.type}): {barcode.data}")

            barcode_info = {
                'data': barcode_data,
                'type': str(barcode.type),
                'rect': barcode.rect # (x, y, width, height) tuple
            }
            processed_results.append(barcode_info)

    return processed_results, latency