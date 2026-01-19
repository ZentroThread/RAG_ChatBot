import mysql.connector
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def load_mysql_data():
    conn = mysql.connector.connect(
        host = os.getenv("MYSQL_HOST"),
        port = os.getenv("MYSQL_PORT"),
        user = os.getenv("MYSQL_USER"),
        password = os.getenv("MYSQL_PASSWORD"),
        database = os.getenv("MYSQL_DATABASE"),
    )
    
    # brands = pd.read_sql("SELECT * FROM brands", conn)
    # categories = pd.read_sql("SELECT * FROM categories", conn)
    # clothes = pd.read_sql("SELECT * FROM clothes", conn)
    
    query = """
    SELECT
    c.cloth_id,
    c.cloth_name,
    cat.category_name,
    b.brand_name,
    c.size,
    c.color,
    c.price,
    c.stock_quantity,
    c.created_at
    FROM clothes c
    JOIN categories cat ON c.category_id = cat.category_id
    JOIN brands b ON c.brand_id = b.brand_id;
    """

    df = pd.read_sql(query, conn)
    
    conn.close()
    
    return df