# Product Catalog Backend

This repository implements a small FastAPI backend for managing a product catalog. It provides endpoints to list products, upload products via CSV, and search/filter products.

This README documents how to set up the development environment, initialize the PostgreSQL database, run the project locally, and test the endpoints in detail.

## Table of contents
- Prerequisites
- Environment variables
- Project layout
- Install dependencies
- Database setup (PostgreSQL)
- Initialize the database schema
- Run the app locally
- Endpoints and examples
- CSV upload format and example
- Troubleshooting
- Next steps / Improvements

## Prerequisites

You will need:

- macOS, Linux, or Windows with WSL
- Python 3.10+ (the repository's venv in this workspace is used by tests by default)
- PostgreSQL (12+ recommended)
- pip (or pipx/poetry if you prefer)
- Optional: curl or httpie for endpoint testing, and a REST client like Postman

If you don't have PostgreSQL installed locally, you can run it with Docker (instructions below).

## Environment variables

Create a `.env` file in the project root (next to `backend/`) with the following variables. These are read by `backend/db.py` via python-dotenv.

```
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=127.0.0.1
DB_PORT=5432
```

Replace the values with your local database credentials. For local development, it's common to use `DB_USER=postgres` and the password you configured.

## Project layout

Relevant files and directories:

- `backend/` - application package
	- `main.py` - application entry (FastAPI app)
	- `db.py` - database helper functions (`get_connection`, `init_db`)
	- `models.py` - Pydantic models
	- `routes/products.py` - product-related endpoints (list, upload CSV, search)
- `data/` - sample CSVs and data
- `requirements.txt` - Python dependencies
- `README.md` - this file

## Install dependencies

1. Create and activate a virtual environment (recommended):

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install requirements:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Note: `requirements.txt` should include packages like `fastapi`, `uvicorn`, `psycopg2-binary`, `python-dotenv`, and `pydantic`. If any are missing, add them and re-run pip install.

## Database setup (PostgreSQL)

You have two common options: install PostgreSQL locally, or run it with Docker.

### Option A — Local PostgreSQL

Install PostgreSQL using Homebrew (macOS):

```bash
brew install postgresql
brew services start postgresql
```

Create a database and user (adjust names/passwords as needed):

```bash
createuser -s postgres  # if you want a superuser named postgres
createdb product_catalog_db
# or using psql:
psql -c "CREATE DATABASE product_catalog_db;"
psql -c "CREATE USER catalog_user WITH PASSWORD 'change_me';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE product_catalog_db TO catalog_user;"
```

Set `.env` accordingly.

### Option B — Docker (quick, isolated)

Run a PostgreSQL container:

```bash
docker run --name product-catalog-db -e POSTGRES_DB=product_catalog_db \
	-e POSTGRES_USER=catalog_user -e POSTGRES_PASSWORD=change_me -p 5432:5432 -d postgres:15
```

Then set `.env` values to match: `DB_NAME=product_catalog_db`, `DB_USER=catalog_user`, `DB_PASSWORD=change_me`, `DB_HOST=127.0.0.1`, `DB_PORT=5432`.

Confirm connectivity:

```bash
psql postgresql://catalog_user:change_me@127.0.0.1:5432/product_catalog_db -c "\dt"
```

## Initialize the database schema

The repo includes `backend/db.py` with an `init_db()` function which creates the `products` table if it doesn't exist.

From a Python REPL inside the activated virtualenv and project root you can run:

```bash
python -c "from backend.db import init_db; init_db(); print('DB initialized')"
```

This will create the `products` table with columns:

- id (serial primary key)
- product_sku (unique)
- product_name
- product_brand
- product_color
- product_mrp (decimal)
- product_quantity (int)

If you'd rather run SQL manually, use the `CREATE TABLE` statement present in `backend/db.py`.

## Run the app locally

Start the FastAPI app with uvicorn (assuming `backend.main` exposes `app`):

```bash
uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Open the interactive API docs at:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

If you get import or DB connection errors, verify your virtual environment, `.env` variables, and that PostgreSQL is reachable.

## Endpoints and examples

1) List all products

- Method: GET
- Path: `/products/`

Example using curl:

```bash
curl -sS http://127.0.0.1:8000/products/ | jq
```

2) Upload products via CSV

- Method: POST
- Path: `/products/upload`
- Content type: multipart/form-data
- Field name: `file` (CSV file)

Sample curl (replace `sample.csv` with your file):

```bash
curl -X POST "http://127.0.0.1:8000/products/upload" \
	-H "accept: application/json" \
	-H "Content-Type: multipart/form-data" \
	-F "file=@data/sample_products.csv;type=text/csv"
```

Response JSON contains `stored` (number of rows inserted) and `failed` (list of rows that failed validation).

3) Search products

All searches use a single endpoint. Use one of the following query forms on `/products/search`:

- Search by brand

	- Method: GET
	- Path: `/products/search` with `brand` query parameter
	- Example:

	```bash
	curl -sS "http://127.0.0.1:8000/products/search?brand=BrandA" | jq
	```

- Search by color

	- Method: GET
	- Path: `/products/search` with `color` query parameter
	- Example:

	```bash
	curl -sS "http://127.0.0.1:8000/products/search?color=red" | jq
	```

- Search by price range (MRP)

	- Method: GET
	- Path: `/products/search` with `min_price` and `max_price` query parameters
	- Example (both required for a range):

	```bash
	curl -sS "http://127.0.0.1:8000/products/search?min_price=100&max_price=200" | jq
	```

Notes:
- The endpoint accepts `brand`, `color`, or both `min_price` and `max_price` as query parameters. Use the appropriate keys shown above to perform the search you want.
- Matching for `brand` and `color` is case-insensitive and performed using SQL `ILIKE` with `%` wildcards for substring search.
- Price range search expects numeric `min_price` and `max_price` values. Provide both to search a range.

## CSV upload format and example

The upload endpoint expects a CSV with headers. The code expects the following headers to be present at a minimum:

- `sku` — product SKU (string, required)
- `name` — product name (string, required)
- `brand` — product brand (string, required)
- `color` — product color (optional)
- `mrp` — product MRP (decimal, required)
- `price` — selling price (decimal, required; must be <= mrp)
- `quantity` — product quantity (integer, required; must be >= 0)

Minimal sample (store as `data/sample_products.csv`):

```
sku,name,brand,color,mrp,price,quantity
SKU1,Running Shoes,BrandA,Red,100.00,90.00,10
SKU2,T-Shirt,BrandB,Blue,25.00,20.00,50
```

Important behavior:
- Rows where `price > mrp`, `quantity < 0`, or missing required fields are considered invalid and returned in the `failed` array of the response.
- On insert, the code uses `ON CONFLICT (product_sku) DO NOTHING`, so duplicate SKUs are ignored.

## Troubleshooting

- Database connection errors:
	- Confirm `.env` values and that PostgreSQL is reachable from your host/port. Use `psql` to test connectivity.
	- If using Docker, ensure the container is running and port 5432 is exposed.

- psycopg2 import/build issues:
	- On macOS you may need to install PostgreSQL client headers before installing `psycopg2-binary`. Usually `psycopg2-binary` is easiest, but if you use the non-binary `psycopg2`, ensure `brew install postgresql` or equivalent is done.

- CSV upload returns many failed rows:
	- Inspect the returned rows in the `failed` array for missing/invalid values.
	- Ensure CSV headers are exactly as expected (case-sensitive keys used by the parser).

## Next steps / Improvements

- Add tests:
	- Unit tests for the CSV parsing and validation logic.
	- Integration tests for endpoints (using a test database or Dockerized Postgres).
- Improve CSV error reporting: include row number and validation error messages.
- Add pagination for GET `/products/`.
- Make search filters more flexible (support single-sided price filters and multiple brands/colors).
- Add authentication/authorization for the upload endpoint.

---

If you'd like, I can add automated tests for the CSV parsing logic and the search SQL builder next. Which would you prefer I do first?
