from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Define Pydantic model for a Product based on MongoDB schema
# Note: _id is removed in DBHandler before returning, so we don't include it here
class Product(BaseModel):
    barcode: str # EAN-13 barcode used for lookup
    ma_sp: str
    ten: str
    gia: float
    mo_ta: str
    danh_muc: str
    thuong_hieu: str
    keywords: Optional[List[str]] # Optional, if you kept it

# Define Pydantic model for the data payload sent in the POST request body
class ScanResultPayload(BaseModel):
    status: str # "success", "not_found", "db_error"
    message: str
    scanned_barcode: str # The barcode that was scanned
    product_details: Optional[Product] = None # The product data from DB (matches Product model)