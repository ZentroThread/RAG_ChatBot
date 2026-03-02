import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def load_mysql_data():
    # Get password from env
    db_password = os.getenv("AWS_RDS_DB_PASSWORD", "")

    conn = psycopg2.connect(
        host = os.getenv("AWS_RDS_DB_HOST"),
        port = int(os.getenv("AWS_RDS_DB_PORT", 5432)),
        user = os.getenv("AWS_RDS_DB_USER"),
        password = db_password,
        database = os.getenv("AWS_RDS_DB_NAME"),
    )
    
    # brands = pd.read_sql("SELECT * FROM brands", conn)
    # categories = pd.read_sql("SELECT * FROM categories", conn)
    # clothes = pd.read_sql("SELECT * FROM clothes", conn)
    
    # Query all 11 tables - Update table names according to your actual schema
    # First, let's get the list of all tables
    tables_query = """
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """

    # Get all table names
    tables_df = pd.read_sql(tables_query, conn)
    print(f"Found {len(tables_df)} tables: {tables_df['table_name'].tolist()}")

    # Define sensitive tables that should not be accessed
    EXCLUDED_TABLES = ['tenants', 'refresh_tokens', 'login']

    # Filter out sensitive tables
    allowed_tables = [table for table in tables_df['table_name'] if table not in EXCLUDED_TABLES]
    print(f"Allowed tables after filtering: {allowed_tables}")

    # Fetch data from all tables and combine
    all_data = []
    for table_name in allowed_tables:
        try:
            table_query = f"SELECT * FROM {table_name}"
            temp_df = pd.read_sql(table_query, conn)
            temp_df['source_table'] = table_name  # Add source table column
            all_data.append(temp_df)
            print(f"Loaded {len(temp_df)} records from {table_name}")
        except Exception as e:
            print(f"Error loading {table_name}: {e}")

    # Combine all dataframes
    if all_data:
        df = pd.concat(all_data, ignore_index=True)
    else:
        df = pd.DataFrame()

    conn.close()
    
    return df