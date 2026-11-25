import zlib
import base64
import urllib.request
from pathlib import Path

diagram = """graph TD
    classDef layerBox fill:#ffffff,stroke:#0284c7,stroke-width:2px,color:#0f172a,rx:8px,ry:8px;
    classDef nodeStyle fill:#f8fafc,stroke:#cbd5e1,stroke-width:1.5px,color:#1e293b,rx:6px,ry:6px;

    subgraph Data["1. Data Storage Layer"]
        A[("Apache Parquet (150K+ Records)<br/>Columnar Analytical Format<br/>ZSTD Compression")]:::nodeStyle
    end

    subgraph Engines["2. Serverless OLAP Engine (Hybrid Dual-Mode)"]
        B["DuckDB Local Engine<br/>Vectorized SIMD Execution<br/>In-Memory Queries in less than 15ms"]:::nodeStyle
        C["MotherDuck Cloud (Public SaaS)<br/>Serverless Data Warehouse<br/>Cloud Persistence & Sync"]:::nodeStyle
    end

    subgraph UI["3. Analytical & UI Layer (Streamlit)"]
        D["OLAP Intelligence Hub UI<br/>Interactive Web Dashboard"]:::nodeStyle
        E["OLAP Operations:<br/>Multidimensional Slice and Dice<br/>Temporal Roll-Up & Drill-Down<br/>PIVOT Matrix and Heatmap<br/>Ad-Hoc SQL Console"]:::nodeStyle
    end

    subgraph DevOps["4. Automation & DataOps (CI/CD)"]
        F["GitHub Repository<br/>main branch"]:::nodeStyle
        G["GitHub Actions Pipeline<br/>Ruff Linting & Pytest Suites<br/>MotherDuck Cloud Sync"]:::nodeStyle
        H["Streamlit Community Cloud<br/>Continuous Public Deployment"]:::nodeStyle
    end

    A --> B
    A --> C
    B --> D
    C --> D
    D --> E
    F --> G
    G --> H
    H -. Live Query .-> C
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
