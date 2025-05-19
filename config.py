# Configuration for the barcode scanning application

# Camera
CAMERA_INDEX = 0  # Default camera index (usually 0 for built-in webcam)
# Set desired resolution (may not be supported by all cameras)
REQUESTED_WIDTH = 640
REQUESTED_HEIGHT = 480

# Display
WINDOW_NAME = 'Real-time Barcode Scanner (Modular Demo)'
SHOW_FPS = True
BOX_COLOR = (0, 255, 0)  # Green BGR
TEXT_COLOR = (0, 255, 0) # Green BGR
FPS_COLOR = (0, 0, 255)   # Red BGR
FONT_SCALE = 0.5
BOX_THICKNESS = 2
TEXT_THICKNESS = 2

# Control
EXIT_KEY = ord('q') # Press 'q' to exit

# Database (MongoDB)
MONGO_URI = "mongodb://localhost:27017/" # Your MongoDB connection string
MONGO_DATABASE = "shopdb"          # Your database name
MONGO_COLLECTION = "products"          # Your collection name

# API Server
API_HOST = "127.0.0.1" # Host for the API server
API_PORT = 8000        # Port for the API server
# Target HTTP POST Endpoint
TARGET_POST_URL = "http://localhost:5000/add_to_cart" # <-- Flutter Server