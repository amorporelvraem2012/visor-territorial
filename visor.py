"""
Módulo 4 -- Visor Territorial.

A diferencia de GeoSDOT-Demarca Perú (que muestra límites e información
general), este visor superpone el AVANCE de implementación: % de saneamiento
por provincia (Ley 31463), jurisdicciones de interés nacional y
recategorizaciones recientes.
"""
import folium

from .utils import normalizar, PALETA

CENTRO_PERU = (-9.19, -75.02)


def _color_por_porcentaje(pct: float) -> str:
    if pct >= 75:
        return "#1F5138"
    if pct >= 40:
        return "#3D7A5C"
    if pct >= 15:
        return "#7FB08F"
    return "#C9DCC9"


def construir_mapa(
    geojson_provincias: dict,
    saneamiento: dict,
    interes_nacional: dict,
) -> folium.Map:
    avances = saneamiento["avances"]
    # índice provincia_normalizada -> registro de avance (puede haber varias
    # provincias con el mismo nombre en distintos departamentos, ej. no aplica
    # aquí pero se deja el índice por departamento+provincia para exactitud)
    indice = {}
    for a in avances:
        for prov_txt in a["provincia"].split("/"):
            clave = (normalizar(a["departamento"]), normalizar(prov_txt))
            indice[clave] = a
        # Caso especial Callao: el registro de Lima también aplica a la
        # provincia Callao aunque el "departamento" declarado sea Lima.
        if "callao" in a["provincia"].lower():
            indice[(normalizar("Callao"), normalizar("Callao"))] = a

    m = folium.Map(
        location=CENTRO_PERU,
        zoom_start=6,
        tiles="CartoDB positron",
        control_scale=True,
    )

    def estilo(feature):
        dep = normalizar(feature["properties"].get("FIRST_NOMB", ""))
        prov = normalizar(feature["properties"].get("NOMBPROV", ""))
        registro = indice.get((dep, prov))
        if registro:
            color = _color_por_porcentaje(registro["porcentaje_saneado"])
        else:
            color = PALETA["sin_dato"]
        return {
            "fillColor": color,
            "color": PALETA["tinta"],
            "weight": 0.6,
            "fillOpacity": 0.85,
        }

    def resaltado(feature):
        return {"weight": 2.5, "color": PALETA["achiote"], "fillOpacity": 0.95}

    def texto_tooltip(feature):
        dep = normalizar(feature["properties"].get("FIRST_NOMB", ""))
        prov = normalizar(feature["properties"].get("NOMBPROV", ""))
        registro = indice.get((dep, prov))
        nombre_prov = feature["properties"].get("NOMBPROV", "?")
        nombre_dep = feature["properties"].get("FIRST_NOMB", "?")
        if registro:
            return (
                f"<b>{nombre_prov} ({nombre_dep})</b><br>"
                f"Saneamiento: <b>{registro['porcentaje_saneado']}%</b><br>"
                f"{registro['detalle'][:120]}...<br>"
                f"<i>{registro['norma']}</i>"
            )
        return f"<b>{nombre_prov} ({nombre_dep})</b><br>Sin dato confirmado en este visor todavía."

    # folium.GeoJsonTooltip no acepta una función por feature directamente,
    # así que precalculamos el HTML del tooltip como una propiedad más y lo
    # referenciamos por nombre de campo.
    for feature in geojson_provincias["features"]:
        feature["properties"]["_tooltip_html"] = texto_tooltip(feature)
    capa = folium.GeoJson(
        geojson_provincias,
        name="Avance de saneamiento provincial (Ley 31463)",
        style_function=estilo,
        highlight_function=resaltado,
        tooltip=folium.GeoJsonTooltip(fields=["_tooltip_html"], aliases=[""], labels=False, sticky=True),
    )
    capa.add_to(m)

    # --- Marcadores: jurisdicciones de interés nacional ---
    coords_conocidas = {
        "juliaca": (-15.4997, -70.1339),
        "moquegua": (-17.1946, -70.9347),
    }
    for d in interes_nacional["declaratorias"]:
        clave = normalizar(d["distrito_base"]).lower()
        coord = coords_conocidas.get(clave)
        if not coord:
            continue
        folium.Marker(
            location=coord,
            popup=folium.Popup(
                f"<b>Interés nacional -- {d['norma_declaratoria']}</b><br>"
                f"Base: {d['distrito_base']}, {d['provincia_base']} ({d['departamento']})<br>"
                f"Distrito propuesto: <b>{d['distrito_propuesto']}</b><br>"
                f"{d['tratamiento']}",
                max_width=280,
            ),
            tooltip=f"Interés nacional: {d['distrito_propuesto']}",
            icon=folium.Icon(color="darkred", icon="star", prefix="fa"),
        ).add_to(m)

    # --- Marcador: recategorización reciente (Campo Verde, Ucayali) ---
    for r in saneamiento.get("recategorizaciones_recientes", []):
        # Campo Verde, Coronel Portillo, Ucayali (coordenada aproximada del distrito)
        folium.Marker(
            location=(-8.4708, -74.6167),
            popup=folium.Popup(
                f"<b>Recategorización -- {r['centro_poblado']}</b><br>"
                f"{r['categoria_anterior']} → <b>{r['categoria_nueva']}</b><br>"
                f"Población: {r['poblacion_sustento']:,} hab. ({r['fuente_poblacion']})<br>"
                f"<i>{r['norma']}</i>",
                max_width=280,
            ),
            tooltip=f"Recategorización: {r['centro_poblado']}",
            icon=folium.Icon(color="orange", icon="arrow-up", prefix="fa"),
        ).add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    return m
