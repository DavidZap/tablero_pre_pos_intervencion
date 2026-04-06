# Tablero de Análisis Pre-Post: Encuesta Likert Power App

## 📋 Descripción General

Este proyecto implementa un **análisis consolidado de encuestas tipo Likert (1-5)** para medir la adopción y satisfacción de la Power App de Ciencias del Comportamiento. Combina análisis estadísticos robustos con visualizaciones interactivas para evaluar el impacto de una intervención educativa.

El proyecto incluye:
- **Análisis descriptivo** de respuestas Likert con métricas de favorabilidad y neto
- **Análisis por constructos TAM/UTAUT** para entender predictores de adopción tecnológica
- **Cálculo de potencia estadística** para estudios pre-post
- **Dashboard interactivo** con Streamlit para exploración de datos

---

## 🎯 Objetivos

1. **Medir la experiencia de usuarios** con la Power App mediante escalas Likert
2. **Identificar constructos clave** de adopción tecnológica (TAM/UTAUT):
   - Facilidad de uso percibida (PEOU)
   - Utilidad percibida (PU)
   - Intención de uso futuro
   - Motivación y apropiación del conocimiento
3. **Evaluar mejoras pre-post intervención** con rigor estadístico
4. **Generar recomendaciones** basadas en análisis de preguntas abiertas

---

## 📁 Estructura del Proyecto

```
tablero_pre_pos_intervencion/
├── README.md                          # Este archivo
├── requirements.txt                   # Dependencias Python
├── streamlit_app.py                   # Dashboard interactivo
├── notebooks/
│   └── 01_analisis_likert_powerapp.ipynb    # Notebook principal con análisis completo
├── data/
│   ├── raw/
│   │   └── Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx    # Datos brutos
│   └── processed/                     # Datos procesados (generado automáticamente)
├── outputs/
│   ├── ranking_preguntas.csv          # Ranking de preguntas por promedio
│   ├── resumen_metricas.csv           # Resumen de métricas Likert
│   ├── constructos_tam_utaut.csv      # Análisis por constructos
│   ├── preguntas_abiertas_resumen.csv # Resumen de respuestas abiertas
│   └── preguntas_abiertas_terminos.csv # Términos frecuentes en abiertas
└── env_pre_pos/                       # Entorno virtual (no subir a git)
```

---

## 📦 Requisitos

- **Python 3.8+**
- Dependencias (ver `requirements.txt`):
  - `pandas` - Manipulación de datos
  - `numpy` - Operaciones numéricas
  - `matplotlib` - Visualización estática
  - `seaborn` - Gráficos estadísticos
  - `plotly` - Gráficos interactivos
  - `streamlit` - Dashboard web
  - `scipy` - Análisis estadístico (pruebas pareadas, Wilcoxon)

---

## 🚀 Instalación y Configuración

### 1. Clonar/descargar el repositorio
```bash
git clone <url-repo>
cd tablero_pre_pos_intervencion
```

### 2. Crear ambiente virtual
```bash
python -m virtualenv env_pre_pos
```

### 3. Activar ambiente

**En PowerShell (Windows):**
```powershell
.\env_pre_pos\Scripts\Activate.ps1
```

**En CMD (Windows):**
```cmd
env_pre_pos\Scripts\activate.bat
```

**En Linux/Mac:**
```bash
source env_pre_pos/bin/activate
```

### 4. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 5. Preparar datos
- Copiar el archivo Excel bruto en: `data/raw/Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx`
- El notebook lo cargará automáticamente en modo local

---

## 📊 Uso

### Opción 1: Análisis Completo en Jupyter Notebook

```bash
jupyter notebook notebooks/01_analisis_likert_powerapp.ipynb
```

El notebook ejecuta secuencialmente:
1. **Carga de datos** (local o SharePoint)
2. **Normalizacion y mapeo** a escala Likert
3. **Cálculo de métricas** globales y por pregunta
4. **Análisis por constructos** TAM/UTAUT
5. **Análisis de preguntas abiertas** (frecuencia de términos)
6. **Análisis pre-pos** (potencia estadística, pruebas pareadas)
7. **Exports** a CSV para el dashboard

### Opción 2: Dashboard Interactivo con Streamlit

```bash
streamlit run streamlit_app.py
```

Abre automáticamente http://localhost:8501 con:
- **Métricas globales** (índice de satisfacción, favorabilidad, n respuestas)
- **Mejor y peor pregunta** con desglose de métricas
- **Ranking interactivo** de preguntas (elegir métrica a visualizar)
- **Distribución Likert** en barras apiladas porcentuales
- **Análisis por constructos TAM/UTAUT** con gráficos autoescalados
- **Análisis de preguntas abiertas** con términos frecuentes

---

## 📈 Análisis Incluidos

### 1. **Análisis Descriptivo Likert**

