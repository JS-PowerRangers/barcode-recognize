import cv2
import config

class CameraHandler:
    """Handles camera initialization, frame reading, and release."""
    def __init__(self, camera_index=config.CAMERA_INDEX):
        print(f"Initializing camera with index: {camera_index}...")
        self.cap = cv2.VideoCapture(camera_index)

        if not self.cap.isOpened():
            print(f"Error: Could not open camera with index {camera_index}")
            self.cap = None
            return

        # Attempt to set resolution if specified in config
        if hasattr(config, 'REQUESTED_WIDTH') and hasattr(config, 'REQUESTED_HEIGHT'):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.REQUESTED_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.REQUESTED_HEIGHT)

        # Get actual resolution
        self.width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        print(f"Camera opened successfully. Resolution: {self.width}x{self.height}")

    def is_opened(self):
        """Checks if the camera is successfully opened."""
        return self.cap is not None and self.cap.isOpened()

    def read_frame(self):
        """Reads a frame from the camera."""
        if not self.is_opened():
            return False, None
        ret, frame = self.cap.read()
        return ret, frame

    def release(self):
        """Releases the camera resource."""
        if self.cap is not None:
            print("Releasing camera...")
            self.cap.release()

    def get_resolution(self):
        """Returns the resolution of the camera."""
        if not self.is_opened():
            return None, None
        return self.width, self.height