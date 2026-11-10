# Caza Coordenadas

Juego para aprender coordenadas geográficas en un planisferio. En cada ronda aparece una coordenada y tres pines de colores: solo uno está en el lugar correcto. El juego explica cada acierto y cada error, y al final muestra un resumen.

- Tres niveles: Explorador, Navegante y Capitán.
- Diez rondas por partida, con puntos extra por racha.
- El avance y el mejor puntaje se guardan en el navegador de cada dispositivo.

## Archivos

- `index.html`: el juego completo en un solo archivo.
- `template.html`: la fuente del juego, sin el mapa.
- `build.py`: inserta el contorno de los continentes en la plantilla.

Para regenerar el juego después de editar `template.html`:

```bash
python build.py land-110m.json template.html juego.html
```

El script descarga `land-110m.json` si no existe. El resultado es el contenido de la página; `index.html` le agrega el encabezado HTML (`<!doctype html>`, `charset` y `viewport`).

El mapa proviene de Natural Earth (dominio público), a través de world-atlas.
