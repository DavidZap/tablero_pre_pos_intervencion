# Tablero de Analisis Pre-Post: Encuesta Likert Power App

Resumen ejecutivo para stakeholders: ver RESUMEN_EJECUTIVO.md.

## Descripcion general

Proyecto para analizar encuestas Likert (1-5) sobre adopcion y experiencia de uso de una Power App de Ciencias del Comportamiento.

Incluye tres componentes principales:

1. Pipeline de analisis (notebooks + scripts) para generar CSV de resultados.
2. Comparativo pretest vs postest con emparejamiento por persona y prueba de Wilcoxon.
3. Dashboard en Streamlit para explorar resultados de encuesta, preguntas abiertas y analitica de uso de la app.

## Objetivos

1. Medir satisfaccion y percepciones de uso con escala Likert.
2. Detectar cambios pre-post de la intervencion con criterios estadisticos.
3. Priorizar oportunidades de mejora a nivel de pregunta y seccion.
4. Exponer resultados en un tablero ejecutable para equipos no tecnicos.

## Estructura actual

```text
tablero_pre_pos_intervencion/
|-- README.md
|-- requirements.txt
|-- streamlit_app.py
|-- analisis_actualizado.py
|-- comparar_pruebas.py
|-- notebooks/
|   |-- 01_analisis_likert_powerapp.ipynb
|   |-- 02_analisis_prepost_completo.ipynb
|-- data/
|   |-- raw/
|   `-- processed/
`-- outputs/
    |-- ranking_preguntas.csv
    |-- resumen_metricas.csv
    |-- constructos_tam_utaut.csv
    |-- preguntas_abiertas_resumen.csv
    |-- preguntas_abiertas_terminos.csv
    |-- comparativo_prepost.csv
    |-- recordatorios_usabilidad.csv
    `-- recordatorios_ultima_accion.csv
```

## Requisitos

- Python 3.10+
- Dependencias en requirements.txt

Principales librerias:

- pandas
- numpy
- scipy
- plotly
- streamlit
- openpyxl
- python-dotenv
- office365-rest-python-client

## Instalacion rapida

En Windows (PowerShell):

```powershell
python -m venv env_pre_pos
.\env_pre_pos\Scripts\Activate.ps1
pip install -r requirements.txt
```

En Windows (CMD):

```cmd
python -m venv env_pre_pos
env_pre_pos\Scripts\activate.bat
pip install -r requirements.txt
```

## Datos esperados

Ubicacion: data/raw/

Archivos clave:

- Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx (pretest)
- Experiencia_en_el_uso_de_Power_App_B-Lab - postest.xlsx (postest)
- Usabilidad Power APP.xlsx (eventos de uso, opcional para modulo de analitica)

Notas:

- El comparativo pre-post empareja por Correo electronico.
- Si falta correo, el dashboard intenta fallback por Nombre.
- Los textos Likert se normalizan (minusculas, sin acentos, espacios limpios) antes del mapeo a 1-5.

## Flujo recomendado

1. Cargar/actualizar archivos fuente en data/raw.
2. Ejecutar notebook(s) de analisis para regenerar CSV en outputs.
3. Levantar dashboard y validar visualmente.
4. Exportar comparativos desde el dashboard cuando aplique.

## Ejecucion

### 1) Notebooks

```bash
jupyter notebook notebooks/01_analisis_likert_powerapp.ipynb
```

Opcional para analisis pre-post extendido:

```bash
jupyter notebook notebooks/02_analisis_prepost_completo.ipynb
```

### 2) Scripts auxiliares

Comparativo pre-post rapido (con pares por persona):

```bash
python analisis_actualizado.py
```

Comparacion Wilcoxon vs t pareada con vectores de ejemplo:

```bash
python comparar_pruebas.py
```

### 3) Dashboard Streamlit

```bash
streamlit run streamlit_app.py
```

URL local por defecto: http://localhost:8501

## Que muestra el dashboard

### Encuesta Likert

- Indice global, favorabilidad global, total de respuestas y numero de preguntas.
- Ranking de preguntas por metrica (promedio, favorabilidad, top-box, desfavorabilidad, neto).
- Distribucion Likert en barras apiladas porcentuales.
- Mejor y peor pregunta.
- Detalle por persona (comparado contra promedio global).

### Pretest vs postest

- Numero de personas en pre, post y pares emparejados.
- Indice global pre y post, delta global y porcentaje de personas que mejoran.
- Cambios por pregunta con:
  - delta promedio
  - porcentaje mejora/sin cambio/empeora
  - p-valor Wilcoxon
  - tamano de efecto dz y categoria
- Exportacion automatica y descarga manual de comparativo_prepost.csv.

### Preguntas abiertas

- Resumen por pregunta abierta.
- Top de terminos frecuentes.
- Tabla de respuestas completas con filtro por texto y por persona.

### Analitica de uso de la app (si existe Usabilidad Power APP.xlsx)

- Usuarios unicos, sesiones, duracion promedio y eventos.
- Tendencia historica de inicios.
- Abandono/completitud por seccion (texto y section_id estable).
- Caminos de navegacion mas frecuentes.
- Franjas horarias de mayor actividad.

## Archivos de salida principales

Generados en outputs/:

- ranking_preguntas.csv
- resumen_metricas.csv
- constructos_tam_utaut.csv
- preguntas_abiertas_resumen.csv
- preguntas_abiertas_terminos.csv
- comparativo_prepost.csv

Si hay analitica de uso:

- recordatorios_usabilidad.csv
- recordatorios_ultima_accion.csv

## Criterio de significancia (dashboard)

Para conclusion de intervencion significativa (indice global pre-post):

1. Delta global > 0
2. p-valor de Wilcoxon < 0.05

Si scipy/Wilcoxon no esta disponible, el dashboard aplica una regla fallback por magnitud del cambio.

## Troubleshooting

### El dashboard muestra error de archivos faltantes

Ejecuta el notebook de pipeline y confirma que existan en outputs, al menos:

- ranking_preguntas.csv
- resumen_metricas.csv
- preguntas_abiertas_resumen.csv
- preguntas_abiertas_terminos.csv

### No aparece comparativo pre-post

Verifica:

- Que existan ambos archivos (pretest y postest) en data/raw.
- Que compartan columnas Likert comparables.
- Que exista una clave comun por persona (correo o nombre).

### ImportError de librerias

```bash
pip install -r requirements.txt
```

## Licencia

Uso interno B-Lab.

## Ultima actualizacion

18 de junio de 2026