**Métricas por pregunta:**
- `n_validas`: Respuestas válidas (no nulos)
- `promedio`: Media en escala 1-5
- `desviacion`: Desviación estándar
- `favorabilidad_pct`: % de respuestas 4-5
- `top_box_pct`: % de respuestas 5 (totalmente de acuerdo)
- `desfavorabilidad_pct`: % de respuestas 1-2
- `neto_favorabilidad_pct`: Favorabilidad - Desfavorabilidad

**Ranking:** Ordena preguntas de peor a mejor según promedio, neto y top-box.

---

### 2. **Análisis por Constructos TAM/UTAUT**

El instrumento se fundamenta en dos modelos de adopción tecnológica:

#### Constructos medidos:

| Constructo | Preguntas | Definición |
|---|---|---|
| **PEOU (Facilidad de uso percibida)** | 3 | Evalúa navegación, claridad de secciones y comprensión de términos |
| **PU (Utilidad percibida)** | 2-3 | Mide si la app facilita el diseño de intervenciones y mejora aplicación de conocimiento |
| **Intención de uso futuro** | 2 | Indaga si usaría la app en futuras iniciativas o la recomendaría |
| **Motivación y apropiación** | 3 | Captura motivación para aplicar ciencias del comportamiento y difusión de conocimiento |

#### Mapeo de preguntas por constructo

Las preguntas se mapean en el análisis de la siguiente manera:

1. **PEOU (Facilidad de uso percibida)**
   - Sé cómo navegar la herramienta.
   - Entiendo el propósito de cada sección de la app ("¿Qué son las Ciencias del Comportamiento?", "Diseña tu Intervención Comportamental", "Registra el impacto de tu intervención").
   - Los términos usados en la Power App que son nuevos para mí los entiendo con facilidad.

2. **PU (Utilidad percibida)**
   - Las herramientas prácticas que te permiten diligenciar campos e interactuar con la app en la sección de "Diseña tu Intervención Comportamental" facilitan diseñar intervenciones.
   - Siento que la app puede ser mi herramienta principal para realizar una intervención comportamental.
   - Considero que la herramienta mejora/facilita la aplicación de Ciencias del Comportamiento.

3. **Intención de uso futuro**
   - La usaría en futuras iniciativas.
   - Considero que esta App puede ser útil incluso para colaboradores que no han tenido espacios con B-Lab.

4. **Motivación y apropiación del conocimiento**
   - Puedo asociar el contenido teórico de la Power App con los retos que tengo en mi rol.
   - Usar esta herramienta me motiva a aplicar Ciencias del Comportamiento en mis proyectos.
   - Comparto con otras personas conocimientos encontrados en la herramienta.

Nota: en el archivo de datos original, algunos encabezados pueden incluir sufijos como ".Selecciona" o variaciones de espacios/puntuación; el mapeo del notebook contempla esos nombres exactos de columnas.

**Métricas por constructo:**
- Promedio agregado de items
- Favorabilidad y neto agregados
- Alfa de Cronbach (consistencia interna, idealmente > 0.7)

**Interpretación:**
- TAM predice que PEOU y PU predicen intención de uso
- Intención de uso predice comportamiento real de adopción
- Motivación moderará la relación entre utilidad y adopción

---

### 3. **Análisis Pre-Pos (Significancia y Potencia)**

**Para estudios con medición pre-intervención y post-intervención:**

```python
PRE_INDICE_GLOBAL = 3.906  # Promedio pre en escala 1-5
N_PRE = 27                  # N pre-intervención
ALPHA = 0.07                # Nivel de significancia
POWER_TARGET = 0.80         # Potencia deseada
```

**Calcula:**
1. **Delta mínima para significancia**: Cambio requerido en promedio para p < alpha
2. **Delta mínima para potencia**: Cambio requerido para 80% de probabilidad detectarlo
3. **Media pos mínima esperada**: PRE_INDICE + delta
4. **Tamaño de efecto (dz)**: Comparación estandarizada pre-pos

**Ejemplo:** Si SD_delta = 0.8 y n = 27, necesitas delta mínima de ~0.39 para p < 0.07

---

### 4. **Análisis de Preguntas Abiertas**

**Procesamiento:**
- Limpieza: minúsculas, sin acentos, espacios limpios
- Tokenización: palabras de 3+ caracteres
- Stopwords: Filtra palabras comunes (que, para, app, etc.)
- Frecuencia: Top 12 términos más frecuentes por pregunta

**Outputs:**
- `preguntas_abiertas_resumen.csv`: Nº de respuestas y longitud promedio
- `preguntas_abiertas_terminos.csv`: Términos con frecuencias para cada pregunta abierta

---

## 📁 Archivos de Salida (CSV)

Generados en `outputs/`:

1. **ranking_preguntas.csv**
   - Todas las preguntas Likert ordenadas peor → mejor
   - Todas las métricas calculadas

