from PIL import Image, ImageOps, ImageDraw

from photobox.utils import utils
from photobox.models.FrameOptions import FrameOptions


class Frame:
    @staticmethod
    def draw_solid_border(image: Image, frame: FrameOptions):
        thickness = utils.to_pixel(frame.thickness)
        image = ImageOps.expand(image, border=thickness, fill=frame.color)
        return image

    @staticmethod
    def draw_lumber_frame(image: Image, color: str = "white"):
        offset = image.height / 100 * 2
        width = utils.to_pixel(1, 2)
        # create draw image
        draw = ImageDraw.Draw(image)
        # left line
        draw.line([(offset, 0), (offset, image.height)], fill=color, width=width)
        # top line
        draw.line([(0, offset), (image.width, offset)], fill=color, width=width)
        # right line
        draw.line([(image.width - offset, 0), (image.width - offset, image.height)], fill=color, width=width)
        # bottom line
        draw.line([(0, image.height - offset), (image.width, image.height - offset)], fill=color, width=width)
        return image

    @staticmethod
    def draw_zebra_frame(image: Image, color: str = "white", offset: int = 50):
        offset = image.height / 100 * 2
        width = utils.to_pixel(1, 2)
        # create draw image
        draw = ImageDraw.Draw(image, "RGBA")
        draw.rectangle(((offset, offset), (image.width - offset, image.height - offset)), outline=color,
                       fill=(255, 255, 255, 0), width=width)
        offset = offset + 50
        draw.rectangle(((offset, offset), (image.width - offset, image.height - offset)), outline=color,
                       fill=(255, 255, 255, 0), width=width)
        return image

    @staticmethod
    def draw_hook_frame(image: Image, color: str = "white", length: int = 50):
        offset = image.height / 100 * 2
        length = image.height / 100 * 5
        width = utils.to_pixel(1, 2)
        # create draw image
        draw = ImageDraw.Draw(image)
        # top-left corner
        # top line
        draw.line([(offset, offset), (offset + length, offset)], fill=color, width=width)
        # left line
        draw.line([(offset, offset), (offset, offset + length)], fill=color, width=width)

        # top-right corner
        # top line
        draw.line([(image.width - offset, offset), (image.width - offset - length, offset)], fill=color, width=width)
        # right line
        draw.line([(image.width - offset, offset), (image.width - offset, offset + length)], fill=color, width=width)

        # bottom-right corner
        # right line
        draw.line([(image.width - offset, image.height - offset), (image.width - offset, image.height - offset - length)],
                  fill=color, width=width)
        # bottom line
        draw.line([(image.width - offset, image.height - offset), (image.width - offset - length, image.height - offset)],
                  fill=color, width=width)

        # bottom-left corner
        # left line
        draw.line([(offset, image.height - offset), (offset, image.height - offset - length)], fill=color, width=width)
        # bottom line
        draw.line([(offset, image.height - offset), (offset + length, image.height - offset)], fill=color, width=width)

        return image

    @staticmethod
    def draw_polaroid_frame(image: Image, color: str = "white"):
        # create draw image
        draw = ImageDraw.Draw(image, "RGBA")
        offset = 100
        width = utils.to_pixel(1, 2)
        width = int(image.height / 100 * 2)
        thickness = utils.to_pixel(5)
        bottom_rectangle_height = thickness * 3
        # bottom line
        draw.rectangle(
            ((0, image.height - bottom_rectangle_height), (image.width, image.height)),
            fill=color)

        # general polaroid frame
       # draw.rectangle(((offset, offset), (image.width - offset, image.height - offset)),
       #                outline=color, fill=(255, 255, 255, 0), width=width)
       # image = image.crop((offset, offset, image.width - offset, image.height - offset))

        image = ImageOps.expand(image, border=thickness, fill=color)
        return image

