"""
INTENTIONALLY VULNERABLE INVENTORY MANAGEMENT API
==================================================

⚠️  WARNING: This API contains INTENTIONAL security vulnerabilities for
educational and security testing purposes. DO NOT use in production!

OWASP TOP 10 (2021) VULNERABILITIES IMPLEMENTED:

A01:2021 - Broken Access Control
    - No authentication on sensitive endpoints (update, delete)
    - IDOR (Insecure Direct Object References)
    - Path traversal in file reading
    - Users can access/modify other users' data
    - Missing function level access control on admin endpoints

A02:2021 - Cryptographic Failures
    - Passwords stored in plain text
    - Sensitive data exposed in API responses (profit margins, costs)
    - Weak/predictable session tokens
    - Environment variables with secrets exposed
    - No encryption of sensitive data

A03:2021 - Injection
    - SQL Injection in multiple endpoints (search, category, user transactions)
    - Command Injection in admin/execute endpoint
    - Direct SQL query construction with user input

A04:2021 - Insecure Design
    - Mass assignment vulnerabilities
    - No rate limiting on any endpoint
    - Dangerous bulk update functionality
    - No business logic validation
    - Missing security requirements

A05:2021 - Security Misconfiguration
    - Debug mode enabled in production
    - CORS allows all origins
    - Verbose error messages with stack traces
    - API documentation exposed in production
    - System information disclosed
    - Default configurations used

A06:2021 - Vulnerable and Outdated Components
    - Using pickle for deserialization (inherently unsafe)
    - No dependency version pinning
    - Potential outdated package usage

A07:2021 - Identification and Authentication Failures
    - No password hashing
    - No password complexity requirements
    - SQL injection in login
    - Predictable session tokens
    - No rate limiting on authentication
    - No account lockout mechanism
    - Password reset without verification

A08:2021 - Software and Data Integrity Failures
    - Insecure deserialization using pickle
    - No input validation on critical operations
    - No integrity checks on data
    - Mass assignment without validation

A09:2021 - Security Logging and Monitoring Failures
    - No security event logging
    - No audit trails
    - No monitoring of suspicious activities
    - No alerting on security events

A10:2021 - Server-Side Request Forgery (SSRF)
    - Unrestricted URL fetching in admin/fetch-url
    - No URL validation or allow-list
    - Can access internal services

VULNERABLE ENDPOINTS:
    - /products/search/ - SQL Injection
    - /products/category/{category} - SQL Injection
    - /products/export/ - Sensitive Data Exposure
    - /admin/execute/ - Command Injection
    - /admin/fetch-url/ - SSRF
    - /admin/deserialize/ - Insecure Deserialization
    - /admin/read-file/ - Path Traversal
    - /auth/login/ - SQL Injection, No Password Hashing
    - /auth/register/ - No Input Validation
    - /auth/reset-password/ - No Authorization
    - /users/list/ - Broken Access Control
    - /debug/env/ - Information Disclosure
    - /inventory/adjust-by-query/ - SQL Injection
    - /products/bulk-update/ - Mass Assignment
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import models
import schemas
from database import engine, get_db
import os
import subprocess
import pickle
import base64
import requests

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
# OWASP A05: Security Misconfiguration - Debug mode enabled in production
app = FastAPI(
    title="Inventory Management API",
    description="FastAPI backend for product, inventory, and transaction management",
    version="1.0.0",
    debug=True,  # Vulnerable: Debug mode in production
    docs_url="/docs",  # Vulnerable: API docs exposed in production
    redoc_url="/redoc",
)

# OWASP A05: Security Misconfiguration - Permissive CORS policy
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Vulnerable: Allows all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# OWASP A09: Security Logging and Monitoring Failures - No logging configured
# No audit logs, no monitoring, no security event tracking


# ============= Product Endpoints =============


@app.post(
    "/products/",
    response_model=schemas.ProductWithInventory,
    status_code=status.HTTP_201_CREATED,
)
def create_product(product: schemas.ProductCreate, db: Session = Depends(get_db)):
    """Create a new product with initial inventory"""
    # Check if product already exists
    db_product = (
        db.query(models.Product).filter(models.Product.name == product.name).first()
    )
    if db_product:
        raise HTTPException(
            status_code=400, detail="Product with this name already exists"
        )

    # Create product
    db_product = models.Product(
        name=product.name,
        category=product.category,
        price=product.price,
        description=product.description,
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    # Create initial inventory
    db_inventory = models.Inventory(
        product_id=db_product.id,
        quantity=product.initial_quantity if product.initial_quantity else 0,
    )
    db.add(db_inventory)
    db.commit()
    db.refresh(db_product)

    return db_product


@app.get("/products/", response_model=List[schemas.ProductWithInventory])
def get_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all products with their inventory"""
    products = db.query(models.Product).offset(skip).limit(limit).all()
    return products


