from typing import Optional
from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import csv
import io
from backend.db import get_connection
from backend.models import Product
from fastapi_pagination import Page, paginate

router = APIRouter(prefix="/products", tags=["products"])

@router.get("/", response_model=Page[Product])
def get_products():
    query = "SELECT * FROM products;"
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
            products = cur.fetchall()
    return paginate(products)


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


@router.get("/search", response_model=Page[Product])
def search_products_by_brand(
    brand: Optional[str] = None,
    color: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
    ):
    # Build SQL with safe %s placeholders for psycopg2 and combine conditions with AND.
    conditions = []
    params = []

    sql_query = "SELECT * FROM products"

    if color:
        conditions.append("product_color ILIKE %s")
        params.append(f"%{color}%")

    if min_price is not None and max_price is not None:
        conditions.append("product_mrp >= %s AND product_mrp <= %s")
        params.append(min_price)
        params.append(max_price)

    if brand:
        conditions.append("product_brand ILIKE %s")
        params.append(f"%{brand}%")

    if conditions:
        sql_query = sql_query + " WHERE " + " AND ".join(conditions)

    # Execute the query and fetch results
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql_query, params)
            products = cur.fetchall()

    return paginate(products)
