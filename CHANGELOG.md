# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

- Added pagination support for the products listing endpoint (`GET /products/`).
  - Uses `fastapi-pagination` and returns `Page[Product]` instead of a raw list.
  - Application is initialized with `add_pagination(app)` in `backend/main.py`.
  - Route `backend/routes/products.py` now calls `paginate(products)` and has `response_model=Page[Product]`.

## 2025-10-17

- Commit fa5d30579a464405500b6bfa2d8b4f77aaa1548e — "added pagination support for listing of products"
  - See changes in `backend/main.py` and `backend/routes/products.py`.
