import sqlite3
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

db_path = "backend/app/app_data.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()
tables = [r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
print("Tables:", tables)

for t in tables:
    count = c.execute(f"SELECT count(*) FROM {t}").fetchone()[0]
    print(f"Table {t}: {count} rows")
    if count > 0:
        rows = c.execute(f"SELECT * FROM {t} LIMIT 5").fetchall()
        col_names = [d[0] for d in c.description]
        print(f"  Columns: {col_names}")
        for r in rows:
            print(f"  {r}")

conn.close()
