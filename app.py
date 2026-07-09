"""
Visor Territorial -- Ley N° 27795
Evaluación, interés nacional y avance de saneamiento territorial.

Ejecutar con:  streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st
from streamlit_folium import st_folium

from modules import motor_evaluacion, visor
from modules.utils import CSS_GLOBAL, PALETA, cargar_geojson, cargar_json, sello_html

st.set_page_config(
    page_title="Visor Territorial · Ley 27795",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown(CSS_GLOBAL, unsafe_allow_html=True)


@st.cache_data
def cargar_datos():
    return {
        "criterios": cargar_json("criterios_normativos.json"),
        "interes_nacional": cargar_json("interes_nacional.json"),
        "saneamiento": cargar_json("saneamiento_provincial.json"),
        "geo_departamentos": cargar_geojson("departamentos.geojson"),
        "geo_provincias": cargar_geojson("provincias.geojson"),
    }


datos = cargar_datos()

# ----------------------------------------------------------------------------
# Navegación
# ----------------------------------------------------------------------------
st.sidebar.markdown(
    "<div class='bloque-eyebrow'>Ley N° 27795 · Demarcación y Organización Territorial</div>",
    unsafe_allow_html=True,
)
st.sidebar.title("Visor Territorial")
pagina = st.sidebar.radio(
    "Módulo",
    [
        "Inicio",
        "1 · Motor de evaluación",
        "2 · Interés nacional",
        "3 · Saneamiento provincial",
        "4 · Visor territorial",
    ],
    label_visibility="collapsed",
)

meta_crit = datos["criterios"]["meta"]
st.sidebar.markdown("---")
st.sidebar.caption(
    f"**Base normativa:** {meta_crit['reglamento_vigente']}\n\n"
    f"**Última incorporación:** {meta_crit['ultima_actualizacion_incorporada']}\n\n"
    f"**Datos cargados:** {meta_crit['fecha_carga_datos']}"
)

# ----------------------------------------------------------------------------
# Página: Inicio
# ----------------------------------------------------------------------------
if pagina == "Inicio":
    st.title("Visor Territorial de la Ley N° 27795")
    st.markdown(
        "Herramienta de apoyo técnico-legal para evaluar centros poblados y "
        "jurisdicciones, y para seguir el **avance real de implementación** "
        "de la demarcación territorial -- no solo la información estática que "
        "ya ofrece GeoSDOT-Demarca Perú."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Categorías evaluables", len(datos["criterios"]["categorias"]))
    c2.metric("Casos de interés nacional registrados", len(datos["interes_nacional"]["declaratorias"]))
    c3.metric("Provincias con % de saneamiento confirmado", len(datos["saneamiento"]["avances"]))
    c4.metric("Modificatorias normativas rastreadas", len(datos["criterios"]["meta"]["historial_normativo"]))

    st.markdown("### Los cuatro módulos")
    st.markdown(
        """
