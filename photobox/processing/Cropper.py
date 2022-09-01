from PIL import Image
import smartcrop

from photobox import utils
from photobox.models.Area import Area
from photobox.models.FrameType import FrameType
from photobox.models.ImagePayload import ImagePayload
from photobox.models.Size import Size


class Cropper:

    @staticmethod
    def crop(image: Image, crop_data: Area, size: Size):
        x, y, w, h = crop_data.x, crop_data.y, crop_data.width, crop_data.height

        # transform percents to pixels
        w = round(image.width / 100 * (w + x))
        h = round(image.height / 100 * (h + y))
        x = round(image.width / 100 * x)
        y = round(image.height / 100 * y)

        image = image.crop((x, y, w, h))
        image = Cropper.resize(image, size)
        return image

    @staticmethod
    def resize(image: Image, size: Size):
        width = utils.to_pixel(size.width)
        height = utils.to_pixel(size.height)

        # resize image by largest side keeping aspect ratio
        if image.width > image.height:
            image = image.resize((height, width), Image.ANTIALIAS)
        else:
            image = image.resize((width, height), Image.ANTIALIAS)
        return image

    @staticmethod
    def auto_crop_best_frame(image: Image, size: Size):
        sc = smartcrop.SmartCrop()
        # switch to horizontal mode in case when image width bigger than image height
        if image.width > image.height:
            result = sc.crop(image, size.height, size.width)
        else:
            result = sc.crop(image, size.width, size.height)
        x, y, width, height = result['top_crop']['x'], result['top_crop']['y'], \
                              result['top_crop']['width'], result['top_crop']['height']

        return Cropper.resize(image.crop((x, y, x + width, y + height)), size)

    @staticmethod
    def fit_to_container(cropper_data: ImagePayload):
        frame_thickness = 0

        # use frame wight from reqeust only for solid or polaroid frame types
        if cropper_data.frame.type == FrameType.SOLID or cropper_data.frame.type == FrameType.POLAROID:
            frame_thickness = cropper_data.frame.thickness

        width = utils.to_pixel(cropper_data.size.width - frame_thickness * 2)
        height = utils.to_pixel(cropper_data.size.height - frame_thickness * 2)

        print(width / height)
        print(cropper_data.size.width / cropper_data.size.height)
        image = cropper_data.image

        if image.width > image.height and not cropper_data.rotate:
            image = image.transpose(Image.Transpose.ROTATE_270)

        if cropper_data.rotate:
            image = image.transpose(Image.Transpose.ROTATE_270)

        # resize image by largest side keeping aspect ratio
        if image.height / image.width < height / width:
            image = image.resize((width, int(width / image.width * image.height)), Image.ANTIALIAS)
        elif image.height / image.width > height / width:
            image = image.resize((int(height / image.height * image.width), height), Image.ANTIALIAS)
        else:
            image = image.resize((width, height), Image.ANTIALIAS)

        # create new image with given size
        blank_image = Image.new('RGB', (width, height), (255, 255, 255))

        # set blured image as background(fill white space)
        if cropper_data.detect_and_fill_with_gradient:
            blank_image.paste(utils.create_blur(image, height).resize((width, height)))

        # put resized image to image container
        blank_image.paste(image, (int((blank_image.width - image.width) / 2),
                                  int((blank_image.height - image.height) / 2)))
        img = blank_image
        return blank_image
