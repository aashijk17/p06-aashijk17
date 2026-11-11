# -*- coding: utf-8 -*-

from io import BytesIO
from os.path import abspath, dirname, join

from PIL import Image
from tornado.testing import gen_test

from tests.handlers.test_base_handler import BaseImagingTestCase
from thumbor.config import Config
from thumbor.context import Context, ServerParameters
from thumbor.importer import Importer


class ExtremeAspectCropTestCase(BaseImagingTestCase):
    def get_context(self):
        cfg = Config(SECURITY_KEY="ACME-SEC")
        cfg.LOADER = "thumbor.loaders.file_loader"
        cfg.FILE_LOADER_ROOT_PATH = abspath(
            join(dirname(__file__), "../course/images")
        )
        cfg.STORAGE = "thumbor.storages.file_storage"
        cfg.FILE_STORAGE_ROOT_PATH = self.root_path
        cfg.QUALITY = "keep"

        importer = Importer(cfg)
        importer.import_modules()
        server = ServerParameters(
            8889, "localhost", "thumbor.conf", None, "info", None
        )
        server.security_key = "ACME-SEC"
        return Context(server, cfg, importer)

    @gen_test
    async def test_wide_short_resize_is_not_empty(self):
        response = await self.async_fetch("/unsafe/800x20/rainbow.png")
        assert response.code == 200
        image = Image.open(BytesIO(response.body)).convert("RGBA")
        assert image.size == (800, 20)
        # The issue reports every pixel as fully transparent.
        assert image.getchannel("A").getextrema()[1] > 0
