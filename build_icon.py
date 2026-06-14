"""Génère l'icône Windows de l'application."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def build_icon():
    output = Path("assets") / "avicole_pro.ico"
    output.parent.mkdir(parents=True, exist_ok=True)

    size = 256
    image = Image.new("RGBA", (size, size), "#0B1F33")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(
        (16, 16, size - 16, size - 16),
        radius=42,
        fill="#123B5D",
        outline="#C9A227",
        width=12,
    )
    draw.rounded_rectangle(
        (52, 52, size - 52, size - 52),
        radius=28,
        fill="#C9A227",
    )

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/seguisb.ttf", 76)
    except OSError:
        font = ImageFont.load_default()

    text = "AP"
    box = draw.textbbox((0, 0), text, font=font)
    x = (size - (box[2] - box[0])) / 2
    y = (size - (box[3] - box[1])) / 2 - box[1]
    draw.text((x, y), text, font=font, fill="#0B1F33")
    image.save(
        output,
        format="ICO",
        sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (256, 256)],
    )
    print(output.resolve())


if __name__ == "__main__":
    build_icon()
