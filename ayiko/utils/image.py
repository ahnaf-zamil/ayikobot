from PIL import Image, ImageDraw, ImageChops
from io import BytesIO


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

        border = Image.new("RGBA", (138, 138), (255, 255, 255))
        cls.crop_to_circle(border)

        border.paste(avatar, (5, 5), avatar)
        return border