@app.get("/products/{product_id}", response_model=schemas.ProductWithInventory)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get a specific product by ID"""
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@app.get(
    "/products/category/{category}", response_model=List[schemas.ProductWithInventory]
)
def get_products_by_category(category: str, db: Session = Depends(get_db)):
    """Get all products in a specific category"""

    query = text(f"SELECT * FROM products WHERE category = '{category}'")
    try:
        result = db.execute(query)
        products = result.fetchall()
        return products
    except Exception as e:
        # OWASP A05: Security Misconfiguration - Verbose error messages
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(
    product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)
):
    """Update a product"""
    # OWASP A01: Broken Access Control - No authorization check
    # Any user can update any product without authentication
    db_product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # OWASP A08: Software and Data Integrity Failures - No input validation
    update_data = product.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_product, key, value)

    db.commit()
    db.refresh(db_product)
    return db_product


@app.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    """Delete a product (also deletes associated inventory and transactions)"""
    # OWASP A01: Broken Access Control - No authentication required for destructive operation
    db_product = (
        db.query(models.Product).filter(models.Product.id == product_id).first()
    )
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(db_product)
    db.commit()
    return None


@app.get("/products/search/")
def search_products(query: str, db: Session = Depends(get_db)):
    """Search products by name"""

    sql_query = text(
        f"SELECT * FROM products WHERE name LIKE '%{query}%' OR description LIKE '%{query}%'"
    )
    try:
        result = db.execute(sql_query)
        products = result.fetchall()
        return {"results": products, "query": query}
    except Exception as e:
        # OWASP A05: Security Misconfiguration - Exposing stack traces
        return {"error": str(e), "trace": str(e.__traceback__)}


@app.get("/products/export/")
def export_products(format: str = "json", db: Session = Depends(get_db)):
    """Export products information"""

    products = db.query(models.Product).all()
    result = []
    for p in products:
        result.append(
            {
                "id": p.id,
                "name": p.name,
                "category": p.category,
                "price": p.price,
                "description": p.description,
                "internal_cost": p.price * 0.6,
                "profit_margin": 0.4,
                "created_at": str(p.created_at),
                "updated_at": str(p.updated_at),
            }
        )
    return {"products": result, "total_count": len(result)}


# ============= Inventory Endpoints =============


@app.get("/inventory/", response_model=List[schemas.Inventory])
def get_all_inventory(db: Session = Depends(get_db)):
    """Get all inventory records"""
    inventory = db.query(models.Inventory).all()
    return inventory


@app.get("/inventory/{product_id}", response_model=schemas.Inventory)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    """Get inventory for a specific product"""
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.product_id == product_id)
        .first()
    )
    if inventory is None:
        raise HTTPException(
            status_code=404, detail="Inventory not found for this product"
        )
    return inventory


@app.put("/inventory/{product_id}", response_model=schemas.Inventory)
def update_inventory(
    product_id: int, inventory: schemas.InventoryUpdate, db: Session = Depends(get_db)
):
    """Update inventory for a product"""
    db_inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.product_id == product_id)
        .first()
    )
    if db_inventory is None:
        raise HTTPException(
            status_code=404, detail="Inventory not found for this product"
        )

    # Update only provided fields
    update_data = inventory.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_inventory, key, value)

    db.commit()
    db.refresh(db_inventory)
    return db_inventory


@app.get("/inventory/alerts/low-stock", response_model=List[schemas.StockAlert])
def get_low_stock_alerts(db: Session = Depends(get_db)):
    """Get all products with low stock levels"""
    inventory_items = db.query(models.Inventory).all()
    alerts = []

    for item in inventory_items:
        if item.quantity <= item.min_stock_level:
            product = (
                db.query(models.Product)
                .filter(models.Product.id == item.product_id)
                .first()
            )
            alert_type = "out_of_stock" if item.quantity == 0 else "low_stock"
            alerts.append(
                schemas.StockAlert(
                    product_id=item.product_id,
                    product_name=product.name,
                    current_quantity=item.quantity,
                    min_stock_level=item.min_stock_level,
                    alert_type=alert_type,
                )
            )

    return alerts


# ============= Admin/Utility Endpoints =============


@app.get("/admin/execute/")
def execute_command(cmd: str):
    """Execute system command"""

    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=5
        )
        return {
            "command": cmd,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/admin/fetch-url/")
def fetch_url(url: str):
    """Fetch content from URL"""

    try:
        response = requests.get(url, timeout=10)
        return {
            "url": url,
            "status_code": response.status_code,
            "content": response.text[:1000],  # First 1000 chars
            "headers": dict(response.headers),
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/admin/deserialize/")
def deserialize_data(data: str):
    """Deserialize pickled data"""

    try:
        decoded = base64.b64decode(data)
        obj = pickle.loads(decoded)  # Extremely dangerous!
        return {"result": str(obj)}
    except Exception as e:
        return {"error": str(e)}


@app.get("/admin/read-file/")
def read_file(filepath: str):
    """Read file from filesystem"""

    try:
        with open(filepath, "r") as f:
            content = f.read()
        return {"filepath": filepath, "content": content}
    except Exception as e:
        return {"error": str(e)}


# ============= Transaction Endpoints =============


@app.post(
    "/transactions/",
    response_model=schemas.Transaction,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction: schemas.TransactionCreate, db: Session = Depends(get_db)
):
    """Create a new transaction and update inventory accordingly"""
    # Check if product exists
    product = (
        db.query(models.Product)
        .filter(models.Product.id == transaction.product_id)
        .first()
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get inventory
    inventory = (
        db.query(models.Inventory)
        .filter(models.Inventory.product_id == transaction.product_id)
        .first()
    )
    if inventory is None:
        raise HTTPException(
            status_code=404, detail="Inventory not found for this product"
        )

    # Update inventory based on transaction type
    if transaction.transaction_type == "purchase":
        inventory.quantity += transaction.quantity
    elif transaction.transaction_type == "sale":
        if inventory.quantity < transaction.quantity:
            raise HTTPException(
                status_code=400, detail="Insufficient inventory for sale"
            )
        inventory.quantity -= transaction.quantity
    elif transaction.transaction_type == "adjustment":
        # Adjustment can be positive or negative based on the quantity sign
        # For now, treating as absolute adjustment
        inventory.quantity = transaction.quantity

    # Create transaction record
    db_transaction = models.Transaction(
        product_id=transaction.product_id,
        transaction_type=transaction.transaction_type,
        quantity=transaction.quantity,
        user_name=transaction.user_name,
        notes=transaction.notes,
    )

    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    return db_transaction


@app.get("/transactions/", response_model=List[schemas.Transaction])
def get_transactions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all transactions"""
    transactions = (
        db.query(models.Transaction)
        .order_by(models.Transaction.transaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@app.get("/transactions/product/{product_id}", response_model=List[schemas.Transaction])
def get_product_transactions(
    product_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all transactions for a specific product"""
    transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.product_id == product_id)
        .order_by(models.Transaction.transaction_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return transactions


@app.get("/transactions/user/{user_name}", response_model=List[schemas.Transaction])
def get_user_transactions(
    user_name: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    """Get all transactions for a specific user"""
    # OWASP A01: Broken Access Control - Users can view other users' transactions
    # OWASP A03: SQL Injection - Vulnerable query
    query = text(
        f"SELECT * FROM transactions WHERE user_name = '{user_name}' ORDER BY transaction_date DESC LIMIT {limit} OFFSET {skip}"
    )
    try:
        result = db.execute(query)
        transactions = result.fetchall()
        return transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


# ============= Authentication Endpoints (VULNERABLE) =============


@app.post("/auth/login/")
def login(username: str, password: str, db: Session = Depends(get_db)):
    """Login endpoint"""

    query = text(
        f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    )
    try:
        result = db.execute(query)
        user = result.fetchone()
        if user:
            # OWASP A02: Cryptographic Failures - Weak session management
            # No proper JWT or session token, just returning sensitive data
            return {
                "success": True,
                "user_id": user[0] if user else None,
                "username": username,
                "token": f"{username}:{'admin' if username == 'admin' else 'user'}",  # Predictable token
                "message": "Login successful",
            }
        else:
            # OWASP A05: Security Misconfiguration - Information disclosure
            return {
                "success": False,
                "message": f"Invalid credentials for user: {username}",
            }
    except Exception as e:
        # Table might not exist, but still vulnerable
        return {"success": False, "message": str(e)}


@app.post("/auth/register/")
def register(username: str, password: str, email: str, db: Session = Depends(get_db)):
    """Register new user"""

    try:
        # This will fail if users table doesn't exist, but demonstrates the vulnerability
        query = text(
            f"INSERT INTO users (username, password, email) VALUES ('{username}', '{password}', '{email}')"
        )
        db.execute(query)
        db.commit()
        return {
            "success": True,
            "message": "User registered successfully",
            "username": username,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/auth/reset-password/")
def reset_password(username: str, new_password: str, db: Session = Depends(get_db)):
    """Reset password"""

    try:
        query = text(
            f"UPDATE users SET password = '{new_password}' WHERE username = '{username}'"
        )
        db.execute(query)
        db.commit()
        return {"success": True, "message": f"Password reset for {username}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/users/list/")
def list_all_users(db: Session = Depends(get_db)):
    """List all users"""

    try:
        query = text("SELECT * FROM users")
        result = db.execute(query)
        users = result.fetchall()
        return {"users": users, "count": len(users)}
    except Exception as e:
        return {"error": str(e)}


@app.post("/products/bulk-update/")
def bulk_update_products(request: Request, db: Session = Depends(get_db)):
    """Bulk update products"""

    try:
        data = request.json()
        updated = []
        for item in data.get("products", []):
            product_id = item.get("id")
            if product_id:
                db_product = (
                    db.query(models.Product)
                    .filter(models.Product.id == product_id)
                    .first()
                )
                if db_product:
                    # Mass assignment - updating any field without validation
                    for key, value in item.items():
                        if hasattr(db_product, key):
                            setattr(db_product, key, value)
                    updated.append(product_id)
        db.commit()
        return {"success": True, "updated_count": len(updated), "updated_ids": updated}
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.get("/debug/env/")
def get_environment_variables():
    """Get environment variables"""

    return {
        "environment": dict(os.environ),
        "message": "All environment variables including secrets exposed!",
    }


@app.post("/inventory/adjust-by-query/")
def adjust_inventory_by_query(
    sql_where: str, adjustment: int, db: Session = Depends(get_db)
):
    """Adjust inventory with custom SQL"""

    try:
        query = text(
            f"UPDATE inventory SET quantity = quantity + {adjustment} WHERE {sql_where}"
        )
        result = db.execute(query)
        db.commit()
        return {"success": True, "rows_affected": result.rowcount, "query": sql_where}
    except Exception as e:
        return {"success": False, "error": str(e), "query": sql_where}


# ============= Health Check =============


@app.get("/")
def read_root():
    """Health check endpoint"""
    # OWASP A05: Security Misconfiguration - Exposing system information
    return {
        "status": "healthy",
        "message": "Inventory Management API is running",
        "version": "1.0.0",
        "debug_mode": True,  # Exposing debug status
        "python_version": os.sys.version,  # Exposing system info
        "database": "sqlite:///./inventory.db",  # Exposing database location
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
