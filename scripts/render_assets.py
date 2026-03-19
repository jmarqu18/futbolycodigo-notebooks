"""Convierte los SVGs de assets/ a PNGs para uso en matplotlib.

Ejecutar una vez:  uv run python scripts/render_assets.py
"""

from pathlib import Path

from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

ASSETS_DIR = Path(__file__).parent.parent / "src" / "futbolycodigo" / "assets"

# Configuración: (nombre_svg, ancho_px_salida)
TARGETS = [
    ("logo_thin_1.svg", 300),
    ("logo_thin_1.svg", 600),
    ("logo_mono.svg", 300),
    ("isotipo_1_tinta_1.svg", 150),
    ("isotipo_1_tinta_2.svg", 150),
]


def convert_svg_to_png(svg_path: Path, output_width: int) -> Path:
    """Convierte un SVG a PNG con el ancho indicado, manteniendo proporciones."""
    drawing = svg2rlg(str(svg_path))
    if drawing is None:
        raise ValueError(f"No se pudo parsear {svg_path}")

    scale = output_width / drawing.width
    drawing.width = output_width
    drawing.height = drawing.height * scale
    drawing.scale(scale, scale)

    stem = svg_path.stem
    out_path = svg_path.parent / f"{stem}_{output_width}w.png"
    renderPM.drawToFile(drawing, str(out_path), fmt="PNG", dpi=150)
    return out_path


def main() -> None:
    for svg_name, width in TARGETS:
        svg_path = ASSETS_DIR / svg_name
        if not svg_path.exists():
            print(f"  SKIP {svg_name} (no encontrado)")
            continue
        out = convert_svg_to_png(svg_path, width)
        print(f"  OK   {out.name} ({width}px)")


if __name__ == "__main__":
    main()
