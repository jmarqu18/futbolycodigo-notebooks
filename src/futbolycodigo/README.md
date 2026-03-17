# Guía de uso: `src/futbolycodigo`

Referencia práctica de los tres módulos de infraestructura del repositorio. El objetivo es que
cualquier notebook arranque en menos de diez líneas y produzca visualizaciones con estilo
consistente sin repetir configuración.

---

## Setup inicial (siempre en la primera celda)

```python
from futbolycodigo.branding import apply_style, watermark, COLORS
from futbolycodigo.data_loaders import get_match_events, get_competition_matches, get_season_events
from futbolycodigo.viz_utils import create_pitch, add_title, plot_heatmap

apply_style()  # aplica el tema FyC globalmente a matplotlib
```

`apply_style()` configura `plt.rcParams` una sola vez: fondos, colores de texto, DPI de pantalla
(150) y de exportación (200). Cualquier figura creada después hereda automáticamente el estilo.

---

## `branding` — identidad visual

### Constantes

```python
from futbolycodigo.branding import BLOG_NAME, BLOG_URL, AUTHOR, COLORS

print(BLOG_NAME)  # "Fútbol y Código"
print(BLOG_URL)   # "https://futbolycodigo.com"
print(AUTHOR)     # "Juanje Márquez"
```

`COLORS` es el diccionario de paleta:

| Clave          | Valor     | Uso                              |
| -------------- | --------- | -------------------------------- |
| `"primary"`    | `#1A472A` | Títulos, elementos principales   |
| `"secondary"`  | `#4a7c59` | Watermark, elementos secundarios |
| `"accent"`     | `#D4AF37` | Destacados, anotaciones          |
| `"background"` | `#FAFAFA` | Fondo de figuras y ejes          |
| `"text"`       | `#333333` | Texto general                    |
| `"grid"`       | `#E0E0E0` | Líneas del campo, bordes         |

### `apply_style()`

```python
apply_style()
```

Llama a esto **una vez al inicio del notebook**, antes de crear cualquier figura. Configura:

- Fondo de figuras y ejes: `COLORS["background"]`
- Color de texto, ticks y etiquetas: `COLORS["text"]`
- `font.size = 11`, `figure.dpi = 150`, `savefig.dpi = 200`, `savefig.bbox = "tight"`

### `watermark(fig)`

```python
fig = plot_heatmap(x, y, title="Pedri — Acciones")
watermark(fig)  # añade "https://futbolycodigo.com · Juanje Márquez" en la esquina inferior derecha
```

Añade un footer discreto (`fontsize=7`, `alpha=0.6`) útil cuando exportas la figura para el blog.

---

## `data_loaders` — carga de datos con caché

Todos los datos vienen de **StatsBomb Open Data** (gratuito, sin autenticación).
La caché local evita descargas repetidas: los archivos parquet se guardan en `data/.cache/`.

### IDs de referencia útiles

| Competición      | `competition_id` | Temporada | `season_id` |
| ---------------- | ---------------- | --------- | ----------- |
| UEFA Euro 2020   | `55`             | 2020      | `43`        |
| La Liga          | `11`             | 2015/16   | `26`        |
| La Liga          | `11`             | 2020/21   | `90`        |
| Premier League   | `2`              | 2003/04   | `44`        |
| Champions League | `16`             | 2021/22   | `106`       |
| FIFA World Cup   | `43`             | 2022      | `106`       |

> Para ver todas las competiciones disponibles: `from statsbombpy import sb; sb.competitions()`

### `get_competition_matches(competition_id, season_id)`

```python
matches = get_competition_matches(55, 43)  # UEFA Euro 2020

matches.head(3)[["match_id", "match_date", "home_team", "away_team", "home_score", "away_score"]]
```

Devuelve un DataFrame con todos los partidos de la competición/temporada.
La caché se guarda en `data/.cache/matches_55_43.parquet`.

### `get_match_events(match_id)`

```python
matches = get_competition_matches(55, 43)
match_id = matches["match_id"].iloc[0]

events = get_match_events(match_id)
print(events["type"].value_counts().head(10))
```

Devuelve todos los eventos del partido (pases, tiros, regates, etc.) en formato StatsBomb.
La caché se guarda en `data/.cache/events_{match_id}.parquet`.

**Segunda llamada — sin red:**

```python
# Misma llamada, lee de data/.cache/ sin HTTP request
events = get_match_events(match_id)
```

**Parámetros opcionales:**

```python
# Desactivar caché (útil en exploración puntual)
events = get_match_events(match_id, cache=False)

# Forzar re-descarga aunque exista caché (p.ej. si StatsBomb actualiza los datos)
events = get_match_events(match_id, force_refresh=True)
```

| `cache` | `force_refresh` | Comportamiento                       |
| ------- | --------------- | ------------------------------------ |
| `True`  | `False`         | Lee caché si existe; descarga si no  |
| `True`  | `True`          | Siempre descarga; sobreescribe caché |
| `False` | `False`         | Siempre descarga; no lee ni escribe  |

### `get_season_events(competition_id, season_id)`

