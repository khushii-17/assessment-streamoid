from pydantic import BaseModel

class Product(BaseModel):
    product_sku: str
    product_name: str
    product_brand: str
    product_color: str
    product_mrp: float
    product_quantity: int
