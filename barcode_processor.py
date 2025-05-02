# ------------ File: barcode_processor.py ------------
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol # Quan trong: Import ZBarSymbol
import time
import cv2 # Import cv2 neu ban muon tien xu ly them o day

def process_barcodes(frame):
    """
    Phat hien va giai ma CHI LOAI EAN-13 trong frame va do latency.

    Args:
        frame: Frame anh dau vao (NumPy array - co the la anh mau hoac xam).

    Returns:
        tuple: (list_of_barcodes, latency)
            list_of_barcodes: Danh sach cac dictionary chua thong tin EAN-13 tim duoc.
            latency: Thoi gian xu ly (giay).
    """
    start_time = time.perf_counter()

    # --- Chi dinh CHI TIM EAN-13 ---
    target_symbols = [ZBarSymbol.EAN13, ZBarSymbol.QRCODE]
    # -----------------------------

    # Su dung frame dau vao (co the la anh mau hoac xam tu main.py)
    # Them tham so `symbols` de chi dinh loai barcode can tim
    barcodes = pyzbar.decode(frame, symbols=target_symbols)

    # --- DEBUG PRINT VAN GIU LAI ---
    # print(f"DEBUG: pyzbar.decode (EAN-13 only) returned: {barcodes}")
    # --- KET THUC DEBUG PRINT ---

    latency = time.perf_counter() - start_time

    processed_results = []
    if barcodes:
        # print(f"--- Found {len(barcodes)} potential EAN-13 barcode(s) ---") # Co the bo comment neu muon
        for barcode in barcodes:
            # Loai barcode se luon la EAN13 o day, nhung van kiem tra cho chac
            if barcode.type == 'EAN13':
                try:
                    barcode_data = barcode.data.decode('utf-8')
                except UnicodeDecodeError: # It xay ra voi EAN13 nhung van de phong
                    barcode_data = str(barcode.data)
                    print(f"[Warning] UnicodeDecodeError for EAN13 data: {barcode.data}")

                barcode_info = {
                    'data': barcode_data,
                    'type': barcode.type, # Se la 'EAN13'
                    'rect': barcode.rect
                }
                processed_results.append(barcode_info)
            # else: # Bo qua neu vi ly do nao do no tra ve loai khac (du da loc)
                # print(f"DEBUG: Ignored detected symbol of type {barcode.type}")
                # pass

    return processed_results, latency