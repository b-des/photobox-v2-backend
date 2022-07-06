from PIL import Image
import smartcrop

from photobox import utils
from photobox.models.Area import Area
from photobox.models.Size import Size


class Cropper:

    @staticmethod
    def crop(image: Image, crop_data: Area):

        x, y, w, h = round(crop_data.x), round(crop_data.y), round(crop_data.width), round(crop_data.height)

        w = round(image.width / 100 * (w + x))
        h = round(image.height / 100 * (h + y))
        x = round(image.width / 100 * x)
        y = round(image.height / 100 * y)
        image = image.crop((x, y, w, h))
        return image

    @staticmethod
    def resize(image: Image, size: Size):
        if min(int(size.width), int(size.height)) > 300:
            multiplier = 2
        else:
            multiplier = 5

        width = utils.to_pixel(size.width, multiplier)
        height = utils.to_pixel(size.height, multiplier)

        image = image.resize((width, height))
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

        return image.crop((x, y, x + width, y + height))

    @staticmethod
    def fit_to_container(image: Image, size: Size, fill_white_space: bool = False, rotate: bool = False):
        width = utils.to_pixel(size.width, 5)
        height = utils.to_pixel(size.height, 5)

        if image.width > image.height and not rotate:
            image = image.transpose(Image.Transpose.ROTATE_270)

        if rotate:
            image = image.transpose(Image.Transpose.ROTATE_270)

        # resize image by largest side keeping aspect ratio
        if image.height / image.width < height / width:
            image = image.resize((width, int(width / image.width * image.height)))
        elif image.height / image.width > height / width:
            image = image.resize((int(height / image.height * image.width), height))
        else:
            image = image.resize((width, height))

        # create new image with given size
        blank_image = Image.new('RGB', (width, height), (255, 255, 255))

        # set blured image as background(fill white space)
        if fill_white_space:
            blank_image.paste(utils.create_blur(image, height).resize((width, height)))

        # put resized image to image container
        blank_image.paste(image, (int((blank_image.width - image.width) / 2),
                                int((blank_image.height - image.height) / 2)))
        img = blank_image
        return blank_image

