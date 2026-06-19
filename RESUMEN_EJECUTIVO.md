# Resumen Ejecutivo: Tablero Pre-Post Power App

## Que es

Tablero interactivo para medir adopcion, satisfaccion y cambios de comportamiento asociados al uso de la Power App de Ciencias del Comportamiento.

## Para que sirve

1. Monitorea experiencia de usuario con escala Likert (1-5).
2. Compara resultados pretest vs postest para estimar impacto de una intervencion.
3. Identifica puntos criticos de mejora por pregunta, seccion y flujo de uso.
4. Entrega evidencia visual y exportable para decisiones de producto y formacion.

## Que informacion entrega

### 1) Vista de encuesta

- Indice global de satisfaccion.
- Favorabilidad global y neto de favorabilidad.
- Ranking de preguntas de menor a mayor desempeno.
- Distribucion de respuestas por categoria Likert.
- Mejor y peor pregunta para priorizacion.

### 2) Vista de impacto pre-post

- Personas en pretest, postest y pares comparables.
- Delta global de mejora.
- Cambio por pregunta con tamano de efecto.
- Prueba de significancia (Wilcoxon) por pregunta y resumen global.
- Exportacion a CSV para reporte.

### 3) Vista de preguntas abiertas

- Terminos mas frecuentes por pregunta.
- Resumen de volumen y longitud de respuestas.
- Tabla filtrable para analisis cualitativo rapido.

### 4) Vista de uso de la app (si hay log de usabilidad)

- Sesiones, usuarios unicos y duracion promedio.
- Secciones con mayor abandono/completitud.
- Caminos de navegacion mas frecuentes.
- Franjas horarias y tendencia de uso.

## Hallazgos que habilita

1. Deteccion temprana de fricciones de contenido o navegacion.
2. Cuantificacion de mejora posterior a capacitacion/intervencion.
3. Priorizacion basada en datos para backlog de mejoras.
4. Seguimiento de adopcion real de la herramienta en el tiempo.

## Requisitos operativos

- Archivos de encuesta en data/raw (pre y post).
- CSV de pipeline en outputs.
- Ejecucion local del tablero con Streamlit.

## Ruta de implementacion sugerida

1. Cargar datos del periodo actual.
2. Regenerar salidas analiticas.
3. Revisar tablero con lideres funcionales.
4. Definir acciones por top 3 hallazgos.
5. Repetir ciclo en la siguiente medicion.

## KPI sugeridos para comite

- Indice global (escala 1-5).
- Favorabilidad global (% 4-5).
- Delta pre-post global.
- Preguntas con cambio significativo (p < 0.05).
- Tasa de abandono por seccion clave.

## Mensaje clave

El tablero no solo describe percepciones: permite demostrar si hubo mejora estadisticamente defendible y en que puntos conviene intervenir primero.
