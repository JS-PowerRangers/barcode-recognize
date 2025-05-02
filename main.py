import cv2
import time
import config
from camera_handler import CameraHandler
from barcode_processor import process_barcodes
from display_utils import draw_all_barcodes, draw_fps

def run_scanner():
    print("Khoi dong chuong trinh quét barcode (Modular Demo)...")
    print(f"Nhan '{chr(config.EXIT_KEY)}' de thoat.")

    # Khoi tao camera
    camera = CameraHandler()
    if not camera.is_opened():
        return # Ket thuc neu khong mo duoc camera

    # Bien cho tinh toan FPS
    last_time = time.perf_counter()
    frame_count = 0
    display_fps = 0

    while True:
        # 1. Doc frame
        ret, frame = camera.read_frame()
        if not ret:
            print("Loi: Khong the nhan frame. Dang thoat...")
            break

        # Sao chep frame de ve len, giu frame goc neu can
        display_frame = frame.copy()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 2. Xu ly barcode
        # detected_barcodes, latency = process_barcodes(frame)
        detected_barcodes, latency = process_barcodes(gray_frame)

        # In thong tin neu tim thay barcode
        if detected_barcodes:
            print(f"--- Frame moi --- Latency: {latency:.4f}s")
            for bc in detected_barcodes:
                print(f"[INFO] Tim thay {bc['type']}: {bc['data']}")

        # 3. Ve ket qua len frame hien thi
        draw_all_barcodes(display_frame, detected_barcodes)

        # 4. Tinh toan va ve FPS
        frame_count += 1
        current_time = time.perf_counter()
        elapsed_time = current_time - last_time
        if elapsed_time >= 1.0:
            display_fps = frame_count / elapsed_time
            frame_count = 0
            last_time = current_time
        draw_fps(display_frame, display_fps)

        # 5. Hien thi frame
        cv2.imshow(config.WINDOW_NAME, display_frame)

        # 6. Kiem tra phim thoat
        key = cv2.waitKey(1) & 0xFF
        if key == config.EXIT_KEY:
            print("Nhan phim thoat. Dang dong chuong trinh...")
            break

    # Don dep
    camera.release()
    cv2.destroyAllWindows()
    print("Chuong trinh da ket thuc.")

if __name__ == "__main__":
    run_scanner()