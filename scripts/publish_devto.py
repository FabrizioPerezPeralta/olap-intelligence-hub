"""
Script para publicar automáticamente el artículo en Dev.to utilizando su API oficial (Forem API).
Permite publicar como borrador (draft) para revisión o publicarlo directamente en vivo.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Optional
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


def get_latest_article_id(api_key: str) -> Optional[int]:
    """Obtiene el ID del artículo más reciente publicado por el usuario en Dev.to."""
    url = "https://dev.to/api/articles/me/all"
    headers = {
        "api-key": api_key.strip(),
        "User-Agent": "Antigravity-OLAP-Publisher/1.0"
    }
    req = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(req) as resp:
            articles = json.loads(resp.read().decode("utf-8"))
            if articles:
                return articles[0]["id"]
    except Exception as e:
        print(f"[-] No se pudo obtener la lista de artículos: {e}")
    return None


def update_devto_article(api_key: str, article_id: int, article_path: Path):
    if not article_path.exists():
        print(f"[-] Error: No se encontró el archivo del artículo en {article_path}")
        sys.exit(1)

    with open(article_path, "r", encoding="utf-8") as f:
        content = f.read()

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
    tags = ["businessintelligence", "duckdb", "python", "dataengineering"]

    payload = {
        "article": {
            "title": title,
            "body_markdown": body_markdown,
            "tags": tags,
            "series": "Online Analytical Processing (OLAP)"
        }
    }

    url = f"https://dev.to/api/articles/{article_id}"
    headers = {
        "api-key": api_key.strip(),
        "Content-Type": "application/json",
        "User-Agent": "Antigravity-OLAP-Publisher/1.0"
    }

    data_bytes = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data_bytes, headers=headers, method="PUT")

    print(f"[*] Actualizando artículo en Dev.to (ID: {article_id})...")
    print(f"    Título: {title}")

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print("\n[+] ¡Artículo actualizado exitosamente en Dev.to!")
            print(f"    Enlace directo: {res_data.get('url')}")
            return res_data
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        print(f"\n[-] Error al actualizar en Dev.to (Código HTTP {e.code}):")
        print(f"    Detalle: {error_body}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[-] Error de conexión: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Publicador y actualizador de artículos en Dev.to vía API")
    parser.add_argument("--key", type=str, help="API Key de Dev.to (o configúralo en .env como DEVTO_API_KEY)")
    parser.add_argument("--file", type=str, default=str(DEFAULT_ARTICLE_PATH), help="Ruta al archivo Markdown")
    parser.add_argument("--publish", action="store_true", help="Publicar inmediatamente en vivo (por defecto crea borrador)")
    parser.add_argument("--update", type=str, nargs="?", const="latest", help="ID del artículo a actualizar (o 'latest' para el más reciente)")

    args = parser.parse_args()

    api_key = args.key or os.environ.get("DEVTO_API_KEY")
    if not api_key:
        print("[-] Error: No se proporcionó la API Key de Dev.to.")
        print("    Puedes pasarla con --key <TU_API_KEY> o definir DEVTO_API_KEY=tu_clave en el archivo .env.")
        print("    Para obtener tu API Key en Dev.to:")
        print("    1. Ingresa a https://dev.to/settings/extensions")
        print("    2. En 'DEV Community API Keys', genera una nueva clave.")
        sys.exit(1)

    if args.update:
        target_id = args.update
        if target_id == "latest":
            target_id = get_latest_article_id(api_key)
            if not target_id:
                print("[-] Error: No se encontró ningún artículo previo para actualizar.")
                sys.exit(1)
        update_devto_article(
            api_key=api_key,
            article_id=int(target_id),
            article_path=Path(args.file)
        )
    else:
        publish_to_devto(
            api_key=api_key,
            article_path=Path(args.file),
            published=args.publish
        )


if __name__ == "__main__":
    main()
