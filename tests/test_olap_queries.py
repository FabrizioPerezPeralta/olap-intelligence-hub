"""
Tests unitarios y de integración para validar el motor analítico OLAP (DuckDB).
"""

import sys
from pathlib import Path
import pytest
import duckdb

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from scripts.generate_sample_data import generate_dataset, PARQUET_FILE
from src.database import (
    execute_olap_kpis,
    execute_time_series_olap,
    execute_dimensional_breakdown,
    execute_pivot_olap,
    build_where_clause
)


@pytest.fixture(scope="session")
def setup_test_data():
    """Genera dataset de prueba si no existe."""
    if not PARQUET_FILE.exists():
        generate_dataset(num_records=10_000)
    con = duckdb.connect()
    parquet_str = str(PARQUET_FILE).replace('\\', '/')
    con.execute(f"CREATE VIEW IF NOT EXISTS sales_fact AS SELECT * FROM read_parquet('{parquet_str}');")
    yield con
    con.close()


def test_dataset_generation_and_schema(setup_test_data):
    con = setup_test_data
    count = con.execute("SELECT COUNT(*) FROM sales_fact").fetchone()[0]
    assert count > 0, "La tabla sales_fact no debe estar vacía."

    columns = [col[0] for col in con.execute("DESCRIBE sales_fact").fetchall()]
    expected_cols = [
        "order_id", "customer_id", "order_date", "region", "country",
        "customer_segment", "category", "sub_category", "payment_method",
        "gross_sales", "net_profit"
    ]
    for col in expected_cols:
        assert col in columns, f"Falta la columna dimensional/métrica esperada: {col}"


def test_olap_kpis(setup_test_data):
    con = setup_test_data
    filters = {}
    kpis = execute_olap_kpis(con, filters)

    assert kpis["total_orders"] > 0
    assert kpis["total_sales"] > 0
    assert kpis["unique_customers"] > 0
    assert kpis["aov"] > 0
    assert -100 <= kpis["profit_margin"] <= 100


def test_time_series_window_functions(setup_test_data):
    con = setup_test_data
    filters = {}
    df_monthly = execute_time_series_olap(con, filters, granularity="Mensual")

    assert not df_monthly.empty
    assert "running_total_sales" in df_monthly.columns
    assert "mom_growth_pct" in df_monthly.columns

    # Verificar que el running total sea monótonamente creciente
    running_totals = df_monthly["running_total_sales"].tolist()
    assert running_totals[-1] >= running_totals[0]


def test_dimensional_breakdown_slice_and_dice(setup_test_data):
    con = setup_test_data
    filters = {"regions": ["North America", "Europe"]}
    df_dim = execute_dimensional_breakdown(con, filters, dimension="category")

    assert not df_dim.empty
    assert "total_sales" in df_dim.columns
    assert "profit_margin_pct" in df_dim.columns


def test_pivot_olap_syntax(setup_test_data):
    con = setup_test_data
    filters = {}
    df_pivot = execute_pivot_olap(con, filters, row_dim="region", col_dim="customer_segment")

    assert not df_pivot.empty
    assert "region" in df_pivot.columns


def test_where_clause_builder():
    filters = {
        "regions": ["Europe", "Latin America"],
        "categories": ["Electronics"],
        "date_range": ("2023-01-01", "2023-12-31")
    }
    clause = build_where_clause(filters)
    assert "region IN ('Europe', 'Latin America')" in clause
    assert "category IN ('Electronics')" in clause
    assert "order_date BETWEEN '2023-01-01' AND '2023-12-31'" in clause
