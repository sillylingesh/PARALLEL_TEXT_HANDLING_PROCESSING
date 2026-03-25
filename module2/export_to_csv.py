import sqlite3
import pandas as pd
import os

def export_db_to_csv():
    # Define paths
    script_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(script_dir, "sen.db")
    csv_path = os.path.join(script_dir, "sen_results.csv")

    print(f"Connecting to database: {db_path}")
    
    # Check if DB exists
    if not os.path.exists(db_path):
        print(f"Error: Database file '{db_path}' not found.")
        return False

    try:
        # Connect to SQLite DB
        conn = sqlite3.connect(db_path)
        
        # Read data from the 'results' table into a DataFrame
        print("Reading 'results' table...")
        df = pd.read_sql_query("SELECT * FROM results", conn)
        
        # Close connection
        conn.close()
        
        # Export to CSV
        print(f"Exporting data to CSV: {csv_path}")
        df.to_csv(csv_path, index=False)
        print("Export successful!")
        return True
        
    except Exception as e:
        print(f"An error occurred during export: {e}")
        return False

if __name__ == "__main__":
    export_db_to_csv()
