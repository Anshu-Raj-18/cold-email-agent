import sqlite3
from src.database import get_connection, export_applications_csv

def reset_applications_to_pending():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE applications SET status = 'Email Drafted', sent_at = NULL, approved_at = NULL")
    count = cursor.rowcount
    conn.commit()
    conn.close()
    
    csv_path = export_applications_csv()
    print("=" * 65)
    print(f"[SUCCESS] Reset {count} applications back to 'Email Drafted' (Pending).")
    print(f"[SUCCESS] Updated database CSV export at: '{csv_path}'")
    print("=" * 65)

if __name__ == "__main__":
    reset_applications_to_pending()
