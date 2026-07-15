"""Run DDL from database/schema.sql to create schema.
Usage: python database/migrate.py --dsn postgresql://user:pass@host:5432/dbname
"""
import argparse
import psycopg2
import os

SCRIPT = os.path.join(os.path.dirname(__file__), 'schema.sql')


def run(sql_path: str, dsn: str):
    with open(sql_path, 'r', encoding='utf-8') as f:
        sql = f.read()
    conn = psycopg2.connect(dsn)
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    conn.close()
    print('migrated schema from', sql_path)

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--dsn', required=True)
    args = p.parse_args()
    run(SCRIPT, args.dsn)
