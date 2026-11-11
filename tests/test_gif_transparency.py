# -*- coding: utf-8 -*-

# Regression test for thumbor#1886: a resized palette GIF loses its
# transparent background when PILLOW_PRESERVE_INDEXED_MODE is on.

from io import BytesIO

from PIL import Image

from thumbor.config import Config
from thumbor.context import Context
from thumbor.engines.pil import Engine


def make_engine():
    cfg = Config(
        SECURITY_KEY="ACME-SEC",
        ENGINE="thumbor.engines.pil",
        PILLOW_PRESERVE_INDEXED_MODE=True,
    )
    cfg.LOADER = "thumbor.loaders.file_loader"
    cfg.STORAGE = "thumbor.storages.no_storage"
    return Engine(Context(config=cfg))


def make_palette_gif():
    # Palette GIF: index 0 is fully transparent (the background),
    # index 1 is blue (the disc in the middle).
    img = Image.new("P", (80, 60), 0)
    img.putpalette([255, 255, 255, 0, 0, 255] + [0, 0, 0] * 254)
    img.paste(1, (20, 15, 60, 45))
    buf = BytesIO()
    img.save(buf, "GIF", transparency=0)
    return buf.getvalue()


def test_resized_palette_gif_keeps_transparent_background():
    engine = make_engine()
    engine.load(make_palette_gif(), ".gif")
    assert engine.original_mode == "P"

    engine.resize(160, 120)
    out = Image.open(BytesIO(engine.read(".gif")))

    assert out.format == "GIF"
    assert out.info.get("transparency") is not None

    alpha = out.convert("RGBA").getchannel("A")
    # Pixels that were transparent in the source must still be transparent
    assert alpha.histogram()[0] > 0
