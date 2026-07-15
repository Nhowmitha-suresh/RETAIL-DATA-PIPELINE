from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

BASE_PATH = Path(__file__).resolve().parents[1] / "data"
DATA_PATH = BASE_PATH / "sales_enterprise.csv"

REGIONS = {
    "North": ["Delhi", "Lucknow", "Jaipur", "Chandigarh", "Patna"],
    "South": ["Bengaluru", "Chennai", "Hyderabad", "Pune", "Coimbatore"],
    "East": ["Kolkata", "Bhubaneswar", "Ranchi", "Guwahati", "Patna"],
    "West": ["Mumbai", "Ahmedabad", "Surat", "Goa", "Nagpur"],
    "Central": ["Bhopal", "Indore", "Raipur", "Nagpur", "Bhubaneswar"],
}

CATEGORIES = {
    "Electronics": ["Mobile", "Laptop", "Audio", "Wearable", "Gaming"],
    "Home": ["Furniture", "Kitchen", "Decor", "Appliances", "Bedding"],
    "Fashion": ["Men", "Women", "Kids", "Footwear", "Accessories"],
    "Groceries": ["Fresh", "Pantry", "Beverages", "Snacks", "Health"],
    "Sports": ["Fitness", "Outdoor", "Team Sports", "Footwear", "Apparel"],
    "Beauty": ["Skincare", "Makeup", "Hair", "Fragrance", "Wellness"],
}

BRANDS = [
    "Nexa", "Pulse", "Aurora", "Vertex", "Marquee", "Solace", "Prime", "Kinetic",
    "Lumiere", "Revive", "Optima", "Zenith", "Urbania", "Coreo", "Verve", "Astra",
]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Cash", "Wallet"]
ORDER_STATUS = ["Completed", "Pending", "Returned", "Cancelled", "Refunded"]
DEVICES = ["Desktop", "Mobile", "Tablet"]
CHANNELS = ["Online", "In-Store", "Mobile App"]
MEMBERSHIP_TIERS = ["Silver", "Gold", "Platinum", "Diamond"]
WEATHER = ["Sunny", "Cloudy", "Rainy", "Stormy", "Hot", "Cold"]
FESTIVALS = ["Diwali", "Holi", "Eid", "Christmas", "Navratri", "None"]
HOLIDAYS = [True, False]
COUPONS = ["SAVE10", "FESTIVE15", "WEEKEND5", "VIP20", "NEWUSER", "" ]

STORE_NAMES = [f"Store {chr(65 + i)}" for i in range(12)]
WAREHOUSES = [f"Warehouse {i+1}" for i in range(20)]
EMPLOYEES = [f"EMP{1000 + i}" for i in range(120)]
SUPPLIERS = [f"Supplier {i+1}" for i in range(250)]

GENDERS = ["Male", "Female", "Non-Binary"]
AGE_GROUPS = ["18-24", "25-34", "35-44", "45-54", "55+"]

PRODUCT_NAMES = [
    "Vertex 5G", "LumaSound Pro", "Astra Laptop", "Urban Dining Set", "Pulse Sport Watch",
    "Zenith Sofa", "Coreo Blender", "Revive Skincare Kit", "Optima Running Shoes",
    "Prime Gaming Kit", "Solace Mattress", "Aurora Haircare", "Marquee Jacket", "Verve Speaker",
]


