import logging
import os
import random
import string
from io import BytesIO
from urllib.parse import urlparse

import requests
from PIL import Image

from photobox import config
from photobox.models.FrameType import FrameType
from photobox.models.ImagePayload import ImagePayload
from photobox.models.PrintMode import PrintMode
from photobox.processing.Color import Color
from photobox.processing.Cropper import Cropper
from photobox.processing.Frame import Frame

logger = logging.getLogger()


class Render:
    def __init__(self, images: [ImagePayload], os_path: str):
        self.os_path = os_path
        self.images = images

    def start(self):
        for i, item in enumerate(self.images):
            logger.info(f"Processing image {i + 1}/{len(self.images)}...")
            try:
                self.process(item)
            except Exception as e:
                logger.error(f"Exception during rendering images: {e}")
            logger.info(f"Image {i + 1}/{len(self.images)} processed")

        logger.info(f"All images have been processed: {len(self.images)}")

    def process(self, image_data: ImagePayload):
        if config.APP_ENV == "development":
            logger.info(f"Read file from url: {image_data.src.full}")
            response = requests.get(image_data.src.full)
            input_file = BytesIO(response.content)
        else:
            logger.info(f"OS PATH: {self.os_path}")
            input_file = os.path.join("/var/www/demonstration/data/www/pechat.photo/", urlparse(image_data.src.full).path)
            logger.info(f"Read file from path: {input_file}")
        with Image.open(input_file) as image:
            image_data.image = image
            # adjust image color
            image_data.image = self.adjust_color(image_data)
            image_data.image = self.resize(image_data)
            image_data.image = self.draw_border(image_data)

            original_filename = os.path.basename(image_data.src.full)
            salt = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            file = f"{original_filename}-{salt}-{image_data.size.width}-{image_data.size.height}.jpg"

            path = os.path.join(self.os_path, image_data.target_path)
            file_path = os.path.join(path, file)

            logger.info(f"Save image as {file_path}")
            if not os.path.exists(path):
                logger.info(f"Path doesn't exist, creating one: {path}")
                os.makedirs(path)
            image_data.image.save(file_path, "JPEG", dpi=(600, 600))

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
                    f"crop data: {image_data.crop_data_for_render}, "
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
            # if crop data is present
            # crop using it, otherwise perform auto crop
            if image_data.crop_data_for_render:
                return Cropper.crop(image_data.image, image_data.crop_data_for_render, image_data.size)
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
    def enhance_color(os_path: str, url: str):
        response = requests.get(url)
        input_file = BytesIO(response.content)
        with Image.open(input_file) as image:
            image = Color.auto_contrast(image)

            filename = os.path.basename(url)
            relative_path = "image/photobox/uploads/"
            file_path = f"{os_path}{relative_path}{filename}"
            image.save(file_path)
            return f"/{relative_path}{filename}"


