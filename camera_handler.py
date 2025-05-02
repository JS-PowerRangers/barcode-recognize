import cv2
import config # Import file config de lay CAMERA_INDEX

class CameraHandler:
    def __init__(self, camera_index=config.CAMERA_INDEX):
        print(f"Dang khoi tao camera voi index: {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            print(f"Loi: Khong the mo camera voi index {camera_index}")
            self.cap = None # Dat la None de kiem tra sau nay
            return

        # Tuy chon: Co gang dat do phan giai neu duoc dinh nghia trong config
        # if hasattr(config, 'REQUESTED_WIDTH') and hasattr(config, 'REQUESTED_HEIGHT'):
        #     self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.REQUESTED_WIDTH)
        #     self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.REQUESTED_HEIGHT)

        # Lay do phan giai thuc te
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera mo thanh cong. Do phan giai: {self.width}x{self.height}")

    def is_opened(self):
        """Kiem tra camera co duoc mo thanh cong khong."""
        return self.cap is not None and self.cap.isOpened()

    def read_frame(self):
        """Doc mot frame tu camera."""
        if not self.is_opened():
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        """Giai phong camera."""
        if self.cap is not None:
            print("Giai phong camera...")
            self.cap.release()

    def get_resolution(self):
        """Tra ve do phan giai cua camera."""
        if not self.is_opened():
            return None, None
        return self.width, self.height