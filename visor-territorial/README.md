# Visor Territorial · Ley N° 27795

Herramienta de apoyo técnico-legal para la evaluación de centros poblados y
jurisdicciones bajo la Ley N° 27795 (Demarcación y Organización Territorial),
y para el seguimiento del avance real de implementación -- no solo la
información estática que ya ofrece el portal oficial GeoSDOT-Demarca Perú
(geosdot.servicios.gob.pe).

## Módulos

1. **Motor de evaluación normativa** (`modules/motor_evaluacion.py`) -- evalúa
   población + servicios contra los umbrales de categorización (caserío →
   metrópoli), citando la norma fuente de cada criterio y marcando cuáles
   están o no verificados contra el TUO 2025.
2. **Registro de interés nacional** (`data/interes_nacional.json`) -- casos
   curados de Decretos Supremos que declaran una jurisdicción de interés
   nacional para priorizar su creación.
3. **Tablero de saneamiento provincial** (`data/saneamiento_provincial.json`)
   -- % de colindancia saneada por provincia bajo la Ley 31463.
4. **Visor territorial** (`modules/visor.py`) -- mapa Folium que junta los
   tres módulos anteriores por provincia.

## Cómo correrlo

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fuentes de datos y cómo mantenerlas al día

Todos los datos "vivos" (normativa, % de saneamiento, casos de interés
nacional) están en archivos JSON dentro de `data/`, no hardcodeados en el
código -- así se pueden actualizar sin tocar la lógica.

| Archivo | Qué contiene | Cómo actualizarlo |
|---|---|---|
| `criterios_normativos.json` | Umbrales de categorización (Art. 72) + historial de modificatorias del Reglamento | **Actualizado 09/07/2026**: los umbrales de caserío (menor/mayor), pueblo, villa, ciudad (menor/intermedia/mayor) y metrópoli (regional/nacional) están verificados contra el Art. 72 del D.S. 191-2020-PCM (mod. por D.S. 074-2025-PCM), corroborado en dos fuentes independientes. Pendiente: confirmar que el TUO (D.S. 134-2025-PCM) conservó el mismo número de artículo al consolidar |
| `interes_nacional.json` | Casos de zonas declaradas de interés nacional | Buscar en El Peruano ("zona de interés nacional" + "creación de distrito") y en dictámenes de la Comisión de Descentralización del Congreso |
| `saneamiento_provincial.json` | % de saneamiento por provincia (Ley 31463) | Revisar comunicaciones.congreso.gob.pe y las leyes específicas que el Pleno aprueba por departamento |
| `geo/departamentos.geojson`, `geo/provincias.geojson` | Polígonos de límites referenciales | Fuente: INEI 2007 vía el repositorio abierto `juaneladio/peru-geojson`. Para límites oficiales SDOT, ver el Registro Nacional de Límites vía IDEP (idep.gob.pe) |

### Umbrales de categorización vigentes (Art. 72)

| Categoría | Población |
|---|---|
| Caserío menor | 51 - 500 |
| Caserío mayor | 501 - 1,000 |
| Pueblo | 1,001 - 2,000 |
| Villa | 2,001 - 5,000 |
| Ciudad menor | 5,001 - 20,000 |
| Ciudad intermedia | 20,001 - 100,000 |
| Ciudad mayor | 100,001 - 500,000 |
| Metrópoli regional | Más de 500,000 |
| Metrópoli nacional | Lima y Callao (designación expresa, no solo umbral) |

Fuente: Art. 72 del Reglamento (D.S. 191-2020-PCM, con la redacción del D.S.
074-2025-PCM), corroborado en un informe técnico de la Gerencia Regional de
Planeamiento de Huánuco y en la Guía Práctica de Centros Poblados de IBC Perú
(2024). Ambas fuentes citan el mismo artículo con las mismas cifras.

**Importante:** los límites geográficos usados son censales/referenciales
(INEI 2007), igual que los que aclara el propio GeoSDOT -- no tienen efecto
demarcatorio oficial. Para un uso normativo real, los polígonos oficiales
deben salir del Registro Nacional de Límites de la SDOT.

## Próximos pasos sugeridos

- Automatizar la carga de `saneamiento_provincial.json` con scraping
  periódico de comunicaciones.congreso.gob.pe (requiere acceso de red que
  este entorno de Claude no tiene habilitado; correrlo desde tu propia
  máquina o CI).
- Confirmar que el Art. 72 conserva ese mismo número en el texto final del
  TUO (D.S. 134-2025-PCM) -- el contenido sustantivo ya está corroborado en
  dos fuentes independientes, falta solo la numeración exacta si se va a
  citar en un expediente real.
- Si se despliega en Streamlit Community Cloud (mismo patrón que
  `navarro-ochoa.streamlit.app`), subir el repo a GitHub y conectar ahí --
  no requiere cambios de código.
