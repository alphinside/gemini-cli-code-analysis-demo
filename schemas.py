from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    price: float = Field(..., gt=0)
    description: Optional[str] = None


class ProductCreate(ProductBase):
    initial_quantity: Optional[int] = Field(default=0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    price: Optional[float] = Field(None, gt=0)
    description: Optional[str] = None


class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductWithInventory(Product):
    inventory: Optional["Inventory"] = None


# Inventory Schemas
class InventoryBase(BaseModel):
    quantity: int = Field(..., ge=0)
    min_stock_level: int = Field(default=10, ge=0)
    max_stock_level: int = Field(default=1000, ge=0)


class InventoryCreate(InventoryBase):
    product_id: int


class InventoryUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = Field(None, ge=0)


class Inventory(InventoryBase):
    id: int
    product_id: int
    last_updated: datetime

    class Config:
        from_attributes = True


# Transaction Schemas
class TransactionBase(BaseModel):
    product_id: int
    transaction_type: str = Field(..., pattern="^(purchase|sale|adjustment)$")
    quantity: int = Field(..., gt=0)
    user_name: str = Field(..., min_length=1, max_length=100)
    notes: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class Transaction(TransactionBase):
    id: int
    transaction_date: datetime

    class Config:
        from_attributes = True


# Response Schemas
class StockAlert(BaseModel):
    product_id: int
    product_name: str
    current_quantity: int
    min_stock_level: int
    alert_type: str  # 'low_stock' or 'out_of_stock'
