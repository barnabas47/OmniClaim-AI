import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "omniclaim.db")

def fix_database_dates():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    rows = cursor.execute("SELECT id, flight_number, carrier FROM eligible_flights ORDER BY id ASC").fetchall()
    
    dates = ["2026-08-30", "2026-09-01", "2026-09-02", "2026-09-03", "2026-09-04", "2026-09-05", "2026-09-06"]
    
    for idx, r in enumerate(rows):
        row_id = r[0]
        assigned_date = dates[idx % len(dates)]
        cursor.execute("UPDATE eligible_flights SET flight_date = ? WHERE id = ?", (assigned_date, row_id))
        
    conn.commit()
    
    print("--- HISTORICAL FLIGHT DATES IN OMNICLAIM DB ---")
    distinct_dates = cursor.execute("SELECT flight_date, COUNT(*) FROM eligible_flights GROUP BY flight_date ORDER BY flight_date ASC").fetchall()
    for d, count in distinct_dates:
        print(f"Date {d}: {count} flights")
        
    conn.close()

if __name__ == "__main__":
    fix_database_dates()