1. **Motor de evaluación** -- ingresa población y servicios de un centro poblado y obtén, requisito por requisito, si califica para su categoría (caserío → metrópoli).
2. **Interés nacional** -- registro curado de Decretos Supremos que declaran una jurisdicción de interés nacional para priorizar su creación.
3. **Saneamiento provincial** -- % de colindancia saneada por provincia bajo la Ley 31463, actualizado con los dictámenes que aprueba el Congreso.
4. **Visor territorial** -- mapa que junta todo lo anterior por región/provincia.
        """
    )

    st.markdown(
        f"""<div class="advertencia-normativa">
        <b>Nota de rigor normativo:</b> {datos['criterios']['meta']['advertencia_umbrales']}
        </div>""",
        unsafe_allow_html=True,
    )

    if datos["criterios"]["meta"].get("actualizacion_2026-07-09"):
        st.markdown(
            f"""<div class="tarjeta-norma">
            <b>Actualización 09/07/2026:</b> {datos['criterios']['meta']['actualizacion_2026-07-09']}
            </div>""",
            unsafe_allow_html=True,
        )

    with st.expander("Historial de modificatorias normativas rastreadas"):
        df_hist = pd.DataFrame(datos["criterios"]["meta"]["historial_normativo"])
        st.dataframe(df_hist, hide_index=True, width='stretch')

# ----------------------------------------------------------------------------
# Página: Motor de evaluación
# ----------------------------------------------------------------------------
elif pagina == "1 · Motor de evaluación":
    st.title("1 · Motor de evaluación normativa")
    st.caption(
        "Evalúa un centro poblado o jurisdicción contra los criterios de categorización "
        "de la Ley 27795 y su Reglamento. Cada criterio referencia su fuente y su estado "
        "de verificación -- no son cifras fijas sin trazabilidad."
    )

    with st.form("form_evaluacion"):
        col1, col2 = st.columns([2, 1])
        with col1:
            nombre = st.text_input("Nombre del centro poblado / jurisdicción", placeholder="Ej. Huaccaña")
            departamento = st.text_input("Departamento", placeholder="Ej. Ayacucho")
            provincia = st.text_input("Provincia", placeholder="Ej. Vilcas Huamán")
        with col2:
            poblacion = st.number_input("Población concentrada", min_value=0, step=1, value=300)
            categoria_objetivo = st.selectbox(
                "Categoría que se busca acreditar",
                [c["categoria"] for c in datos["criterios"]["categorias"]],
            )

        st.markdown("**Servicios y condiciones existentes**")
        s1, s2, s3 = st.columns(3)
        vivienda = s1.checkbox("Vivienda continua o parcialmente dispersa")
        local_comunal = s1.checkbox("Local comunal de uso múltiple")
        centro_educativo = s2.checkbox("Centro educativo en funcionamiento")
        salud = s2.checkbox("Establecimiento de salud")
        plan_urbano = s3.checkbox("Plan Urbano / Plan Director aprobado")
        plan_acond = s3.checkbox("Plan de Acondicionamiento Territorial aprobado")

        enviado = st.form_submit_button("Evaluar", type="primary", width='stretch')

    if enviado:
        servicios = {
            "vivienda_continua_o_dispersa": vivienda,
            "local_comunal": local_comunal,
            "centro_educativo": centro_educativo,
            "establecimiento_salud": salud,
            "plan_urbano": plan_urbano,
            "plan_acondicionamiento_territorial": plan_acond,
        }
        r = motor_evaluacion.evaluar_centro_poblado(
            poblacion=int(poblacion),
            servicios=servicios,
            criterios=datos["criterios"],
            categoria_objetivo=categoria_objetivo,
            departamento=departamento,
            provincia=provincia,
        )

        st.markdown("---")
        titulo = nombre if nombre else "Jurisdicción evaluada"
        ubicacion = ", ".join(x for x in [provincia, departamento] if x)
        st.markdown(f"### Resultado: {titulo} {f'({ubicacion})' if ubicacion else ''}")

        if r.categoria_sugerida is None:
            st.markdown(sello_html("Sin categoría asignable automáticamente", "pendiente"), unsafe_allow_html=True)
        elif r.cumple_categoria_objetivo:
            st.markdown(sello_html(f"Cumple para {categoria_objetivo}", "cumple"), unsafe_allow_html=True)
        else:
            st.markdown(sello_html(f"No cumple (aún) para {categoria_objetivo}", "no_cumple"), unsafe_allow_html=True)

        st.write("")
        colA, colB = st.columns(2)
        with colA:
            st.markdown("**Categoría sugerida por población**")
            if r.categorias_candidatas:
                st.write(", ".join(r.categorias_candidatas))
            else:
                st.write("No determinada")
            if r.requisitos_cumplidos:
                st.markdown("**Requisitos cumplidos**")
                for req in r.requisitos_cumplidos:
                    st.markdown(f"✅ {req}")
        with colB:
            if r.requisitos_faltantes:
                st.markdown("**Requisitos pendientes**")
                for req in r.requisitos_faltantes:
                    st.markdown(f"⬜ {req}")

        if r.advertencias:
            for adv in r.advertencias:
                st.markdown(
                    f'<div class="advertencia-normativa">⚠️ {adv}</div>',
                    unsafe_allow_html=True,
                )

        with st.expander("Ver requisitos generales para creación de distrito/provincia"):
            for req in datos["criterios"]["requisitos_creacion_distrito_provincia"]:
                st.markdown(f"- {req}")

# ----------------------------------------------------------------------------
# Página: Interés nacional
# ----------------------------------------------------------------------------
elif pagina == "2 · Interés nacional":
    st.title("2 · Registro de jurisdicciones de interés nacional")
    meta_in = datos["interes_nacional"]["meta"]
    st.caption(meta_in["concepto"])

    st.markdown(
        f"""<div class="tarjeta-norma">
        <b>Marco procedimental vigente:</b> {meta_in['marco_procedimental_vigente']}
        </div>""",
        unsafe_allow_html=True,
    )

    df_in = pd.DataFrame(datos["interes_nacional"]["declaratorias"])
    departamentos_disp = ["Todos"] + sorted(df_in["departamento"].unique().tolist())
    filtro_dep = st.selectbox("Filtrar por departamento", departamentos_disp)
    if filtro_dep != "Todos":
        df_in = df_in[df_in["departamento"] == filtro_dep]

    st.dataframe(
        df_in.rename(
            columns={
                "norma_declaratoria": "Norma",
                "fecha": "Año",
                "departamento": "Departamento",
                "provincia_base": "Provincia base",
                "distrito_base": "Distrito base",
                "distrito_propuesto": "Distrito propuesto",
                "estado": "Estado",
                "tratamiento": "Tratamiento",
            }
        ),
        hide_index=True,
        width='stretch',
    )

    st.markdown(
        f'<div class="advertencia-normativa">⚠️ {meta_in["advertencia"]}</div>',
        unsafe_allow_html=True,
    )
    with st.expander("Cómo ampliar este registro"):
        for c in datos["interes_nacional"]["campos_a_completar_por_el_usuario"]:
            st.markdown(f"- {c}")

# ----------------------------------------------------------------------------
# Página: Saneamiento provincial
# ----------------------------------------------------------------------------
elif pagina == "3 · Saneamiento provincial":
    st.title("3 · Tablero de saneamiento provincial")
    meta_san = datos["saneamiento"]["meta"]
    st.caption(meta_san["mecanismo"])

    df_av = pd.DataFrame(datos["saneamiento"]["avances"])
    df_av["etiqueta"] = df_av["provincia"] + " (" + df_av["departamento"] + ")"

    fig = px.bar(
        df_av.sort_values("porcentaje_saneado"),
        x="porcentaje_saneado",
        y="etiqueta",
        orientation="h",
        text="porcentaje_saneado",
        labels={"porcentaje_saneado": "% de colindancia saneada", "etiqueta": ""},
        color="porcentaje_saneado",
        color_continuous_scale=[PALETA["sin_dato"], PALETA["cumple"]],
    )
    fig.update_traces(texttemplate="%{text}%", textposition="outside")
    fig.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        coloraxis_showscale=False,
        font=dict(family="IBM Plex Sans"),
        margin=dict(l=0, r=20, t=10, b=0),
    )
    st.plotly_chart(fig, width='stretch')

    st.markdown("#### Detalle por provincia")
    st.dataframe(
        df_av[["departamento", "provincia", "porcentaje_saneado", "detalle", "norma", "fecha_aprobacion"]].rename(
            columns={
                "departamento": "Departamento",
                "provincia": "Provincia",
                "porcentaje_saneado": "% saneado",
                "detalle": "Detalle",
                "norma": "Norma",
                "fecha_aprobacion": "Aprobación",
            }
        ),
        hide_index=True,
        width='stretch',
    )

    st.markdown("#### Recategorizaciones recientes de centros poblados")
    df_recat = pd.DataFrame(datos["saneamiento"]["recategorizaciones_recientes"])
    st.dataframe(
        df_recat.rename(
            columns={
                "centro_poblado": "Centro poblado",
                "distrito": "Distrito",
                "provincia": "Provincia",
                "departamento": "Departamento",
                "categoria_anterior": "Categoría anterior",
                "categoria_nueva": "Categoría nueva",
                "poblacion_sustento": "Población (sustento)",
                "fuente_poblacion": "Fuente de población",
                "norma": "Norma",
                "fecha_aprobacion": "Aprobación",
            }
        ),
        hide_index=True,
        width='stretch',
    )

    st.markdown(
        f'<div class="advertencia-normativa">⚠️ {meta_san["advertencia"]}</div>',
        unsafe_allow_html=True,
    )
    with st.expander(f"Departamentos sin dato confirmado en este visor ({len(datos['saneamiento']['departamentos_sin_dato_confirmado'])})"):
        st.write(", ".join(datos["saneamiento"]["departamentos_sin_dato_confirmado"]))

# ----------------------------------------------------------------------------
# Página: Visor territorial
# ----------------------------------------------------------------------------
elif pagina == "4 · Visor territorial":
    st.title("4 · Visor territorial")
    st.caption(
        "A diferencia de GeoSDOT-Demarca Perú, este mapa no muestra solo límites: "
        "muestra el AVANCE de implementación por provincia."
    )

    leyenda_cols = st.columns(5)
    tramos = [
        ("Sin dato confirmado", PALETA["sin_dato"]),
        ("< 15%", "#C9DCC9"),
        ("15% - 40%", "#7FB08F"),
        ("40% - 75%", PALETA["cumple"]),
        ("≥ 75%", "#1F5138"),
    ]
    for col, (etiqueta, color) in zip(leyenda_cols, tramos):
        col.markdown(
            f'<div style="background:{color};border-radius:4px;padding:6px;text-align:center;'
            f'font-size:0.75rem;color:#20302C;font-weight:600;">{etiqueta}</div>',
            unsafe_allow_html=True,
        )

    mapa = visor.construir_mapa(
        datos["geo_provincias"],
        datos["saneamiento"],
        datos["interes_nacional"],
    )
    st_folium(mapa, use_container_width=True, height=560, returned_objects=[])

    st.markdown(
        "🔴 Estrella roja = jurisdicción declarada de interés nacional &nbsp;·&nbsp; "
        "🟠 Flecha naranja = recategorización reciente de centro poblado"
    )
