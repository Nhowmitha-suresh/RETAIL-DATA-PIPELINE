"""Simple CSV import helper for PostgreSQL using psycopg2 COPY.
Usage: python database/import.py --dir ../data --dsn postgresql://user:pass@host:5432/dbname
"""
import argparse
import os
import psycopg2


def do_copy(conn, table, csv_path, columns=None):
    cur = conn.cursor()
    with open(csv_path, 'r', encoding='utf-8') as f:
        if columns:
            cols = ','.join(columns)
            sql = f"COPY {table} ({cols}) FROM STDIN WITH CSV HEADER"
        else:
            sql = f"COPY {table} FROM STDIN WITH CSV HEADER"
        cur.copy_expert(sql, f)
        conn.commit()
        print('imported', csv_path, '->', table)


def main(data_dir, dsn):
    conn = psycopg2.connect(dsn)
    files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
    # Order matters for FK constraints
    order = ['suppliers.csv','products.csv','customers.csv','warehouses.csv','stores.csv','orders.csv','order_items.csv']
    for fname in order:
        if fname in files:
            table = fname.replace('.csv','')
            csv_path = os.path.join(data_dir, fname)
            do_copy(conn, table, csv_path)
    conn.close()

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dir', dest='data_dir', default='../data')
    p.add_argument('--dsn', dest='dsn', required=True)
    args = p.parse_args()
    main(args.data_dir, args.dsn)
