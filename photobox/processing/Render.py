import io
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
                logger.info(f"Image {i + 1}/{len(self.images)} processed")
            except Exception as e:
                logger.error(f"Exception during rendering image: {item.src.full}, message: {e}", e)

        logger.info(f"All images have been processed: {len(self.images)}")

    def process(self, image_data: ImagePayload):
        image_data.image = self.open_image(self.os_path, image_data.src.full)
        #original_aspect = image_data.size.height / image_data.size.width
        if image_data.image.mode != "RGB":
            logger.info(f"Image mode is {image_data.image.mode}, converting to RGB")
            image_data.image = image_data.image.convert('RGB')
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
        #logger.info(f"Aspect ratio of the final image is: {   image_data.image.height / image_data.image.width}, required: {original_aspect}")
        if not os.path.exists(path):
            logger.info(f"Path doesn't exist, creating one: {path}")
            os.makedirs(path)
        image_data.image.convert("RGB").save(file_path, "JPEG", dpi=(600, 600))

    @staticmethod
    def open_image(full_path, src):
        if config.APP_ENV == "development":
            logger.info(f"Read file from url: {src}")
            response = requests.get(src)
            input_file = BytesIO(response.content)
            return Image.open(input_file)
        else:
            logger.info(f"OS PATH: {full_path}")
            file_path = urlparse(src).path.strip("/")
            input_file = os.path.join(full_path, file_path)
            logger.info(f"Read file from path: {input_file}")
            f = open(input_file, "rb")
            b = io.BytesIO(f.read())
            return Image.open(b)

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
            return Cropper.fit_to_container(image_data)

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
        is_crop_mode = image_data.image_print_mode == PrintMode.CROP
        if frame.type == FrameType.SOLID:
            return Frame.draw_solid_border(image_data.image, frame, is_crop_mode)
        elif frame.type == FrameType.ZEBRA:
            return Frame.draw_zebra_frame(image_data.image, frame.color)
        elif frame.type == FrameType.HOOK:
            return Frame.draw_hook_frame(image_data.image, frame.color)
        elif frame.type == FrameType.LUMBER:
            return Frame.draw_lumber_frame(image_data.image, frame.color)
        elif frame.type == FrameType.POLAROID:
            return Frame.draw_polaroid_frame(image_data.image, frame, is_crop_mode)

        return image_data.image

    @staticmethod
    def enhance_color(os_path: str, url: str):
        image = Render.open_image(os_path, url)
        image = Color.auto_contrast(image)
        filename = os.path.basename(url)
        relative_path = "image/photobox/uploads/"
        file_path = f"{os_path}{relative_path}{filename}"
        image.save(file_path)
        return f"/{relative_path}{filename}"


