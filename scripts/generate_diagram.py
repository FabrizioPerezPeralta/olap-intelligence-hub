import zlib
import base64
import urllib.request
from pathlib import Path

diagram = """graph TD
    classDef layerBox fill:#ffffff,stroke:#0284c7,stroke-width:2px,color:#0f172a,rx:8px,ry:8px;
    classDef nodeStyle fill:#f8fafc,stroke:#cbd5e1,stroke-width:1.5px,color:#1e293b,rx:6px,ry:6px;

    subgraph Data["1. Capa de Almacenamiento y Datos"]
        A[("Apache Parquet (150K+ Registros)<br/>Formato Columnar Analitico<br/>Compresion ZSTD")]:::nodeStyle
    end

    subgraph Engines["2. Motor OLAP Serverless (Modo Hibrido Dual)"]
        B["DuckDB Local Engine<br/>Ejecucion Vectorizada SIMD<br/>Consultas en RAM en menos de 15ms"]:::nodeStyle
        C["MotherDuck Cloud (SaaS Publico)<br/>Data Warehouse Serverless<br/>Sincronizacion en la Nube"]:::nodeStyle
    end

    subgraph UI["3. Capa de Aplicacion Analitica (Streamlit)"]
        D["OLAP Intelligence Hub UI<br/>Dashboard Interactivo Web"]:::nodeStyle
        E["Operaciones OLAP:<br/>Slice and Dice Multidimensional<br/>Roll-Up y Drill-Down Temporal<br/>Matriz PIVOT y Heatmap<br/>Consola SQL Ad-Hoc"]:::nodeStyle
    end

    subgraph DevOps["4. Automatizacion y DataOps (CI/CD)"]
        F["Repositorio GitHub<br/>Rama main"]:::nodeStyle
        G["GitHub Actions Pipeline<br/>Calidad de Codigo y Pruebas Pytest<br/>Sincronizacion con MotherDuck"]:::nodeStyle
        H["Streamlit Community Cloud<br/>Despliegue Publico Continuo"]:::nodeStyle
    end

    A --> B
    A --> C
    B --> D
    C --> D
    D --> E
    F --> G
    G --> H
    H -. Consulta en Vivo .-> C
"""

comp = zlib.compress(diagram.encode('utf-8'), 9)
enc = base64.urlsafe_b64encode(comp).decode('ascii')

url_svg = f"https://kroki.io/mermaid/svg/{enc}"
url_png = f"https://kroki.io/mermaid/png/{enc}"

print(f"URL SVG: {url_svg}")
print(f"URL PNG: {url_png}")

# Descargar SVG
req_svg = urllib.request.Request(url_svg, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_svg) as resp:
    svg_data = resp.read()

out_svg = Path(__file__).resolve().parent.parent / "docs" / "architecture.svg"
out_svg.parent.mkdir(parents=True, exist_ok=True)
with open(out_svg, "wb") as f:
    f.write(svg_data)
print(f"[+] SVG guardado: {out_svg} ({len(svg_data)} bytes)")

# Descargar PNG
req_png = urllib.request.Request(url_png, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req_png) as resp:
    png_data = resp.read()

out_png = Path(__file__).resolve().parent.parent / "docs" / "architecture.png"
with open(out_png, "wb") as f:
    f.write(png_data)
print(f"[+] PNG guardado: {out_png} ({len(png_data)} bytes)")
