"""Utilidades compartidas para el Visor Territorial - Ley 27795."""
import json
import unicodedata
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
GEO_DIR = DATA_DIR / "geo"


def normalizar(texto: str) -> str:
    """Mayúsculas, sin tildes, espacios recortados -- para hacer match de nombres
    entre las fuentes normativas (con tildes) y los GeoJSON (sin tildes)."""
    if texto is None:
        return ""
    nfkd = unicodedata.normalize("NFKD", texto)
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return sin_tildes.strip().upper()


def cargar_json(nombre_archivo: str) -> dict:
    ruta = DATA_DIR / nombre_archivo
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def cargar_geojson(nombre_archivo: str) -> dict:
    ruta = GEO_DIR / nombre_archivo
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


# --- Paleta institucional: "verde prado" + cartografía ---
PALETA = {
    "papel": "#F3F5EC",
    "tinta": "#22301C",
    "prado": "#4F7942",
    "prado_oscuro": "#2E4A28",
    "arena": "#E7ECDC",
    "contorno": "#8FA876",
    "achiote": "#A8481F",
    "cumple": "#3D7A34",
    "pendiente": "#B8860B",
    "no_cumple": "#A13D3D",
    "sin_dato": "#C7CDBB",
}

_TOPO_SVG_B64 = "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNDAiIGhlaWdodD0iMjQwIj4KICA8ZyBmaWxsPSJub25lIiBzdHJva2U9IiM4RkE4NzYiIHN0cm9rZS13aWR0aD0iMSIgb3BhY2l0eT0iMC4zNSI+CiAgICA8cGF0aCBkPSJNMCw0MCBRMzAsMjAgNjAsNDAgVDEyMCw0MCBUMTgwLDQwIFQyNDAsNDAiLz4KICAgIDxwYXRoIGQ9Ik0wLDkwIFEzMCw2NSA2MCw5MCBUMTIwLDkwIFQxODAsOTAgVDI0MCw5MCIvPgogICAgPHBhdGggZD0iTTAsMTQwIFEzMCwxMTUgNjAsMTQwIFQxMjAsMTQwIFQxODAsMTQwIFQyNDAsMTQwIi8+CiAgICA8cGF0aCBkPSJNMCwxOTAgUTMwLDE2NSA2MCwxOTAgVDEyMCwxOTAgVDE4MCwxOTAgVDI0MCwxOTAiLz4KICAgIDxwYXRoIGQ9Ik0tMjAsMTUgUTEwLC01IDQwLDE1IFQxMDAsMTUgVDE2MCwxNSBUMjIwLDE1Ii8+CiAgICA8cGF0aCBkPSJNLTIwLDY1IFExMCw0NSA0MCw2NSBUMTAwLDY1IFQxNjAsNjUgVDIyMCw2NSIgb3BhY2l0eT0iMC42Ii8+CiAgICA8cGF0aCBkPSJNLTIwLDExNSBRMTAsOTUgNDAsMTE1IFQxMDAsMTE1IFQxNjAsMTE1IFQyMjAsMTE1IiBvcGFjaXR5PSIwLjYiLz4KICAgIDxwYXRoIGQ9Ik0tMjAsMTY1IFExMCwxNDUgNDAsMTY1IFQxMDAsMTY1IFQxNjAsMTY1IFQyMjAsMTY1IiBvcGFjaXR5PSIwLjYiLz4KICAgIDxwYXRoIGQ9Ik0tMjAsMjE1IFExMCwxOTUgNDAsMjE1IFQxMDAsMjE1IFQxNjAsMjE1IFQyMjAsMjE1IiBvcGFjaXR5PSIwLjYiLz4KICA8L2c+Cjwvc3ZnPg=="

CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
}}

[data-testid="stAppViewContainer"] {{
    background-color: {PALETA['papel']};
    background-image: url("data:image/svg+xml;base64,{_TOPO_SVG_B64}");
    background-repeat: repeat;
    background-size: 240px 240px;
}}

[data-testid="stSidebar"] {{
    background-color: {PALETA['arena']};
    background-image: url("data:image/svg+xml;base64,{_TOPO_SVG_B64}");
    background-repeat: repeat;
    background-size: 240px 240px;
    border-right: 1px solid {PALETA['contorno']}66;
}}

h1, h2, h3 {{
    font-family: 'Source Serif 4', serif !important;
    color: {PALETA['prado_oscuro']} !important;
    letter-spacing: -0.01em;
}}

.bloque-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {PALETA['prado']};
    border-bottom: 1px solid {PALETA['contorno']}77;
    padding-bottom: 6px;
    margin-bottom: 4px;
}}

.sello {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    font-weight: 600;
    padding: 5px 14px;
    border-radius: 999px;
    border: 1.5px dashed currentColor;
}}
.sello-cumple {{ color: {PALETA['cumple']}; background: {PALETA['cumple']}14; }}
.sello-no-cumple {{ color: {PALETA['no_cumple']}; background: {PALETA['no_cumple']}14; }}
.sello-pendiente {{ color: {PALETA['pendiente']}; background: {PALETA['pendiente']}14; }}

.tarjeta-norma {{
    border-left: 3px solid {PALETA['prado']};
    background: {PALETA['arena']}CC;
    padding: 10px 16px;
    margin: 8px 0;
    border-radius: 2px;
}}

.advertencia-normativa {{
    border: 1px solid {PALETA['pendiente']}55;
    background: {PALETA['pendiente']}12;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 0.9rem;
}}

hr {{ border-color: {PALETA['contorno']}55; }}

[data-testid="stMetricValue"] {{ color: {PALETA['prado_oscuro']}; }}
</style>
"""


def sello_html(texto: str, tipo: str) -> str:
    """tipo: 'cumple' | 'no_cumple' | 'pendiente'"""
    clase = {"cumple": "sello-cumple", "no_cumple": "sello-no-cumple", "pendiente": "sello-pendiente"}[tipo]
    return f'<span class="sello {clase}">{texto}</span>'
