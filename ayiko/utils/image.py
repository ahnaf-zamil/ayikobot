# Copyright (C) 2021 K.M Ahnaf Zamil

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from PIL import Image, ImageDraw, ImageChops, ImageFont
from io import BytesIO

import hikari
import typing


class ImageUtils:
    @staticmethod
    def crop_to_circle(im):
        bigsize = (im.size[0] * 3, im.size[1] * 3)
        mask = Image.new("L", bigsize, 0)
        ImageDraw.Draw(mask).ellipse((0, 0) + bigsize, fill=255)
        mask = mask.resize(im.size, Image.ANTIALIAS)
        mask = ImageChops.darker(mask, im.split()[-1])
        im.putalpha(mask)

    @classmethod
    def get_circle_img(cls, avatar) -> Image:
        data = BytesIO(avatar)
        avatar = Image.open(data)
        cls.crop_to_circle(avatar)
        avatar = avatar.resize((128, 128), Image.ANTIALIAS).convert("RGBA")
        return avatar

    @classmethod
    def create_rank_card(
        cls,
        avatar: Image,
        user: hikari.Member,
        icon: Image,
        rank: int,
        current_level: int,
        coords: typing.List[tuple],
        xp_text: str,
    ) -> Image:
        bg = Image.open("ayiko/resources/img/stats_bg.png").convert("RGBA")
        bg.paste(avatar, (36, 36), avatar)

        draw = ImageDraw.Draw(bg)

        # Drawing the author's username
        font = ImageFont.truetype(
            "ayiko/resources/font/Asap-SemiBold.ttf", int(450 / len(str(user)) - 1)
        )
        draw.text((210, 31), str(user), (255, 255, 255), font=font)

        # Drawing the server icon
        icon = icon.resize((50, 50), Image.ANTIALIAS)
        bg.paste(icon, (630, 35), icon)

        # Drawing the server rank
        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 60)
        draw.text((210, 100), f"#{rank}", (164, 165, 166), font=font)

        # Drawing the level
        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 30)
        draw.text((517, 42), f"Level {current_level}", "white", font=font)

        rectangle_color = (89, 172, 255)

        rectangle_base = Image.new("RGBA", bg.size, "white")
        d = ImageDraw.Draw(rectangle_base)
        d.rectangle(coords, rectangle_color)
        rectangle_base.paste(bg, (0, 0), bg)
        bg = rectangle_base

        # Drawing the XP ratio on top of XP bar
        draw = ImageDraw.Draw(bg)
        font = ImageFont.truetype("ayiko/resources/font/Asap-SemiBold.ttf", 30)

        draw.text(
            (555, 122) if len(xp_text) < 8 else (545, 122),
            xp_text,
            "black",
            font=font,
            anchor="rs",
        )

        return bg
