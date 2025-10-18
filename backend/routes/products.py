from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
from backend.db import get_connection
from backend.models import Product

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/")
def get_products():
    query = "SELECT * FROM products;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            products = cur.fetchall()
    return products


@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # Ensure it's a CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")

    # Read file contents
    content = await file.read()
    decoded = content.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(decoded))

    valid_rows = []
    invalid_rows = []

    for row in csv_reader:
        # Basic validation rules
        try:
            mrp = float(row["mrp"])
            price = float(row["price"])
            qty = int(row["quantity"])

            if price > mrp or qty < 0 or not row["sku"] or not row["name"] or not row["brand"]:
                invalid_rows.append(row)
                continue

            valid_rows.append(row)
        except Exception:
            invalid_rows.append(row)


    # Insert valid_rows into your database (e.g., PostgreSQL)
    with get_connection() as conn:
        with conn.cursor() as cur:
            for row in valid_rows:
                cur.execute("""
                    INSERT INTO products (
                            product_sku, 
                            product_name, 
                            product_brand, 
                            product_color, 
                            product_mrp, 
                            product_quantity
                    ) VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (product_sku) DO NOTHING;
                    """, (
                    row["sku"],
                    row["name"],
                    row["brand"],
                    row.get("color", None),
                    float(row["mrp"]),
                    int(row["quantity"])
                ))
        conn.commit()

    return JSONResponse(content={
        "stored": len(valid_rows),
        "failed": invalid_rows
    })
