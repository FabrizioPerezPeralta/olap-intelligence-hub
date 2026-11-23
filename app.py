"""
OLAP Intelligence Hub: Aplicación Analítica Empresarial
Desarrollada con Streamlit, DuckDB y MotherDuck (Cloud SaaS).
"""

import sys
from pathlib import Path
import time
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

# Añadir directorio raíz al path para importar módulos internos
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.append(str(ROOT_DIR))

from src.database import (
    get_olap_connection,
    get_filter_options,
    execute_olap_kpis,
    execute_time_series_olap,
    execute_dimensional_breakdown,
    execute_pivot_olap,
    PARQUET_FILE
)

# Configuración de página
st.set_page_config(
    page_title="OLAP Analytics Hub | DuckDB & MotherDuck",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .metric-card {
        background: #FFFFFF;
        padding: 1.25rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .metric-label {
        font-size: 0.85rem;
        color: #64748B;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        font-size: 1.75rem;
        color: #0F172A;
        font-weight: 700;
        margin-top: 0.35rem;
    }
    .metric-sub {
        font-size: 0.8rem;
        color: #10B981;
        margin-top: 0.25rem;
        font-weight: 500;
    }
    .badge-cloud {
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .badge-local {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def main():
    # Conexión al motor analítico
    con, mode_name, db_type = get_olap_connection()
    filter_opts = get_filter_options(con)

    # Header principal
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.title("⚡ OLAP Intelligence Hub")
        st.caption("Solución Analítica Multidimensional impulsada por **DuckDB** y **MotherDuck Cloud**")
    with col_h2:
        badge_class = "badge-cloud" if db_type == "cloud" else "badge-local"
        st.markdown(f"<div style='text-align: right; margin-top: 1.5rem;'><span class='{badge_class}'>● {mode_name}</span></div>", unsafe_allow_html=True)

    # Barra lateral: Operación de Slice & Dice (Filtros OLAP)
    st.sidebar.header("🔍 Controles de Navegación OLAP")
    st.sidebar.markdown("*Slice & Dice multidimensional*")

    # Filtro de rango de fechas
    min_date = filter_opts["min_date"]
    max_date = filter_opts["max_date"]
    selected_dates = st.sidebar.date_input(
        "Rango Temporal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    # Filtros dimensionales
    selected_regions = st.sidebar.multiselect(
        "Región Geográfica:",
        options=filter_opts["regions"],
        default=filter_opts["regions"]
    )

    selected_categories = st.sidebar.multiselect(
        "Categoría de Producto:",
        options=filter_opts["categories"],
        default=filter_opts["categories"]
    )

    selected_segments = st.sidebar.multiselect(
        "Segmento de Cliente:",
        options=filter_opts["segments"],
        default=filter_opts["segments"]
    )

    selected_payments = st.sidebar.multiselect(
        "Método de Pago:",
        options=filter_opts["payment_methods"],
        default=filter_opts["payment_methods"]
    )

    # Diccionario de filtros
    active_filters = {
        "date_range": selected_dates if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2 else None,
        "regions": selected_regions,
        "categories": selected_categories,
        "segments": selected_segments,
        "payment_methods": selected_payments,
    }

    # Ejecución de KPIs en tiempo récord (Vectorized query)
    start_time = time.time()
    kpis = execute_olap_kpis(con, active_filters)
    query_duration_ms = (time.time() - start_time) * 1000

    # Fila de KPIs Ejecutivos
    kpi_cols = st.columns(5)
    with kpi_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ventas Brutas</div>
            <div class="metric-value">${kpis['total_sales']:,.2f}</div>
            <div class="metric-sub">AOV: ${kpis['aov']:,.2f}</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Ganancia Neta</div>
            <div class="metric-value">${kpis['total_profit']:,.2f}</div>
            <div class="metric-sub">Margen: {kpis['profit_margin']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Volumen de Órdenes</div>
            <div class="metric-value">{kpis['total_orders']:,}</div>
            <div class="metric-sub">Descuento Prom: {kpis['avg_discount']:.1f}%</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_cols[3]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Clientes Únicos</div>
            <div class="metric-value">{kpis['unique_customers']:,}</div>
            <div class="metric-sub">Ratio: {(kpis['total_orders'] / max(kpis['unique_customers'], 1)):.2f} ord/cli</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_cols[4]:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">Latencia de Consulta</div>
            <div class="metric-value">{query_duration_ms:.1f} ms</div>
            <div class="metric-sub">⚡ Vectorized DuckDB</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Pestañas Analíticas OLAP
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Roll-Up & Tendencias Temporales",
        "🧩 Slice & Dice Dimensional",
        "📊 Tabla Dinámica (Pivot OLAP)",
        "💻 Consola SQL Ad-Hoc"
    ])

    # TAB 1: Roll-up y Drill-down temporal
    with tab1:
        st.subheader("Análisis Temporal y Funciones de Ventana (Window Functions)")
        t_col1, t_col2 = st.columns([1, 3])
        with t_col1:
            granularity = st.selectbox(
                "Nivel de Agregación (Roll-Up / Drill-Down):",
                options=["Mensual", "Trimestral", "Anual", "Día de la semana"],
                index=0
            )

        df_time = execute_time_series_olap(con, active_filters, granularity)

        if not df_time.empty:
            # Gráfico interactivo con Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_time['time_period'],
                y=df_time['period_sales'],
                name='Ventas Brutas ($)',
                marker_color='#0284C7'
            ))
            fig.add_trace(go.Scatter(
                x=df_time['time_period'],
                y=df_time['period_profit'],
                name='Ganancia Neta ($)',
                mode='lines+markers',
                line=dict(color='#10B981', width=3),
                yaxis='y2'
            ))

            fig.update_layout(
                title=f"Evolución Analítica ({granularity})",
                xaxis_title="Período",
                yaxis=dict(title="Ventas Brutas ($)"),
                yaxis2=dict(
                    title="Ganancia Neta ($)",
                    overlaying='y',
                    side='right',
                    showgrid=False
                ),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                margin=dict(l=40, r=40, t=50, b=40),
                hovermode="x unified"
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("Ver tabla analítica detallada con Ventas Acumuladas"):
                st.dataframe(
                    df_time.rename(columns={
                        "time_period": "Período",
                        "period_sales": "Ventas ($)",
                        "period_profit": "Ganancia ($)",
                        "order_volume": "N° Órdenes",
                        "running_total_sales": "Ventas Acumuladas ($)",
                        "mom_growth_pct": "Crecimiento vs Período Anterior (%)"
                    }),
                    use_container_width=True
                )
        else:
            st.info("No se encontraron registros para los filtros seleccionados.")

    # TAB 2: Slice & Dice Dimensional
    with tab2:
        st.subheader("Desglose Dimensional Multieje")
        d_col1, d_col2 = st.columns([1, 2])
        with d_col1:
            dim_choice = st.selectbox(
                "Seleccionar Dimensión para Análisis:",
                options=[
                    ("category", "Categoría de Producto"),
                    ("sub_category", "Sub-categoría"),
                    ("region", "Región"),
                    ("country", "País"),
                    ("customer_segment", "Segmento de Cliente"),
                    ("payment_method", "Método de Pago"),
                    ("shipping_mode", "Modo de Envío")
                ],
                format_func=lambda x: x[1]
            )

        df_dim = execute_dimensional_breakdown(con, active_filters, dim_choice[0])

        if not df_dim.empty:
            c1, c2 = st.columns([3, 2])
            with c1:
                fig_bar = px.bar(
                    df_dim,
                    x='dimension_value',
                    y='total_sales',
                    color='profit_margin_pct',
                    color_continuous_scale='Tealgrn',
                    title=f"Ventas y Margen por {dim_choice[1]}",
                    labels={
                        'dimension_value': dim_choice[1],
                        'total_sales': 'Ventas Totales ($)',
                        'profit_margin_pct': 'Margen (%)'
                    }
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            with c2:
                fig_pie = px.pie(
                    df_dim,
                    names='dimension_value',
                    values='total_sales',
                    title=f"Distribución Porcentual ({dim_choice[1]})",
                    hole=0.45
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            st.dataframe(
                df_dim.rename(columns={
                    "dimension_value": dim_choice[1],
                    "orders": "Órdenes",
                    "total_sales": "Ventas ($)",
                    "total_profit": "Ganancia ($)",
                    "avg_ticket": "Ticket Promedio ($)",
                    "profit_margin_pct": "Margen (%)"
                }),
                use_container_width=True
            )

    # TAB 3: Pivot Table OLAP
    with tab3:
        st.subheader("Operación PIVOT de DuckDB (Matriz Cruzada)")
        st.markdown("Aprovecha la sentencia nativa `PIVOT` de DuckDB para cruzar dimensiones con máxima eficiencia.")
        
        p_col1, p_col2 = st.columns(2)
        with p_col1:
            row_dim = st.selectbox("Dimensión en Filas:", ["region", "category", "customer_segment"], index=0)
        with p_col2:
            col_dim = st.selectbox("Dimensión en Columnas:", ["customer_segment", "payment_method", "category"], index=1)

        if row_dim != col_dim:
            df_pivot = execute_pivot_olap(con, active_filters, row_dim, col_dim)
            st.dataframe(df_pivot, use_container_width=True)
            
            # Heatmap visual
            pivot_matrix = df_pivot.set_index(row_dim)
            fig_heat = px.imshow(
                pivot_matrix,
                labels=dict(x=col_dim, y=row_dim, color="Ventas ($)"),
                x=pivot_matrix.columns,
                y=pivot_matrix.index,
                color_continuous_scale="Blues",
                title=f"Mapa de Calor: {row_dim} vs {col_dim}"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("Selecciona dos dimensiones distintas para el eje de filas y columnas.")

    # TAB 4: Consola SQL Ad-Hoc
    with tab4:
        st.subheader("Explorador SQL OLAP Interactivo")
        st.markdown("Ejecuta consultas analíticas personalizadas sobre la tabla `sales_fact` utilizando la potencia de DuckDB.")

        default_query = """SELECT 
    region, 
    category, 
    COUNT(*) AS total_tx,
    ROUND(SUM(gross_sales), 2) AS total_sales,
    ROUND(AVG(gross_sales), 2) AS aov,
    ROUND(SUM(net_profit), 2) AS profit
FROM sales_fact
GROUP BY CUBE (region, category)
ORDER BY total_sales DESC
LIMIT 20;"""

        user_query = st.text_area("Consulta SQL:", value=default_query, height=180)
        
        if st.button("▶ Ejecutar Consulta"):
            try:
                start_q = time.time()
                res_df = con.execute(user_query).df()
                elapsed = (time.time() - start_q) * 1000
                st.success(f"Consulta completada en **{elapsed:.2f} ms** ({len(res_df)} registros devueltos).")
                st.dataframe(res_df, use_container_width=True)
            except Exception as e:
                st.error(f"Error al ejecutar la consulta SQL: {e}")

    # Footer
    st.divider()
    st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 0.85rem;">
        Proyecto de Inteligencia de Negocios — Solución OLAP Serverless con DuckDB & MotherDuck (Sin AWS).<br>
        Repositorio público con CI/CD automatizado en GitHub Actions y despliegue en la Nube Pública.
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
