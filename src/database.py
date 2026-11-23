"""
Módulo de gestión de conexión y consultas analíticas OLAP con DuckDB y MotherDuck.
Soporta ejecución híbrida: Local DuckDB / Parquet o Cloud MotherDuck SaaS.
"""

import os
import datetime
from pathlib import Path
from typing import Optional, Tuple, Dict, Any
import duckdb
import pandas as pd
import streamlit as st

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PARQUET_FILE = DATA_DIR / "sample_ecommerce.parquet"
LOCAL_DB_FILE = DATA_DIR / "ecommerce_olap.duckdb"


def get_motherduck_token() -> Optional[str]:
    """Obtiene el token de MotherDuck desde streamlit secrets o variables de entorno."""
    token = None
    if hasattr(st, "secrets") and "MOTHERDUCK_TOKEN" in st.secrets:
        token = st.secrets["MOTHERDUCK_TOKEN"]
    if not token:
        token = os.environ.get("MOTHERDUCK_TOKEN")
    return token.strip() if token else None


@st.cache_resource
def get_olap_connection():
    """
    Establece conexión con MotherDuck (SaaS) o DuckDB Local.
    Retorna (connection, mode_name, db_type).
    """
    token = get_motherduck_token()
    
    if token:
        try:
            con = duckdb.connect(f"md:ecommerce_olap?motherduck_token={token}")
            # Verificar si existe la tabla sales_fact
            tables = con.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            if "sales_fact" not in table_names:
                # Si no está creada en la nube, inicializarla desde el parquet local
                if PARQUET_FILE.exists():
                    parquet_str = str(PARQUET_FILE).replace('\\', '/')
                    con.execute(f"CREATE TABLE IF NOT EXISTS sales_fact AS SELECT * FROM read_parquet('{parquet_str}');")
            return con, "MotherDuck Cloud (SaaS)", "cloud"
        except Exception as e:
            st.warning(f"No se pudo conectar a MotherDuck ({e}). Conectando a DuckDB Local.")

    # Modo Local: usar base de datos local o consultar Parquet directamente en memoria
    con = duckdb.connect()
    parquet_str = str(PARQUET_FILE).replace('\\', '/')
    if PARQUET_FILE.exists():
        con.execute(f"CREATE VIEW IF NOT EXISTS sales_fact AS SELECT * FROM read_parquet('{parquet_str}');")
    elif LOCAL_DB_FILE.exists():
        local_db_str = str(LOCAL_DB_FILE).replace('\\', '/')
        con = duckdb.connect(local_db_str, read_only=True)
    else:
        # Si aún no existe el archivo, generar el dataset
        from scripts.generate_sample_data import generate_dataset
        generate_dataset()
        con.execute(f"CREATE VIEW IF NOT EXISTS sales_fact AS SELECT * FROM read_parquet('{parquet_str}');")

    return con, "DuckDB Local (Engine Vectorizado)", "local"


