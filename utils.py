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


# --- Paleta institucional/cartográfica (ver design tokens en README) ---
PALETA = {
    "papel": "#F3F2EC",
    "tinta": "#20302C",
    "andina": "#2C4A45",
    "achiote": "#A8481F",
    "sillar": "#8B7355",
    "cumple": "#3D7A5C",
    "pendiente": "#B8860B",
    "no_cumple": "#A13D3D",
    "sin_dato": "#C9C7BB",
}

CSS_GLOBAL = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@500&display=swap');

html, body, [class*="css"] {{
    font-family: 'IBM Plex Sans', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'Source Serif 4', serif !important;
    color: {PALETA['tinta']} !important;
    letter-spacing: -0.01em;
}}

.bloque-eyebrow {{
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: {PALETA['achiote']};
    border-bottom: 1px solid {PALETA['sillar']}55;
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
    border-left: 3px solid {PALETA['achiote']};
    background: {PALETA['andina']}08;
    padding: 10px 16px;
    margin: 8px 0;
    border-radius: 2px;
}}

.advertencia-normativa {{
    border: 1px solid {PALETA['pendiente']}55;
    background: {PALETA['pendiente']}0E;
    border-radius: 4px;
    padding: 12px 16px;
    font-size: 0.9rem;
}}

hr {{ border-color: {PALETA['sillar']}44; }}
</style>
"""


def sello_html(texto: str, tipo: str) -> str:
    """tipo: 'cumple' | 'no_cumple' | 'pendiente'"""
    clase = {"cumple": "sello-cumple", "no_cumple": "sello-no-cumple", "pendiente": "sello-pendiente"}[tipo]
    return f'<span class="sello {clase}">{texto}</span>'
