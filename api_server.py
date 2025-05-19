from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import uvicorn
import threading
import asyncio # Need asyncio to run send_text from a different thread
import json # To serialize Pydantic models/dicts to JSON

import config
from models import Product, ScanResultWebSocketMessage # Import models

# This list will hold active WebSocket connections
# We need to access this list from the main thread
active_websockets: list[WebSocket] = []

def create_api_app() -> FastAPI:
    """Creates the FastAPI application instance with a WebSocket endpoint."""
    app = FastAPI(
        title="Barcode Scanner WebSocket Server",
        description="Provides a WebSocket endpoint to push scanned product info.",
        version="1.0.0"
    )

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket):
        """Handles incoming WebSocket connections."""
        await websocket.accept()
        active_websockets.append(websocket)
        print(f"WebSocket connection accepted from {websocket.client}. Total active: {len(active_websockets)}")
        try:
            # Keep the connection alive. Listen for messages (optional for push-only).
            # If the client sends data, process it here.
            # If not expecting client messages, this loop mainly handles disconnects.
            while True:
                # You can receive messages here if needed, e.g., keep-alives, commands
                # data = await websocket.receive_text()
                # print(f"Received message from {websocket.client}: {data}")
                # For a simple push server, you might just wait or pass
                await asyncio.sleep(60) # Keep the connection open, wait for pings/disconnects
                # A better approach for just staying alive might involve handling pings
                # or having the client send occasional keep-alives.
                # receive_text() or receive_bytes() will automatically raise WebSocketDisconnect on close

        except WebSocketDisconnect as e:
            # Handle client disconnect
            print(f"WebSocket disconnected: {websocket.client} (code: {e.code}, reason: {e.reason})")
        except Exception as e:
            # Handle other potential errors
            print(f"WebSocket error with client {websocket.client}: {e}")
        finally:
            # Clean up the connection
            if websocket in active_websockets:
                active_websockets.remove(websocket)
                print(f"WebSocket connection closed for {websocket.client}. Total active: {len(active_websockets)}")


    # Add a simple health check endpoint (optional, but good practice)
    @app.get("/health")
    async def health_check():
        """Basic health check."""
        return {"status": "ok", "message": "API is running"}

    return app

# Helper class to run the FastAPI application (including WebSocket) in a separate thread
class APIServerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        # Create the FastAPI app
        self.app = create_api_app()
        # Configure uvicorn server
        # Need to explicitly create the config and server to access the loop later
        self.config = uvicorn.Config(
            self.app,
            host=config.API_HOST,
            port=config.API_PORT,
            log_level="info"
            # Disable standard signal handlers as we're in a thread
            # https://github.com/encode/uvicorn/issues/742#issuecomment-645110915
            # log_config=None, # Optional: suppress uvicorn's logging if you manage it elsewhere
            # lifespan="off", # Or handle lifespan events properly if needed
        )
        self.server = uvicorn.Server(self.config)
        print(f"API server configured to run on http://{config.API_HOST}:{config.API_PORT} (WebSocket on /ws)")

    def run(self):
        """Starts the uvicorn server in this thread."""
        print("Starting API server thread...")
        # Note: Running uvicorn.run() or server.run() directly in a thread
        # can make graceful shutdown tricky. Using server.run() is standard.
        # The daemon=True setting in main.py helps ensure the app exits.
        try:
            # This runs the uvicorn server, including the WebSocket endpoint.
            # It blocks until the server stops.
            self.server.run()
        except Exception as e:
            print(f"API server thread encountered an error: {e}")

    # Method to get the list of active WebSocket connections
    def get_active_websockets(self) -> list[WebSocket]:
        return active_websockets

    # Method to get the asyncio loop where the server is running
    def get_asyncio_loop(self) -> asyncio.AbstractEventLoop:
         return self.server.config.loop

    # Note: A robust stop method would involve signaling uvicorn's server object
    # and potentially joining the thread, but daemon=True simplifies exit for demos.
    # For production, research graceful uvicorn shutdown in threads/processes.