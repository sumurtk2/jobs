# Exposición a la IA del Mercado Laboral Español

Visualización interactiva (treemap) de 342 ocupaciones del mercado laboral español, mostrando su nivel de exposición a la inteligencia artificial.

🔗 **[Ver la web](https://sumurtk2.github.io/jobs/)**

## ¿Qué es esto?

Un mapa visual donde cada rectángulo representa una ocupación. El tamaño indica el número de empleos y el color muestra el nivel de exposición a la IA (verde = baja, rojo = alta).

- **Datos salariales:** Adaptados al mercado español (EUR)
- **Empleo:** Escalado a la fuerza laboral española (~21M empleados)
- **Educación:** Sistema educativo español (ESO, FP, Grado, Máster, Doctorado)
- **Exposición IA:** Puntuación 0-10 por Gemini Flash

## Origen

Adaptación al mercado español del proyecto original de [Andrej Karpathy](https://github.com/karpathy/jobs), que usa datos del Bureau of Labor Statistics (BLS) de EE.UU.

## Estructura

```
site/index.html    # Web (HTML + JS, archivo único)
site/data.json     # Datos de ocupaciones (ES)
scores.json        # Puntuaciones de exposición IA
occupations.csv    # Datos originales BLS
build_spain_data.py # Script de adaptación a España
```
