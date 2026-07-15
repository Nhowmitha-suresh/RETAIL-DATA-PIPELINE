"""Generate enterprise-grade CSV datasets for PostgreSQL import.
Creates normalized CSVs: suppliers, products, customers, warehouses, stores, orders, order_items.
Designed for streaming large datasets (500k+ orders).
"""
import csv
import random
import uuid
from datetime import datetime, timedelta
from faker import Faker
import os

OUTDIR = os.path.join(os.path.dirname(__file__), '..', 'data')
os.makedirs(OUTDIR, exist_ok=True)

fake = Faker()

NUM_SUPPLIERS = 500
NUM_PRODUCTS = 15000
NUM_CUSTOMERS = 50000
NUM_WAREHOUSES = 100
NUM_STORES = 200
NUM_ORDERS = 500000  # 500k orders

START_DATE = datetime.now() - timedelta(days=365*10)  # 10 years

CURRENCIES = ['INR']
CATEGORIES = ['Electronics', 'Apparel', 'Home', 'Grocery', 'Sports', 'Toys', 'Beauty']
BRANDS = [f'Brand{i}' for i in range(1, 501)]

random.seed(42)

def write_suppliers():
    path = os.path.join(OUTDIR, 'suppliers.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['supplier_id', 'name', 'contact_info'])
        for i in range(NUM_SUPPLIERS):
            sid = str(uuid.uuid4())
            name = fake.company()
            contact = {"phone": fake.phone_number(), "email": fake.company_email(), "address": fake.address()}
            w.writerow([sid, name, str(contact)])
    print('wrote', path)

def write_products():
    path = os.path.join(OUTDIR, 'products.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['product_id','external_id','name','category','subcategory','brand','supplier_id','cost','selling_price'])
        for i in range(NUM_PRODUCTS):
            pid = str(uuid.uuid4())
            external = f'P{1000000+i}'
            category = random.choice(CATEGORIES)
            subcategory = category + ' - ' + fake.word()
            brand = random.choice(BRANDS)
            supplier_idx = random.randint(0, NUM_SUPPLIERS-1)
            supplier_id = None
            # supplier id placeholder - will assign after suppliers file written
            cost = round(random.uniform(50, 5000), 2)
            markup = random.uniform(1.05, 2.5)
            selling = round(cost * markup, 2)
            w.writerow([pid, external, fake.sentence(nb_words=3), category, subcategory, brand, f'supplier_{supplier_idx}', cost, selling])
    print('wrote', path)

def write_customers():
    path = os.path.join(OUTDIR, 'customers.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['customer_id','external_id','gender','age_group','membership_tier','customer_type','created_at'])
        age_groups = ['18-24','25-34','35-44','45-54','55-64','65+']
        tiers = ['Standard','Silver','Gold','Platinum']
        types = ['Retail','Wholesale']
        for i in range(NUM_CUSTOMERS):
            cid = str(uuid.uuid4())
            external = f'C{1000000+i}'
            gender = random.choice(['M','F','O'])
            age = random.choice(age_groups)
            tier = random.choices(tiers, weights=[60,25,10,5])[0]
            ctype = random.choices(types, weights=[95,5])[0]
            created = START_DATE + timedelta(days=random.randint(0, 365*10))
            w.writerow([cid, external, gender, age, tier, ctype, created.isoformat()])
    print('wrote', path)

def write_warehouses():
    path = os.path.join(OUTDIR, 'warehouses.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['warehouse_id','name','city','region'])
        for i in range(NUM_WAREHOUSES):
            wid = str(uuid.uuid4())
            name = f'WH-{i+1}'
            city = fake.city()
            region = fake.state()
            w.writerow([wid, name, city, region])
    print('wrote', path)

def write_stores():
    path = os.path.join(OUTDIR, 'stores.csv')
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['store_id','name','city','state','region'])
        for i in range(NUM_STORES):
            sid = str(uuid.uuid4())
            name = f'Store-{i+1}'
            city = fake.city()
            state = fake.state()
            region = fake.country()
            w.writerow([sid, name, city, state, region])
    print('wrote', path)


def stream_orders_and_items():
    orders_path = os.path.join(OUTDIR, 'orders.csv')
    items_path = os.path.join(OUTDIR, 'order_items.csv')
    with open(orders_path, 'w', newline='', encoding='utf-8') as fo, open(items_path, 'w', newline='', encoding='utf-8') as fi:
        wo = csv.writer(fo)
        wi = csv.writer(fi)
        wo.writerow(['order_id','transaction_id','invoice_id','customer_id','store','warehouse_id','employee_id','region','state','city','payment_method','discount','tax','cost','selling_price','profit','quantity','order_status','order_timestamp'])
        wi.writerow(['item_id','order_id','product_id','quantity','unit_price','total_price'])
        for i in range(NUM_ORDERS):
            oid = str(uuid.uuid4())
            tx = f'TX{1000000+i}'
            invoice = f'INV{1000000+i}'
            customer_idx = random.randint(0, NUM_CUSTOMERS-1)
            customer_id = f'customer_{customer_idx}'
            store_idx = random.randint(0, NUM_STORES-1)
            store = f'Store-{store_idx+1}'
            warehouse_idx = random.randint(0, NUM_WAREHOUSES-1)
            warehouse_id = f'warehouse_{warehouse_idx}'
            employee_id = f'employee_{random.randint(1,5000)}'
            region = fake.state()
            state = fake.state()
            city = fake.city()
            payment = random.choice(['Card','UPI','NetBanking','Wallet','COD'])
            qty = random.randint(1,5)
            product_idx = random.randint(0, NUM_PRODUCTS-1)
            product_id = f'product_{product_idx}'
            unit_price = round(random.uniform(100, 20000), 2)
            total_price = round(unit_price * qty, 2)
            cost = round(unit_price * random.uniform(0.6, 0.95), 2)
            profit = round(total_price - cost*qty, 2)
            discount = round(total_price * random.choice([0,0.05,0.1,0.15]), 2)
            tax = round(total_price * 0.18, 2)
            status = random.choices(['Completed','Returned','Cancelled'], weights=[0.95,0.03,0.02])[0]
            order_ts = START_DATE + timedelta(days=random.randint(0, 365*10), seconds=random.randint(0, 86400))
            wo.writerow([oid, tx, invoice, customer_id, store, warehouse_id, employee_id, region, state, city, payment, discount, tax, cost, unit_price, profit, qty, status, order_ts.isoformat()])
            # Write 1-3 items per order
            num_items = random.choices([1,1,1,2,3], weights=[60,20,10,7,3])[0]
            for _ in range(num_items):
                item_id = str(uuid.uuid4())
                pid = f'product_{random.randint(0, NUM_PRODUCTS-1)}'
                q = random.randint(1,3)
                up = round(random.uniform(50, 20000), 2)
                tp = round(up * q, 2)
                wi.writerow([item_id, oid, pid, q, up, tp])
            if (i+1) % 10000 == 0:
                print('generated orders', i+1)
    print('wrote', orders_path, items_path)


if __name__ == '__main__':
    write_suppliers()
    write_products()
    write_customers()
    write_warehouses()
    write_stores()
    stream_orders_and_items()
    print('All files generated in', OUTDIR)
