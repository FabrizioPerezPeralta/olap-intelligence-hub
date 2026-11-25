"""
Script para publicar automáticamente el artículo en Dev.to utilizando su API oficial (Forem API).
Permite publicar como borrador (draft) para revisión o publicarlo directamente en vivo.
"""

import os
import sys
import json
import argparse
from pathlib import Path
import urllib.request
import urllib.error
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
DEFAULT_ARTICLE_PATH = ROOT_DIR / "ARTICLE_FABRIZIO.md"


def publish_to_devto(api_key: str, article_path: Path, published: bool = False):
    if not article_path.exists():
        print(f"[-] Error: No se encontró el archivo del artículo en {article_path}")
        sys.exit(1)

    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extraer título de la primera línea con '# '
    lines = content.splitlines()
    title = "Solución OLAP Serverless con DuckDB, MotherDuck y Streamlit"
    body_lines = []
    title_found = False

    for line in lines:
        if line.startswith("# ") and not title_found:
            title = line.replace("# ", "").strip()
            title_found = True
        else:
            body_lines.append(line)

    body_markdown = "\n".join(body_lines).strip()

    # Dev.to permite un máximo de 4 tags (solo alfanuméricos en minúsculas)
    tags = ["businessintelligence", "duckdb", "python", "dataengineering"]

    payload = {
        "article": {
            "title": title,
            "published": published,
            "body_markdown": body_markdown,
            "tags": tags,
            "series": "Online Analytical Processing (OLAP)"
        }
    }

    url = "https://dev.to/api/articles"
    headers = {
        "api-key": api_key.strip(),
        "Content-Type": "application/json",
        "User-Agent": "Antigravity-OLAP-Publisher/1.0"
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="POST")

    status_label = "PÚBLICO" if published else "BORRADOR (DRAFT)"
    print(f"[*] Enviando artículo a Dev.to ({status_label})...")
    print(f"    Título: {title}")
    print(f"    Tags: {', '.join(tags)}")

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            article_url = res_data.get("url")
            print("\n[+] ¡Artículo publicado exitosamente en Dev.to!")
            print(f"    ID: {res_data.get('id')}")
            print(f"    Estado: {'Publicado en vivo' if published else 'Guardado como borrador'}")
            print(f"    Enlace directo: {article_url}")
            if not published:
                print(f"    Para editar y publicarlo desde la web: https://dev.to/dashboard")
            return res_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"\n[-] Error al publicar en Dev.to (Código HTTP {e.code}):")
        print(f"    Detalle: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Error de conexión: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Publicador de artículos en Dev.to vía API")
    parser.add_argument("--key", type=str, help="API Key de Dev.to (o configúralo en .env como DEVTO_API_KEY)")
    parser.add_argument("--file", type=str, default=str(DEFAULT_ARTICLE_PATH), help="Ruta al archivo Markdown")
    parser.add_argument("--publish", action="store_true", help="Publicar inmediatamente en vivo (por defecto crea borrador)")

    args = parser.parse_args()

    api_key = args.key or os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("[-] Error: No se proporcionó la API Key de Dev.to.")
        print("    Puedes pasarla con --key <TU_API_KEY> o definir DEVTO_API_KEY=tu_clave en el archivo .env.")
        print("    Para obtener tu API Key en Dev.to:")
        print("    1. Ingresa a https://dev.to/settings/extensions")
        print("    2. En 'DEV Community API Keys', genera una nueva clave.")
        sys.exit(1)

    publish_to_devto(
        api_key=api_key,
        article_path=Path(args.file),
        published=args.publish
    )


if __name__ == "__main__":
    main()