def execute_olap_kpis(con, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula los KPIs ejecutivos OLAP con vectorización y filtros dinámicos.
    """
    where_clause = build_where_clause(filters)
    query = f"""
    SELECT
        COUNT(order_id) AS total_orders,
        COUNT(DISTINCT customer_id) AS unique_customers,
        COALESCE(SUM(gross_sales), 0) AS total_sales,
        COALESCE(SUM(net_profit), 0) AS total_profit,
        COALESCE(AVG(gross_sales), 0) AS aov,
        COALESCE(SUM(net_profit) / NULLIF(SUM(gross_sales), 0) * 100, 0) AS profit_margin,
        COALESCE(AVG(discount_rate) * 100, 0) AS avg_discount
    FROM sales_fact
    WHERE {where_clause}
    """
    cursor = con.cursor()
    row = cursor.execute(query).fetchone()
    if not row or row[0] is None:
        return {
            "total_orders": 0,
            "unique_customers": 0,
            "total_sales": 0.0,
            "total_profit": 0.0,
            "aov": 0.0,
            "profit_margin": 0.0,
            "avg_discount": 0.0,
        }
    return {
        "total_orders": row[0] or 0,
        "unique_customers": row[1] or 0,
        "total_sales": float(row[2] or 0),
        "total_profit": float(row[3] or 0),
        "aov": float(row[4] or 0),
        "profit_margin": float(row[5] or 0),
        "avg_discount": float(row[6] or 0),
    }


def execute_time_series_olap(con, filters: Dict[str, Any], granularity: str = "year_month") -> pd.DataFrame:
    """
    Operación OLAP: Roll-up / Drill-down en dimensión tiempo.
    Calcula ventas, margen de ganancia y crecimiento acumulativo usando Window Functions.
    """
    where_clause = build_where_clause(filters)
    
    time_column = {
        "Mensual": "year_month",
        "Trimestral": "order_year || '-Q' || order_quarter",
        "Anual": "order_year::VARCHAR",
        "Día de la semana": "day_of_week"
    }.get(granularity, "year_month")

    query = f"""
    WITH aggregated AS (
        SELECT
            {time_column} AS time_period,
            SUM(gross_sales) AS period_sales,
            SUM(net_profit) AS period_profit,
            COUNT(order_id) AS order_volume
        FROM sales_fact
        WHERE {where_clause}
        GROUP BY 1
    )
    SELECT
        time_period,
        period_sales,
        period_profit,
        order_volume,
        -- Window function OLAP: Ventas acumuladas en el tiempo
        SUM(period_sales) OVER (ORDER BY time_period) AS running_total_sales,
        -- Window function OLAP: Crecimiento respecto al periodo anterior
        ROUND(
            (period_sales - LAG(period_sales, 1) OVER (ORDER BY time_period)) 
            / NULLIF(LAG(period_sales, 1) OVER (ORDER BY time_period), 0) * 100, 2
        ) AS mom_growth_pct
    FROM aggregated
    ORDER BY time_period;
    """
    cursor = con.cursor()
    return cursor.execute(query).df()


def execute_dimensional_breakdown(con, filters: Dict[str, Any], dimension: str) -> pd.DataFrame:
    """
    Operación OLAP: Slice & Dice sobre una dimensión analítica con métricas agregadas.
    """
    where_clause = build_where_clause(filters)
    query = f"""
    SELECT
        {dimension} AS dimension_value,
        COUNT(order_id) AS orders,
        ROUND(SUM(gross_sales), 2) AS total_sales,
        ROUND(SUM(net_profit), 2) AS total_profit,
        ROUND(AVG(gross_sales), 2) AS avg_ticket,
        ROUND(SUM(net_profit) / NULLIF(SUM(gross_sales), 0) * 100, 2) AS profit_margin_pct
    FROM sales_fact
    WHERE {where_clause}
    GROUP BY 1
    ORDER BY total_sales DESC;
    """
    cursor = con.cursor()
    return cursor.execute(query).df()


def execute_pivot_olap(con, filters: Dict[str, Any], row_dim: str, col_dim: str) -> pd.DataFrame:
    """
    Operación OLAP: Tabla dinámica (Pivot) usando la sintaxis PIVOT nativa de DuckDB.
    """
    where_clause = build_where_clause(filters)
    query = f"""
    PIVOT (
        SELECT {row_dim}, {col_dim}, gross_sales 
        FROM sales_fact 
        WHERE {where_clause}
    )
    ON {col_dim}
    USING ROUND(SUM(gross_sales), 2)
    GROUP BY {row_dim};
    """
    cursor = con.cursor()
    return cursor.execute(query).df()


def get_filter_options(con) -> Dict[str, Any]:
    """Obtiene los valores únicos para los selectores de filtro."""
    cursor = con.cursor()
    regions = [r[0] for r in cursor.execute("SELECT DISTINCT region FROM sales_fact ORDER BY 1").fetchall()]
    categories = [r[0] for r in cursor.execute("SELECT DISTINCT category FROM sales_fact ORDER BY 1").fetchall()]
    segments = [r[0] for r in cursor.execute("SELECT DISTINCT customer_segment FROM sales_fact ORDER BY 1").fetchall()]
    payment_methods = [r[0] for r in cursor.execute("SELECT DISTINCT payment_method FROM sales_fact ORDER BY 1").fetchall()]
    date_row = cursor.execute("SELECT MIN(order_date), MAX(order_date) FROM sales_fact").fetchone()
    
    min_date = date_row[0] if date_row and date_row[0] else datetime.date(2023, 1, 1)
    max_date = date_row[1] if date_row and date_row[1] else datetime.date(2024, 12, 31)
    
    return {
        "regions": regions,
        "categories": categories,
        "segments": segments,
        "payment_methods": payment_methods,
        "min_date": min_date,
        "max_date": max_date,
    }


def build_where_clause(filters: Dict[str, Any]) -> str:
    """Construye cláusula WHERE segura a partir de los filtros seleccionados."""
    clauses = ["1=1"]
    
    if filters.get("regions"):
        formatted = ", ".join(f"'{r}'" for r in filters["regions"])
        clauses.append(f"region IN ({formatted})")
        
    if filters.get("categories"):
        formatted = ", ".join(f"'{c}'" for c in filters["categories"])
        clauses.append(f"category IN ({formatted})")
        
    if filters.get("segments"):
        formatted = ", ".join(f"'{s}'" for s in filters["segments"])
        clauses.append(f"customer_segment IN ({formatted})")
        
    if filters.get("payment_methods"):
        formatted = ", ".join(f"'{p}'" for p in filters["payment_methods"])
        clauses.append(f"payment_method IN ({formatted})")
        
    if filters.get("date_range") and len(filters["date_range"]) == 2:
        start_date, end_date = filters["date_range"]
        clauses.append(f"order_date BETWEEN '{start_date}' AND '{end_date}'")
        
    return " AND ".join(clauses)
