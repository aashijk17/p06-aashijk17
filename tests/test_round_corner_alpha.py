# -*- coding: utf-8 -*-

# thumbor imaging service
# https://github.com/thumbor/thumbor/wiki

# Licensed under the MIT license:
# http://www.opensource.org/licenses/mit-license
# Copyright (c) 2011 globo.com thumbor@googlegroups.com

from tornado.testing import gen_test

from tests.base import FilterTestCase


class RoundCornerAlphaEdgeTestCase(FilterTestCase):
    @gen_test
    async def test_round_corner_transparent_edge_is_smoothed_through_alpha(
        self,
    ):
        image = await self.get_filtered(
            "source.jpg",
            "thumbor.filters.round_corner",
            "round_corner(50,255,0,0,1)",
            mode="RGBA",
        )

        # The top-left corner arc lies inside the 50x50 square. Pixels on
        # the arc should be partly transparent so the edge blends into the
        # background. Today the arc pixels are fully opaque, so no alpha
        # value falls between 0 and 255.
        alphas = {
            image.getpixel((x, y))[3] for x in range(50) for y in range(50)
        }
        assert any(0 < a < 255 for a in alphas)
