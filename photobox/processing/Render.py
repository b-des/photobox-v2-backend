import logging
from io import BytesIO
import requests
from PIL import Image

from photobox import config
from photobox.processing.Color import Color
from photobox.processing.Cropper import Cropper
from photobox.processing.Frame import Frame
from photobox.models.FrameType import FrameType
from photobox.models.ImagePayload import ImagePayload
from photobox.models.PrintMode import PrintMode

logger = logging.getLogger()


class Render:
    def __init__(self, images: [ImagePayload], image_path: str):
        self.image_path = image_path
        self.images = images

    def start(self):
        for i, item in enumerate(self.images):
            logger.info(f"Processing image {i + 1}/{len(self.images)}...")
            self.process(item)
            logger.info(f"Image {i + 1}/{len(self.images)} processed")

    def process(self, image_data: ImagePayload):
        response = requests.get(image_data.src.full)
        input_file = BytesIO(response.content)
        with Image.open(input_file) as image:
            image_data.image = image
            # adjust image color
            image_data.image = self.adjust_color(image_data)
            image_data.image = self.resize(image_data)
            image_data.image = self.draw_border(image_data)
            final_path = f"{self.image_path}/res.jpg"
            logger.info(f"Save image as {final_path}")
            image_data.image.save(f"{final_path}")

    @staticmethod
    def adjust_color(image_data: ImagePayload):
        logger.info(f"Adjust color, auto: {image_data.auto_color_enhance}, settings: {image_data.color_adjustment}")
        if image_data.auto_color_enhance:
            return Color.auto_contrast(image_data.image)

        return Color.adjust_color(image_data.image, image_data.color_adjustment)

    @staticmethod
    def resize(image_data: ImagePayload):
        logger.info(f"Resize image according to format. Mode: {image_data.image_print_mode}, "
                    f"format: {image_data.size}, "
                    f"crop data: {image_data.crop_data}, "
                    f"fill background: {image_data.detect_and_fill_with_gradient}, rotation: {image_data.rotate}")
        # fit to container if full mode has been chosen
        if image_data.image_print_mode == PrintMode.FULL:
            return Cropper.fit_to_container(
                image_data.image,
                image_data.size,
                image_data.detect_and_fill_with_gradient,
                bool(image_data.rotate)
            )

        # crop image
        if image_data.image_print_mode == PrintMode.CROP:
            # if crop models is present
            # crop using it, otherwise perform auto crop
            if image_data.crop_data:
                return Cropper.crop(image_data.image, image_data.crop_data)
            else:
                return Cropper.auto_crop_best_frame(image_data.image, image_data.size)

    @staticmethod
    def draw_border(image_data: ImagePayload):
        frame = image_data.frame
        logger.info(f"Draw border, type: {frame.type}, color: {frame.color}, width: {frame.thickness}")
        if frame.type == FrameType.SOLID:
            return Frame.draw_solid_border(image_data.image, frame)
        elif frame.type == FrameType.ZEBRA:
            return Frame.draw_zebra_frame(image_data.image, frame.color)
        elif frame.type == FrameType.HOOK:
            return Frame.draw_hook_frame(image_data.image, frame.color)
        elif frame.type == FrameType.LUMBER:
            return Frame.draw_lumber_frame(image_data.image, frame.color)
        elif frame.type == FrameType.POLAROID:
            return Frame.draw_polaroid_frame(image_data.image, frame.color)

        return image_data.image

    @staticmethod
    def enhance_color(image_path: str, url: str, host: str):
        response = requests.get(url)
        input_file = BytesIO(response.content)
        with Image.open(input_file) as image:
            image = Color.auto_contrast(image)
            filename = "color.jpg"
            file_path = f"{image_path}image/photobox/uploads/{filename}"
            image.save(file_path)
            return file_path


