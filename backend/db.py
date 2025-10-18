import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def get_connection():
    """Get PostgreSQL connection with dictionary-style cursor."""
    try:
        conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        raise


def init_db():
    """Initialize database table if not exists."""
    query = """
        CREATE TABLE IF NOT EXISTS products (
            id SERIAL PRIMARY KEY,
            product_sku VARCHAR(100) UNIQUE NOT NULL,
            product_name VARCHAR(255) NOT NULL,
            product_brand VARCHAR(100),
            product_color VARCHAR(50),
            product_mrp DECIMAL(10, 2) NOT NULL,
            product_quantity INT NOT NULL
        );"""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query)
        conn.commit()
