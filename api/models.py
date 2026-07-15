from sqlalchemy import Column, String, Integer, Numeric, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
import uuid

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, index=True)
    gender = Column(String)
    age_group = Column(String)
    membership_tier = Column(String)
    customer_type = Column(String)
    created_at = Column(DateTime)

class Supplier(Base):
    __tablename__ = 'suppliers'
    supplier_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    contact_info = Column(JSONB)

class Product(Base):
    __tablename__ = 'products'
    product_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String, unique=True, index=True)
    name = Column(String)
    category = Column(String, index=True)
    subcategory = Column(String)
    brand = Column(String, index=True)
    supplier_id = Column(UUID(as_uuid=True), ForeignKey('suppliers.supplier_id'))
    cost = Column(Numeric(12,2))
    selling_price = Column(Numeric(12,2))
    supplier = relationship('Supplier')

class Warehouse(Base):
    __tablename__ = 'warehouses'
    warehouse_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    city = Column(String)
    region = Column(String)

class Store(Base):
    __tablename__ = 'stores'
    store_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    city = Column(String)
    state = Column(String)
    region = Column(String)

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transaction_id = Column(String, unique=True, index=True)
    invoice_id = Column(String)
    customer_id = Column(UUID(as_uuid=True), ForeignKey('customers.customer_id'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'))
    store = Column(String, index=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('warehouses.warehouse_id'))
    employee_id = Column(String)
    category = Column(String)
    subcategory = Column(String)
    brand = Column(String)
    region = Column(String, index=True)
    state = Column(String)
    city = Column(String)
    payment_method = Column(String)
    discount = Column(Numeric(12,2))
    tax = Column(Numeric(12,2))
    cost = Column(Numeric(12,2))
    selling_price = Column(Numeric(12,2))
    profit = Column(Numeric(12,2))
    quantity = Column(Integer)
    return_count = Column(Integer, default=0)
    rating = Column(Numeric(3,2))
    delivery_days = Column(Integer)
    shipping_cost = Column(Numeric(10,2))
    promotion_used = Column(Boolean, default=False)
    coupon_code = Column(String)
    order_status = Column(String, index=True)
    purchase_channel = Column(String)
    device = Column(String)
    order_timestamp = Column(DateTime, index=True)

class OrderItem(Base):
    __tablename__ = 'order_items'
    item_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey('orders.order_id'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('products.product_id'))
    quantity = Column(Integer)
    unit_price = Column(Numeric(12,2))
    total_price = Column(Numeric(12,2))
    order = relationship('Order')
    product = relationship('Product')
