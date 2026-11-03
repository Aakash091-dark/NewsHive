import psycopg2
import os
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime, date
import json
import pandas as pd

load_dotenv()
# ----------------------------------
# CONFIG
# ----------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

OUTPUT_FILE = "scraping_reports.json"
EXCEL_FILE = "scraping_reports.xlsx"


def convert_value(v):
    """Convert non-JSON-serializable values to JSON safe strings."""
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    return v  # lists & dicts are already JSON serializable


def export_scraping_reports_to_json():
    try:
        print("Connecting to database...")
        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        print("Fetching data from scraping_reports table...")
        cursor.execute("SELECT * FROM scraping_reports;")
        rows = cursor.fetchall()

        if not rows:
            print("No data found.")
            return

        print(f"Fetched {len(rows)} rows.")

        print(f"Writing JSON to {OUTPUT_FILE}...")

        cleaned_rows = []
        for row in rows:
            cleaned_row = {k: convert_value(v) for k, v in row.items()}
            cleaned_rows.append(cleaned_row)

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(cleaned_rows, f, indent=4, ensure_ascii=False)

        print("JSON export completed successfully!")

        # ----------------------------------------------
        # NEW SECTION: Convert JSON → Excel
        # ----------------------------------------------
        print(f"\n📄 Converting JSON to Excel: {EXCEL_FILE}")

        df = pd.DataFrame(cleaned_rows)

        if df.empty:
            print("⚠ JSON has no rows. Creating empty Excel with columns only.")
            df.to_excel(EXCEL_FILE, index=False)
        else:
            df.to_excel(EXCEL_FILE, index=False)

        print("Excel file saved successfully!")

        # ----------------------------------------------
        # Alignment Check
        # ----------------------------------------------
        print("\n🔍 Checking Excel alignment...")

        if df.empty:
            print("ℹ No rows found in Excel.")
            print("✅ Excel is empty but correctly structured.")
        else:
            non_null_counts = df.notna().sum()
            if len(set(non_null_counts)) == 1:
                print("✅ All columns properly aligned.")
            else:
                print("⚠ Misalignment detected:")
                for col, count in non_null_counts.items():
                    print(f"   → {col}: {count} filled values")

            empty_cols = df.columns[df.isna().all()].tolist()
            if empty_cols:
                print(f"⚠ Empty columns found: {empty_cols}")
            else:
                print("✅ No empty columns.")

        print("✔ Alignment check completed.\n")

    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        try:
            cursor.close()
            conn.close()
        except:
            pass


if __name__ == "__main__":
    export_scraping_reports_to_json()