2. **resumen_metricas.csv**
   - Frecuencias absoluta por categoría Likert (1-5) para cada pregunta

3. **constructos_tam_utaut.csv**
   - Métricas agregadas por los 4 constructos
   - Alfa de Cronbach por constructo

4. **preguntas_abiertas_resumen.csv**
   - Nº de respuestas no vacías por pregunta abierta
   - Longitud promedio del texto

5. **preguntas_abiertas_terminos.csv**
   - Términos más frecuentes y sus conteos
   - Asociados a cada pregunta abierta

---

## 🔧 Configuración Personalizada

### Cambiar mapeo de constructos
En el notebook, celda "Mapeo de preguntas a constructos":
```python
CONSTRUCTOS = {
    "Mi_Constructo": [
        "Pregunta 1 exacta del dataset",
        "Pregunta 2 exacta del dataset",
    ]
}
```

### Cambiar parámetros pre-pos
En celda "Análisis Pre-Pos":
```python
PRE_INDICE_GLOBAL = 3.5      # Tu promedio pre actual
N_PRE = 30                    # Tu N pre
ALPHA = 0.05                  # Tu alpha (ej: 0.05 o 0.07)
POWER_TARGET = 0.80           # Potencia deseada (típicamente 0.80)
```

### Cambiar preguntas abiertas
En `CONFIG`:
```python
"open_text_columns": [
    "Tu pregunta abierta 1",
    "Tu pregunta abierta 2",
]
```

---

## 📝 Interpretación de Resultados

### Neto de Favorabilidad vs Promedio

| Métrica | Qué mide | Cuándo usar |
|---|---|---|
| **Promedio** | Tendencia central en escala 1-5 | Comparar niveles absolutos |
| **Neto** | Brecha entre favorables (4-5) y desfavorables (1-2) | Detectar polarización, decisiones |

**Ejemplo:**
- Constructo A: promedio 3.9, neto 65% → gente acuerda pero algunos neutrales
- Constructo B: promedio 3.9, neto 45% → gente más dispersa en opiniones

---

## 🧪 Validaciones Incluidas

El notebook ejecuta automáticamente:

1. ✅ Al menos 1 pregunta Likert detectada
2. ✅ Todos los valores mapeados entre 1-5 (o NaN)
3. ✅ Frecuencias totales coinciden con respuestas válidas
4. ✅ Pruebas unitarias de funciones críticas (normalización, mapeo, alfa)

---

## 🐛 Troubleshooting

### Error: "No se encontró archivo fallback"
**Solución:** Copia el Excel bruto en `data/raw/Experiencia_en_el_uso_de_Power_App_B-Lab.xlsx`

### Error: "No se detectaron columnas Likert"
**Solución:** Revisa `CONFIG["metadata_columns"]` y `CONFIG["open_text_columns"]` — asegúrate de que las preguntas Likert no estén listadas ahí.

### Gráficos de constructos con rangos extraños
**Solución:** Normal — la escala se autoajusta al min/max de tus datos reales (no a rangos fijos).

### ImportError: No module named 'plotly'
**Solución:**
```bash
pip install plotly
```

---

## 📚 Referencias

- **TAM (Technology Acceptance Model):** Davis, F. D. (1989). "Perceived usefulness, perceived ease of use, and user acceptance of information technology."
- **UTAUT (Unified Theory of Acceptance and Use of Technology):** Venkatesh, V., et al. (2003). "User Acceptance of Information Technology: Toward a Unified View."
- **Alfa de Cronbach:** Medida de consistencia interna multiítem (valores > 0.7 indican buena consistencia)
- **Prueba t pareada:** Compara medias pre-post para n pares pequeños (típicamente n ≤ 30)
- **Potencia estadística:** Probabilidad de detectar un efecto si realmente existe

---

## 👤 Autor

**Desarrollado para:** Maestría en Estudios del Comportamiento - B-Lab  
**Propósito:** Medición y evaluación de adopción de Power App educativa  
**Fecha:** Abril 2026

---

## 📄 Licencia

Este proyecto está disponible para uso interno dentro de B-Lab.

---

## 📞 Contacto / Soporte

Para preguntas sobre:
- **Análisis estadístico:** Revisar docstrings en funciones del notebook
- **Configuración:** Ver secciones "Configuración Personalizada" arriba
- **Bugs:** Verificar sección "Troubleshooting"

---

## ✅ Checklist Pre-Producción

- [ ] Archivo Excel copiado en `data/raw/`
- [ ] `requirements.txt` actualizado con versiones
- [ ] Notebook ejecutado exitosamente (todas las celdas)
- [ ] Archivos CSV generados en `outputs/`
- [ ] Dashboard Streamlit carga sin errores
- [ ] Parámetros pre-pos ajustados a tu estudio (si aplica)
- [ ] README revisado y actualizado

---

**Última actualización:** 04 de abril de 2026