```python
# Carga TODOS los eventos de la temporada (pesado en primera ejecución)
all_events = get_season_events(55, 43)

# Filtrar por tipo
passes = all_events[all_events["type"] == "Pass"]
print(f"Total pases en la Euro 2020: {len(passes):,}")
```

Llama a `get_match_events(..., cache=True)` por cada partido. La primera ejecución descarga
todos los partidos; las siguientes son rápidas porque leen de caché.

> **Aviso:** la Euro 2020 tiene 51 partidos × ~3.000 eventos = ~150.000 filas. Espera
> 1-2 minutos en la primera ejecución.

---

## `viz_utils` — visualizaciones sobre el campo

### `create_pitch(orientation, *, half, figsize)`

Crea un campo de fútbol con estilo FyC listo para añadir capas encima.

```python
# Campo completo horizontal (default)
fig, ax, pitch = create_pitch()

# Campo vertical (ideal para análisis de zona de ataque)
fig, ax, pitch = create_pitch(orientation="vertical")

# Medio campo horizontal
fig, ax, pitch = create_pitch(half=True)

# Tamaño personalizado
fig, ax, pitch = create_pitch(figsize=(16, 10))
```

Devuelve `(fig, ax, pitch)` donde `pitch` es el objeto mplsoccer — necesario para usar sus
métodos de dibujo (`pitch.scatter`, `pitch.arrows`, `pitch.kdeplot`, etc.).

**Tamaños por defecto:**

- Horizontal: `(12, 8)`
- Vertical: `(8, 12)`

### `add_title(fig, title, subtitle="")`

```python
fig, ax, pitch = create_pitch()

# Solo título
add_title(fig, "Mapa de pases — España vs Croatia")

# Título + subtítulo
add_title(fig, "Mapa de pases — España vs Croatia", "UEFA Euro 2020 · Fase de grupos")
```

Añade texto al `Figure` (no al `Axes`), por encima del campo. El título usa `COLORS["primary"]`
en negrita; el subtítulo usa `COLORS["text"]` en cursiva.

### `plot_heatmap(x, y, *, title, subtitle, orientation, cmap)`

Atajo de alto nivel: crea el campo y dibuja un KDE heatmap en una sola llamada.

```python
# Heatmap de posiciones de Pedri
pedri_events = events[events["player"] == "Pedro González López"]
x = pedri_events["location"].apply(lambda loc: loc[0])
y = pedri_events["location"].apply(lambda loc: loc[1])

fig = plot_heatmap(
    x, y,
    title="Pedri — Mapa de acciones",
    subtitle="Euro 2020 · España",
)
watermark(fig)
fig.savefig("pedri_heatmap.png")
```

**Parámetros:**

| Parámetro     | Default      | Descripción                       |
| ------------- | ------------ | --------------------------------- |
| `x`, `y`      | —            | Coordenadas en unidades StatsBomb |
| `title`       | `""`         | Título (vacío = sin título)       |
| `subtitle`    | `""`         | Subtítulo opcional                |
| `orientation` | `"vertical"` | `"horizontal"` o `"vertical"`     |
| `cmap`        | `"Greens"`   | Cualquier colormap de matplotlib  |

---

## Workflow completo de ejemplo

```python
# ── Celda 1: Setup ───────────────────────────────────────────────────────────
from futbolycodigo.branding import apply_style, watermark
from futbolycodigo.data_loaders import get_competition_matches, get_match_events
from futbolycodigo.viz_utils import create_pitch, add_title, plot_heatmap

apply_style()

# ── Celda 2: Carga de datos ───────────────────────────────────────────────────
matches = get_competition_matches(55, 43)  # Euro 2020
match_id = matches.loc[matches["home_team"] == "Spain", "match_id"].iloc[0]
events = get_match_events(match_id)

# ── Celda 3: Filtrar acciones de un jugador ───────────────────────────────────
pedri = events[events["player"] == "Pedro González López"].copy()
x = pedri["location"].apply(lambda loc: loc[0])
y = pedri["location"].apply(lambda loc: loc[1])

# ── Celda 4: Heatmap de alto nivel ────────────────────────────────────────────
fig = plot_heatmap(
    x, y,
    title="Pedri — Mapa de acciones",
    subtitle=f"España vs {matches.loc[matches['match_id'] == match_id, 'away_team'].iloc[0]} · Euro 2020",
)
watermark(fig)

# ── Celda 5: Personalización manual ──────────────────────────────────────────
# Si necesitas más control, usa create_pitch directamente:
fig, ax, pitch = create_pitch(orientation="vertical")
pitch.scatter(x, y, ax=ax, s=20, color=watermark.__module__ and "#D4AF37", zorder=4)
add_title(fig, "Pedri — Dispersión de acciones")
watermark(fig)
```

---

## Organización de la caché

```text
data/
└── .cache/
    ├── matches_55_43.parquet          # get_competition_matches(55, 43)
    ├── events_3794685.parquet         # get_match_events(3794685)
    ├── events_3794686.parquet
    └── ...
```

Los archivos parquet están en `.gitignore` (`data/**/*.parquet`). Para limpiar la caché:

```bash
rm -rf data/.cache/
```

O para invalidar un partido concreto:

```python
get_match_events(match_id, force_refresh=True)
```