def build_product_catalog(num_products: int = 5000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    categories = list(CATEGORIES.keys())
    products = []
    for product_id in range(1, num_products + 1):
        category = rng.choice(categories)
        subcategory = rng.choice(CATEGORIES[category])
        brand = rng.choice(BRANDS)
        cost = float(round(rng.uniform(150.0, 22000.0), 2))
        price = float(round(cost * rng.uniform(1.18, 1.75), 2))
        products.append(
            {
                "product_id": f"P{100000 + product_id}",
                "product_name": f"{brand} {subcategory} {product_id}",
                "category": category,
                "subcategory": subcategory,
                "brand": brand,
                "supplier_id": rng.choice(SUPPLIERS),
                "cost": cost,
                "selling_price": price,
            }
        )
    return pd.DataFrame(products)


def build_customer_list(num_customers: int = 20000) -> pd.DataFrame:
    rng = np.random.default_rng(65)
    customers = []
    age_group_weights = [0.18, 0.35, 0.25, 0.14, 0.08]
    tier_weights = [0.45, 0.30, 0.18, 0.07]
    for customer_id in range(1, num_customers + 1):
        gender = rng.choice(GENDERS)
        age_group = rng.choice(AGE_GROUPS, p=age_group_weights)
        tier = rng.choice(MEMBERSHIP_TIERS, p=tier_weights)
        customers.append(
            {
                "customer_id": f"C{200000 + customer_id}",
                "gender": gender,
                "age_group": age_group,
                "membership_tier": tier,
                "customer_type": rng.choice(["Retail", "Wholesale", "Loyal"]),
            }
        )
    return pd.DataFrame(customers)


def generate_timestamps(num_records: int, start_date: str = "2023-01-01", days: int = 730) -> np.ndarray:
    base = datetime.fromisoformat(start_date)
    increments = np.random.randint(0, days, size=num_records)
    times = [base + timedelta(days=int(dt)) for dt in increments]
    return np.array(times)


def generate_daily_sales(num_records: int = 250_000, output_path: Path | str | None = None) -> pd.DataFrame:
    output_path = Path(output_path or DATA_PATH)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    product_df = build_product_catalog()
    customer_df = build_customer_list()
    region_keys = list(REGIONS.keys())
    months = list(range(1, 13))
    quarters = ["Q1", "Q2", "Q3", "Q4"]

    rng = np.random.default_rng(97)
    num_records = int(num_records)
    roster = rng.integers(0, len(product_df), size=num_records)
    customer_idx = rng.integers(0, len(customer_df), size=num_records)
    region = rng.choice(region_keys, size=num_records, p=[0.22, 0.24, 0.18, 0.2, 0.16])
    city = [rng.choice(REGIONS[r]) for r in region]
    state = [f"{r} State" for r in region]
    store = rng.choice(STORE_NAMES, size=num_records)
    warehouse = rng.choice(WAREHOUSES, size=num_records)
    employee = rng.choice(EMPLOYEES, size=num_records)
    payment_method = rng.choice(PAYMENT_METHODS, size=num_records, p=[0.26, 0.22, 0.24, 0.14, 0.08, 0.06])
    channel = rng.choice(CHANNELS, size=num_records, p=[0.45, 0.3, 0.25])
    device = np.where(channel == "Online", rng.choice(DEVICES, size=num_records, p=[0.35, 0.5, 0.15]), "In-Store")
    promotion_used = rng.choice([True, False], size=num_records, p=[0.32, 0.68])
    coupon = [rng.choice(COUPONS) if promo else "" for promo in promotion_used]
    order_status = rng.choice(ORDER_STATUS, size=num_records, p=[0.82, 0.08, 0.05, 0.03, 0.02])
    quantity = rng.integers(1, 8, size=num_records)
    returns = np.where(order_status == "Returned", 1, 0)
    weather = rng.choice(WEATHER, size=num_records, p=[0.32, 0.26, 0.17, 0.08, 0.12, 0.05])
    festival = rng.choice(FESTIVALS, size=num_records, p=[0.12, 0.1, 0.08, 0.05, 0.04, 0.61])
    holiday = np.where(festival != "None", True, False)
    timestamps = generate_timestamps(num_records)
    month = [t.month for t in timestamps]
    quarter = [f"Q{((m - 1) // 3) + 1}" for m in month]
    year = [t.year for t in timestamps]
    financial_year = [f"FY{y}-{str(y + 1)[-2:]}" for y in year]
    delivery_days = rng.integers(1, 10, size=num_records)
    ratings = np.clip(np.round(rng.normal(4.2, 0.8, size=num_records), 1), 1.0, 5.0)
    shipping_cost = np.round(np.maximum(15.0, np.abs(rng.normal(45, 22, size=num_records))), 2)

    sale_rows = []
    product_ids = product_df["product_id"].to_numpy()
    product_lookup = product_df.set_index("product_id").to_dict("index")
    customer_ids = customer_df["customer_id"].to_numpy()
    customer_lookup = customer_df.set_index("customer_id").to_dict("index")

    for idx in range(num_records):
        pid = product_ids[roster[idx]]
        product = product_lookup[pid]
        cid = customer_ids[customer_idx[idx]]
        customer = customer_lookup[cid]
        qty = int(quantity[idx])
        tax_rate = 0.05 if product["category"] == "Groceries" else 0.12 if product["category"] == "Home" else 0.18
        base_price = product["selling_price"] * qty
        discount_pct = float(rng.choice([0, 5, 10, 15, 20, 25], p=[0.42, 0.2, 0.18, 0.12, 0.06, 0.02]))
        discount = float(round(base_price * discount_pct / 100, 2))
        tax = float(round((base_price - discount) * tax_rate, 2))
        revenue = float(round(base_price - discount + tax + shipping_cost[idx], 2))
        cost = float(round(product["cost"] * qty + shipping_cost[idx] * 0.2, 2))
        profit = float(round(revenue - cost - shipping_cost[idx] * 0.4, 2))
        order_value = float(round(revenue, 2))
        invoice_id = f"INV{6000000 + idx}"
        sale_rows.append(
            {
                "transaction_id": f"T{8000000 + idx}",
                "invoice_id": invoice_id,
                "customer_id": cid,
                "product_id": pid,
                "store": store[idx],
                "warehouse": warehouse[idx],
                "employee_id": employee[idx],
                "category": product["category"],
                "subcategory": product["subcategory"],
                "brand": product["brand"],
                "region": region[idx],
                "state": state[idx],
                "city": city[idx],
                "payment_method": payment_method[idx],
                "discount": discount,
                "tax": tax,
                "cost": cost,
                "selling_price": float(round(product["selling_price"] * qty, 2)),
                "profit": profit,
                "quantity": qty,
                "return_count": int(returns[idx]),
                "rating": ratings[idx],
                "delivery_days": int(delivery_days[idx]),
                "shipping_cost": shipping_cost[idx],
                "promotion_used": promotion_used[idx],
                "coupon_code": coupon[idx],
                "order_status": order_status[idx],
                "customer_gender": customer["gender"],
                "age_group": customer["age_group"],
                "membership_tier": customer["membership_tier"],
                "customer_type": customer["customer_type"],
                "purchase_channel": channel[idx],
                "device": device[idx],
                "order_timestamp": timestamps[idx],
                "month": month[idx],
                "quarter": quarter[idx],
                "financial_year": financial_year[idx],
                "weather": weather[idx],
                "festival_season": festival[idx],
                "holiday_indicator": bool(holiday[idx]),
                "supplier_id": product["supplier_id"],
            }
        )

    df = pd.DataFrame(sale_rows)
    df.to_csv(output_path, index=False)
    return df


if __name__ == "__main__":
    df = generate_daily_sales(250_000, DATA_PATH)
    print(f"Generated {len(df)} rows in {DATA_PATH}")
