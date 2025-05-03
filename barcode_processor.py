# ------------ File: barcode_processor.py ------------
from pyzbar import pyzbar
from pyzbar.pyzbar import ZBarSymbol # Quan trong: Import ZBarSymbol
import time
import cv2 # Import cv2 neu ban muon tien xu ly them o day

def process_barcodes(frame):
    """
    Args:
        frame: Frame anh dau vao (NumPy array - co the la anh mau hoac xam).

    Returns:
        tuple: (list_of_barcodes, latency)
            list_of_barcodes: Danh sach cac dictionary chua thong tin EAN-13 tim duoc.
            latency: Thoi gian xu ly (giay).
    """
    start_time = time.perf_counter()

    # --- Chi dinh CHI TIM EAN-13 ---
    # target_symbols = [ZBarSymbol.EAN13]
    # -----------------------------
    
    
    # --- TIEN XU LY (THU NGHIEM) ---
    # 1. Dam bao la anh xam (neu frame dau vao co the la anh mau)
    if len(frame.shape) == 3:
        proc_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    else:
        proc_frame = frame # Neu da la anh xam

    # 2. Thu lam mo nhe (GIUP GIAM NHIEU) - Bo comment de thu
    proc_frame = cv2.GaussianBlur(proc_frame, (3, 3), 0)

    # 3. Thu nhi phan hoa (LAM NOI BARCODE) - Bo comment de thu
    # _, proc_frame = cv2.threshold(proc_frame, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # Hoac dung Adaptive Thresholding neu anh sang khong deu
    proc_frame = cv2.adaptiveThreshold(proc_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    # -----------------------------

    # Su dung frame dau vao (co the la anh mau hoac xam tu main.py)
    # Them tham so `symbols` de chi dinh loai barcode can tim
    # barcodes = pyzbar.decode(frame, symbols=target_symbols)
    barcodes = pyzbar.decode(proc_frame)

    # --- DEBUG PRINT VAN GIU LAI ---
    # print(f"DEBUG: pyzbar.decode (EAN-13 only) returned: {barcodes}")
    # --- KET THUC DEBUG PRINT ---

    latency = time.perf_counter() - start_time

    processed_results = []
    if barcodes:
        for barcode in barcodes:
            try:
                barcode_data = barcode.data.decode('utf-8')
            except UnicodeDecodeError:
                 barcode_data = str(barcode.data)
                 print(f"[Warning] UnicodeDecodeError for barcode data ({barcode.type}): {barcode.data}")

            barcode_info = {
                'data': barcode_data,
                'type': str(barcode.type),
                'rect': barcode.rect 
            }
            processed_results.append(barcode_info)

    return processed_results, latency