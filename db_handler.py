from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
import config

class DBHandler:
    """Handles database connection and product lookup."""
    def __init__(self):
        print("Connecting to MongoDB...")
        self.client = None
        self.db = None
        self.collection = None
        self._connect()

    def _connect(self):
        """Establishes the connection to MongoDB."""
        try:
            # Connect to MongoDB server
            self.client = MongoClient(config.MONGO_URI)
            # The ismaster command is cheap and does not require auth.
            self.client.admin.command('ismaster')
            print("MongoDB connection successful.")

            # Get database and collection
            self.db = self.client[config.MONGO_DATABASE]
            self.collection = self.db[config.MONGO_COLLECTION]
            print(f"Using database: {config.MONGO_DATABASE}, collection: {config.MONGO_COLLECTION}")

        except ConnectionFailure:
            print(f"Error: Could not connect to MongoDB at {config.MONGO_URI}")
            self.client = None
            self.db = None
            self.collection = None
        except Exception as e:
            print(f"An unexpected error occurred during MongoDB connection: {e}")
            self.client = None
            self.db = None
            self.collection = None


    def is_connected(self):
        """Checks if the database connection is active."""
        # Check if client is initialized and can perform a simple operation
        if self.client is None:
            return False
        try:
            # Ping the database to check connection health
            self.client.admin.command('ping')
            return True
        except:
            # If ping fails, connection is likely down
            print("MongoDB connection lost or failed ping.")
            return False

    def get_product_by_barcode(self, barcode_data: str):
        """
        Looks up a product in the database by barcode.

        Args:
            barcode_data: The string data from the scanned barcode (EAN-13).

        Returns:
            dict or None: The product document if found, otherwise None.
        """
        if not self.is_connected():
            print("Database not connected. Cannot perform lookup.")
            return None

        try:
            # Query the collection for a document matching the barcode
            product = self.collection.find_one({"barcode": barcode_data})
            # Remove MongoDB's ObjectId for easier handling in API response
            if product and "_id" in product:
                 product.pop("_id")
            return product
        except PyMongoError as e:
            print(f"An error occurred during database lookup for barcode {barcode_data}: {e}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during database lookup for barcode {barcode_data}: {e}")
            return None


    def close(self):
        """Closes the database connection."""
        if self.client:
            print("Closing MongoDB connection...")
            self.client.close()
            self.client = None
            self.db = None
            self.collection = None