"""
Generador de datos sintéticos analíticos en formato Parquet usando DuckDB.
Genera 150,000 registros de transacciones con esquema de estrella analítico.
"""

import os
from pathlib import Path
import duckdb

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PARQUET_FILE = DATA_DIR / "sample_ecommerce.parquet"
LOCAL_DB_FILE = DATA_DIR / "ecommerce_olap.duckdb"


def generate_dataset(num_records: int = 150_000, motherduck_token: str = None):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[*] Generando {num_records:,} registros analíticos con DuckDB...")

    con = duckdb.connect()

    # Consulta SQL vectorizada de alta velocidad para generar dataset realista
    sql = f"""
    WITH raw_data AS (
        SELECT
            range AS order_id,
            'CUST-' || LPAD((range % 5000 + 1)::VARCHAR, 5, '0') AS customer_id,
            DATE '2023-01-01' + INTERVAL ((range % 730)::INTEGER) DAY AS order_date,
            ['North America', 'Europe', 'Latin America', 'Asia-Pacific'][(range % 4) + 1] AS region,
            ['Consumer', 'Corporate', 'Small Business'][(range % 3) + 1] AS customer_segment,
            ['Electronics', 'Furniture', 'Clothing', 'Home & Kitchen', 'Sports'][(range % 5) + 1] AS category,
            ['Credit Card', 'PayPal', 'Wire Transfer', 'Cryptocurrency'][(range % 4) + 1] AS payment_method,
            ['Standard', 'Express', 'Same Day', 'Economy'][(range % 4) + 1] AS shipping_mode,
            ['Delivered', 'Delivered', 'Delivered', 'Shipped', 'Returned', 'Cancelled'][(range % 6) + 1] AS order_status,
            ROUND(10 + (range % 800) * 1.35, 2) AS unit_price,
            (range % 5 + 1) AS quantity,
            ROUND((range % 4) * 0.05, 2) AS discount_rate,
            ROUND(5 + (range % 25) * 1.1, 2) AS shipping_cost
        FROM range(1, {num_records + 1})
    ),
    enriched AS (
        SELECT
            order_id,
            customer_id,
            order_date,
            EXTRACT(YEAR FROM order_date) AS order_year,
            EXTRACT(QUARTER FROM order_date) AS order_quarter,
            EXTRACT(MONTH FROM order_date) AS order_month,
            STRFTIME(order_date, '%Y-%m') AS year_month,
            STRFTIME(order_date, '%A') AS day_of_week,
            region,
            CASE region
                WHEN 'North America' THEN ['United States', 'Canada', 'Mexico'][(order_id % 3) + 1]
                WHEN 'Europe' THEN ['Germany', 'United Kingdom', 'France', 'Spain'][(order_id % 4) + 1]
                WHEN 'Latin America' THEN ['Peru', 'Colombia', 'Chile', 'Brazil', 'Argentina'][(order_id % 5) + 1]
                ELSE ['Japan', 'South Korea', 'Australia', 'Singapore'][(order_id % 4) + 1]
            END AS country,
            customer_segment,
            category,
            CASE category
                WHEN 'Electronics' THEN ['Laptops', 'Smartphones', 'Headphones', 'Smart TVs'][(order_id % 4) + 1]
                WHEN 'Furniture' THEN ['Office Chairs', 'Desks', 'Bookshelves', 'Sofas'][(order_id % 4) + 1]
                WHEN 'Clothing' THEN ['T-Shirts', 'Jeans', 'Jackets', 'Sneakers'][(order_id % 4) + 1]
                WHEN 'Home & Kitchen' THEN ['Blenders', 'Coffee Makers', 'Cookware', 'Microwaves'][(order_id % 4) + 1]
                ELSE ['Fitness Trackers', 'Bicycles', 'Yoga Mats', 'Weights'][(order_id % 4) + 1]
            END AS sub_category,
            payment_method,
            shipping_mode,
            order_status,
            unit_price,
            quantity,
            discount_rate,
            shipping_cost,
            ROUND((unit_price * quantity) * (1 - discount_rate), 2) AS gross_sales,
            ROUND(((unit_price * quantity) * (1 - discount_rate)) * (0.18 + (order_id % 12) * 0.02) - shipping_cost, 2) AS net_profit
        FROM raw_data
    )
    SELECT * FROM enriched
    """

    # Guardar en archivo Parquet optimizado
    parquet_path_str = str(PARQUET_FILE).replace('\\', '/')
    con.execute(f"COPY ({sql}) TO '{parquet_path_str}' (FORMAT PARQUET, COMPRESSION ZSTD);")
    print(f"[+] Archivo Parquet creado exitosamente en: {PARQUET_FILE}")

    # Guardar también en base de datos local DuckDB
    local_db_str = str(LOCAL_DB_FILE).replace('\\', '/')
    con_local = duckdb.connect(local_db_str)
    con_local.execute(f"CREATE OR REPLACE TABLE sales_fact AS SELECT * FROM read_parquet('{parquet_path_str}');")
    count = con_local.execute("SELECT count(*) FROM sales_fact").fetchone()[0]
    print(f"[+] Base de datos local DuckDB inicializada con {count:,} filas en: {LOCAL_DB_FILE}")
    con_local.close()

    # Si hay token de MotherDuck configurado, subir a la nube
    token = motherduck_token or os.environ.get("MOTHERDUCK_TOKEN")
    if token:
        print("[*] Sincronizando datos con MotherDuck en la nube pública...")
        try:
            md_con = duckdb.connect(f"md:ecommerce_olap?motherduck_token={token}")
            md_con.execute(f"CREATE OR REPLACE TABLE sales_fact AS SELECT * FROM read_parquet('{parquet_path_str}');")
            cloud_count = md_con.execute("SELECT count(*) FROM sales_fact").fetchone()[0]
            print(f"[+] Sincronización exitosa con MotherDuck Cloud: {cloud_count:,} filas cargadas.")
            md_con.close()
        except Exception as e:
            print(f"[-] Nota: No se pudo conectar a MotherDuck ({e}). Se mantendrán los datos locales.")


if __name__ == "__main__":
    generate_dataset()
