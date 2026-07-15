-- Retail Intelligence Enterprise DB Schema (PostgreSQL)
-- Normalized schema with indexes and FK constraints

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Customers
CREATE TABLE customers (
  customer_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id TEXT UNIQUE,
  gender TEXT,
  age_group TEXT,
  membership_tier TEXT,
  customer_type TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_customers_age ON customers(age_group);

-- Suppliers
CREATE TABLE suppliers (
  supplier_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT,
  contact_info JSONB
);

-- Employees
CREATE TABLE employees (
  employee_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  employee_code TEXT UNIQUE,
  name TEXT,
  role TEXT,
  store TEXT
);

-- Warehouses
CREATE TABLE warehouses (
  warehouse_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name TEXT,
  city TEXT,
  region TEXT
);

-- Products
CREATE TABLE products (
  product_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  external_id TEXT UNIQUE,
  name TEXT,
  category TEXT,
  subcategory TEXT,
  brand TEXT,
  supplier_id UUID REFERENCES suppliers(supplier_id) ON DELETE SET NULL,
  cost NUMERIC(12,2),
  selling_price NUMERIC(12,2)
);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_brand ON products(brand);

-- Inventory
CREATE TABLE inventory (
  inventory_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  product_id UUID REFERENCES products(product_id) ON DELETE CASCADE,
  warehouse_id UUID REFERENCES warehouses(warehouse_id) ON DELETE CASCADE,
  stock_qty INTEGER DEFAULT 0,
  reserved_qty INTEGER DEFAULT 0,
  last_updated TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX idx_inventory_product ON inventory(product_id);

-- Orders (transactions)
CREATE TABLE orders (
  order_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  transaction_id TEXT UNIQUE,
  invoice_id TEXT,
  customer_id UUID REFERENCES customers(customer_id),
  product_id UUID REFERENCES products(product_id),
  store TEXT,
  warehouse_id UUID REFERENCES warehouses(warehouse_id),
  employee_id UUID REFERENCES employees(employee_id),
  category TEXT,
  subcategory TEXT,
  brand TEXT,
  region TEXT,
  state TEXT,
  city TEXT,
  payment_method TEXT,
  discount NUMERIC(12,2),
  tax NUMERIC(12,2),
  cost NUMERIC(12,2),
  selling_price NUMERIC(12,2),
  profit NUMERIC(12,2),
  quantity INTEGER,
  return_count INTEGER DEFAULT 0,
  rating NUMERIC(3,2),
  delivery_days INTEGER,
  shipping_cost NUMERIC(10,2),
  promotion_used BOOLEAN DEFAULT FALSE,
  coupon_code TEXT,
  order_status TEXT,
  purchase_channel TEXT,
  device TEXT,
  order_timestamp TIMESTAMP WITH TIME ZONE,
  month INTEGER,
  quarter TEXT,
  financial_year TEXT,
  weather TEXT,
  festival_season TEXT,
  holiday_indicator BOOLEAN,
  supplier_id UUID REFERENCES suppliers(supplier_id),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE INDEX idx_orders_ts ON orders(order_timestamp);
CREATE INDEX idx_orders_region ON orders(region);
CREATE INDEX idx_orders_store ON orders(store);
CREATE INDEX idx_orders_product ON orders(product_id);
CREATE INDEX idx_orders_customer ON orders(customer_id);

-- Payments
CREATE TABLE payments (
  payment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
  amount NUMERIC(12,2),
  method TEXT,
  status TEXT,
  paid_at TIMESTAMP WITH TIME ZONE
);

-- Shipments
CREATE TABLE shipments (
  shipment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
  shipped_at TIMESTAMP WITH TIME ZONE,
  delivered_at TIMESTAMP WITH TIME ZONE,
  carrier TEXT,
  tracking JSONB
);

-- Returns
CREATE TABLE returns (
  return_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
  reason TEXT,
  refund_amount NUMERIC(12,2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Reviews
CREATE TABLE reviews (
  review_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  order_id UUID REFERENCES orders(order_id) ON DELETE CASCADE,
  rating NUMERIC(3,2),
  comment TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Promotions
CREATE TABLE promotions (
  promotion_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  code TEXT UNIQUE,
  description TEXT,
  discount_pct NUMERIC(5,2),
  start_date DATE,
  end_date DATE
);

-- Audit logs
CREATE TABLE audit_logs (
  audit_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  actor TEXT,
  action TEXT,
  resource_type TEXT,
  resource_id TEXT,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Materialized view for fast KPIs
CREATE MATERIALIZED VIEW mv_kpis AS
SELECT
  COUNT(o.*) FILTER (WHERE o.order_status = 'Completed') AS completed_orders,
  SUM(o.selling_price) AS total_revenue,
  SUM(o.profit) AS total_profit,
  SUM(o.selling_price) - SUM(o.cost) AS gross_margin,
  COUNT(DISTINCT o.customer_id) AS unique_customers,
  MAX(o.order_timestamp) AS last_order_ts
FROM orders o;

-- Indexes for performance
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_order_ts ON orders(order_timestamp DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_region_store ON orders(region, store);

-- Helpers
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
