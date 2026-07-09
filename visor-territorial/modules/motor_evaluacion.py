"""
Módulo 1 -- Motor de Evaluación Normativa.

Evalúa un centro poblado / jurisdicción contra los criterios de categorización
de la Ley 27795 y su Reglamento (Art. 72, D.S. 191-2020-PCM / TUO 134-2025-PCM).
El motor está "versionado": cada criterio referencia la norma de la que
proviene y su estado de verificación, en lugar de tratar los umbrales como
constantes fijas sin trazabilidad.
"""
from dataclasses import dataclass, field

LIMA_CALLAO = {"LIMA", "CALLAO"}


@dataclass
class ResultadoEvaluacion:
    categoria_sugerida: str | None
    poblacion: int
    cumple_categoria_objetivo: bool | None
    requisitos_cumplidos: list = field(default_factory=list)
    requisitos_faltantes: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)
    categorias_candidatas: list = field(default_factory=list)


def categoria_por_poblacion(poblacion: int, categorias: list[dict]) -> list[dict]:
    """Devuelve la(s) categoría(s) cuyo rango poblacional confirmado incluye
    a `poblacion`. Con el Art. 72 verificado, los tramos son continuos
    (51 en adelante) y ya no dejan un hueco entre caserío y ciudad."""
    candidatas = []
    for cat in categorias:
        pmin = cat["poblacion_min"]
        pmax = cat["poblacion_max"]
        if pmin is None and pmax is None:
            continue
        if pmin is not None and poblacion < pmin:
            continue
        if pmax is not None and poblacion > pmax:
            continue
        candidatas.append(cat)
    return candidatas


def _es_lima_o_callao(departamento: str, provincia: str) -> bool:
    dep = (departamento or "").strip().upper()
    prov = (provincia or "").strip().upper()
    return dep in LIMA_CALLAO or prov in LIMA_CALLAO


def evaluar_centro_poblado(
    poblacion: int,
    servicios: dict,
    criterios: dict,
    categoria_objetivo: str | None = None,
    departamento: str = "",
    provincia: str = "",
) -> ResultadoEvaluacion:
    """
    servicios: dict con llaves booleanas, ej.
        {"vivienda_continua_o_dispersa": True, "local_comunal": True,
         "centro_educativo": False, "establecimiento_salud": False,
         "plan_acondicionamiento_territorial": False}
    """
    categorias = criterios["categorias"]
    candidatas = categoria_por_poblacion(poblacion, categorias)

    resultado = ResultadoEvaluacion(
        categoria_sugerida=None,
        poblacion=poblacion,
        cumple_categoria_objetivo=None,
    )

    if not candidatas:
        resultado.advertencias.append(
            f"Con {poblacion} habitantes, la jurisdicción no alcanza el mínimo "
            f"de 51 habitantes que exige el Art. 72 para categorizarse como "
            f"'caserío menor' (el mínimo de 50 habitantes del Art. 8.2 aplica "
            f"solo a la CREACIÓN inicial del centro poblado, un trámite previo "
            f"y distinto ante la municipalidad distrital)."
        )
        return resultado

    resultado.categorias_candidatas = [c["categoria"] for c in candidatas]
    cat = candidatas[0]

    # Caso especial: "metrópoli nacional" está reservada por norma a Lima y
    # Callao, no es solo un umbral poblacional -- si hay dos candidatas
    # (metrópoli regional y metrópoli nacional) se resuelve por ubicación.
    if len(candidatas) > 1:
        es_lima_callao = _es_lima_o_callao(departamento, provincia)
        preferida = next(
            (c for c in candidatas if ("nacional" in c["categoria"]) == es_lima_callao),
            candidatas[0],
        )
        cat = preferida
        if any(c.get("designacion_especial") for c in candidatas):
            resultado.advertencias.append(
                "'Metrópoli Nacional' es una designación reservada expresamente "
                "a Lima y Callao por el Art. 72, no un tramo poblacional propio; "
                "cualquier otra jurisdicción que supere 500,000 habitantes es "
                "'Metrópoli Regional'."
            )

    resultado.categoria_sugerida = cat["categoria"]

    if not cat.get("verificado_contra_tuo_2025", False):
        resultado.advertencias.append(
            f"El rango poblacional usado para '{cat['categoria']}' proviene de "
            f"{cat['fuente']} y no fue verificado contra el TUO 2025 "
            f"(D.S. 134-2025-PCM). Confirmar antes de usar en un expediente real."
        )
    else:
        resultado.advertencias.append(
            f"Umbral verificado: {cat['fuente']}. Pendiente únicamente confirmar "
            f"que el TUO (D.S. 134-2025-PCM) conserva el mismo número de "
            f"artículo tras la consolidación -- el contenido sustantivo tiene "
            f"alta confianza por doble corroboración independiente."
        )

    # Chequeo de requisitos no-poblacionales (servicios) declarados como texto
    # libre en criterios_normativos.json -- se listan para revisión manual,
    # ya que no siempre corresponden 1:1 a una llave booleana simple.
    # Cada entrada: (palabras clave que deben aparecer TODAS, llave del servicio)
    mapa_servicios = [
        (["vivienda"], "vivienda_continua_o_dispersa"),
        (["local comunal"], "local_comunal"),
        (["centro educativo"], "centro_educativo"),
        (["salud"], "establecimiento_salud"),
        (["plan de acondicionamiento territorial"], "plan_acondicionamiento_territorial"),
        (["plan urbano"], "plan_urbano"),
        (["plan director"], "plan_urbano"),
        (["esquema de acondicionamiento urbano"], "plan_urbano"),
    ]

    for requisito in cat["requisitos_minimos"]:
        req_lower = requisito.lower()
        llave = next(
            (v for palabras, v in mapa_servicios if all(p in req_lower for p in palabras)),
            None,
        )
        if llave is None:
            resultado.requisitos_faltantes.append(f"{requisito} (verificar documentalmente)")
            continue
        if servicios.get(llave):
            resultado.requisitos_cumplidos.append(requisito)
        else:
            resultado.requisitos_faltantes.append(requisito)

    if categoria_objetivo:
        resultado.cumple_categoria_objetivo = (
            categoria_objetivo == cat["categoria"]
            and len([r for r in resultado.requisitos_faltantes if "verificar documentalmente" not in r]) == 0
        )

    return resultado
