import os

from PIL import Image, ImageDraw, ImageOps, ImageEnhance, ImageFilter
import requests
from io import BytesIO
import smartcrop

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
from photobox.processing.Cropper import Cropper
from photobox.processing.Frame import FrameOptions
from photobox.utils import to_pixel
from photobox.models.ImagePayload import ImagePayload
from urllib.parse import urlparse

def print_hi(name):
    json = '[{"colorAdjustment":{"saturation":0,"brightness":1,"contrast":1},"cropData":{"x":141.68524590163935,"y":0,"width":225.62950819672133,"height":339,"rotate":0},"canvasData":null,"detectAndFillWithGradient":false,"frame":{"color":"#ffffff","thickness":5,"type":"solid"},"imagePrintMode":"FULL","selectedOptions":[{"option_id":"9","option_value_id":"20","checked":true},{"option_id":"11","option_value_id":"32","checked":true},{"option_id":"79","option_value_id":"329","checked":true},{"option_id":"82","option_value_id":"341","checked":true}],"quantity":1,"rotate":0,"size":{"height":152,"width":102},"src":{"thumbnail":"./img/1-thumbnail.jpg","full":"./img/1-thumbnail.jpg","adjusted":"./img/1-thumbnail.jpg"},"zoom":0,"autoColorEnhance":false,"autoDetectBestFrame":true,"resolution":"400x500"},{"colorAdjustment":{"saturation":1,"brightness":1.2,"contrast":1},"cropData":{"x":72,"y":24,"width":21,"height":32,"rotate":0},"canvasData":null,"detectAndFillWithGradient":false,"frame":{"color":"#ffffff","thickness":5,"type":"solid"},"imagePrintMode":"FULL","selectedOptions":[{"option_id":"9","option_value_id":"20","checked":true},{"option_id":"11","option_value_id":"32","checked":true},{"option_id":"79","option_value_id":"329","checked":true},{"option_id":"82","option_value_id":"341","checked":true}],"quantity":1,"rotate":0,"size":{"height":152,"width":102},"src":{"thumbnail":"./img/Mona_Lisa-restored.jpg","full":"./img/Mona_Lisa-restored.jpg","adjusted":"./img/Mona_Lisa-restored.jpg"},"zoom":0,"autoColorEnhance":false,"autoDetectBestFrame":true,"resolution":"400x500"},{"colorAdjustment":{"saturation":1,"brightness":1,"contrast":1},"cropData":{"x":72,"y":24,"width":21,"height":32,"rotate":0},"canvasData":{"left":-200.87479500000018,"top":-19.741445000000105,"width":409.8747950000002,"height":272.9814450000001,"naturalWidth":509,"naturalHeight":339},"detectAndFillWithGradient":false,"frame":{"color":"#ffffff","type":"none","thickness":5},"imagePrintMode":"CROP","selectedOptions":[],"quantity":1,"rotate":0,"size":{"height":9,"width":9},"src":{"thumbnail":"./img/1-thumbnail.jpg"},"zoom":0.8052550000000004,"autoColorEnhance":false,"autoDetectBestFrame":false,"resolution":"5120x2880"},{"colorAdjustment":{"saturation":1,"brightness":1,"contrast":1},"cropData":{"x":31,"y":0,"width":67,"height":100,"rotate":0},"canvasData":null,"detectAndFillWithGradient":false,"frame":{"color":"#ffffff","type":"none","thickness":5},"imagePrintMode":"CROP","selectedOptions":[],"quantity":1,"rotate":0,"size":{"height":9,"width":9},"src":{"thumbnail":"./img/1-thumbnail.jpg","full":"./img/1-thumbnail.jpg"},"zoom":0,"autoColorEnhance":false,"autoDetectBestFrame":true,"resolution":null}]'
    image_payload: [ImagePayload] = ImagePayload.schema().loads(json, many=True)
    i: ImagePayload = image_payload[2]
    print((i.auto_color_enhance))
    url = "https://steamuserimages-a.akamaihd.net/ugc/940586530515504757/CDDE77CB810474E1C07B945E40AE4713141AFD76/?imw=5000&imh=5000&ima=fit&impolicy=Letterbox&imcolor=%23000000&letterbox=false"
    #url = "http://localhost:3000/img/Mona_Lisa-restored.jpg"
    response = requests.get(url)
    input = BytesIO(response.content)
    # input = "./public/Mona_Lisa-restored.jpg"

    with Image.open(input) as im:
        im = Cropper.fit_to_container(im, 102, 152, False)
        im = draw_solid_border(im, 5, "red")
        im.save("./public/result1.jpg")

    with Image.open("./public/1654596030680.jpg") as im:
        im = Cropper.fit_to_container(im, 102, 152, False)
        im.save("./public/result2.jpg")

    with Image.open("./public/1654596030680.jpg") as im:
        i1 = im.height
        im = Cropper.crop(im, 58, 32, 14, 32)
        im = Cropper.resize(im, 102, 152)
        i2 = im.height
        im = FrameOptions.draw_lumber_frame(im, "white", round(i2 / i1))
        im.save("./public/result3.jpg")


def find_and_crop_best_frame(image, width, height):
    sc = smartcrop.SmartCrop()
    result = sc.crop(image, width, height)
    x, y, width, height = result['top_crop']['x'], result['top_crop']['y'], \
                          result['top_crop']['width'], result['top_crop']['height']

    return image.crop((x, y, x + width, y + height))


def fit_to_container(img, width, height, rotate: bool = False):
    if img.width / img.height > 1 and not rotate:
        img = img.transpose(Image.Transpose.ROTATE_270)

    if rotate and img.width / img.height < 1:
        img = img.transpose(Image.Transpose.ROTATE_270)

    # resize image by largest side keeping aspect ratio
    if img.height / img.width < height / width:
        img = img.resize((width, int(width / img.width * img.height)))
    elif img.height / img.width > height / width:
        img = img.resize((int(height / img.height * img.width), height))
    else:
        img = img.resize((width, height))

    # create new image with given size
    blank_image = Image.new('RGB', (width, height), (255, 255, 255))

    # set blured image as background
    #blank_image.paste(create_blur(img, height).resize((width, height)))

    # put resized image to image container
    blank_image.paste(img, (int((blank_image.width - img.width) / 2),
                            int((blank_image.height - img.height) / 2)))
    img = blank_image
    return blank_image


def create_blur(img, size):
    return img.filter(ImageFilter.GaussianBlur(size / 10))


def auto_contrast(img: Image):
    return ImageOps.autocontrast(img, cutoff=5, ignore=0)


def adjust_color(img: Image, brightness: float, saturation: float, contrast: float):
    brightness_filter = ImageEnhance.Brightness(img)
    result = brightness_filter.enhance(brightness)

    saturation_filter = ImageEnhance.Color(result)
    result = saturation_filter.enhance(saturation)

    contrast_filter = ImageEnhance.Contrast(result)
    result = contrast_filter.enhance(contrast)
    return result


def draw_solid_border(img, thickness: int, color):
    img = ImageOps.expand(img, border=to_pixel(thickness), fill=color)
    return img


def draw_lumber_frame(img: Image, color: str = "white", offset: int = 100):
    # create draw image
    draw = ImageDraw.Draw(img)
    # left line
    draw.line([(offset, 0), (offset, img.height)], fill=color, width=1)
    # top line
    draw.line([(0, offset), (img.width, offset)], fill=color, width=1)
    # right line
    draw.line([(img.width - offset, 0), (img.width - offset, img.height)], fill=color, width=1)
    # bottom line
    draw.line([(0, img.height - offset), (img.width, img.height - offset)], fill=color, width=1)


def draw_zebra_frame(img: Image, color: str = "white", offset: int = 50):
    # create draw image
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle(((offset, offset), (img.width - offset, img.height - offset)), outline=color,
                   fill=(255, 255, 255, 0), width=1)
    offset = offset + 50
    draw.rectangle(((offset, offset), (img.width - offset, img.height - offset)), outline=color,
                   fill=(255, 255, 255, 0), width=1)


def draw_hook_frame(img: Image, color: str = "white", offset: int = 50, length: int = 50):
    # create draw image
    draw = ImageDraw.Draw(img)
    # top-left corner
    # top line
    draw.line([(offset, offset), (offset + length, offset)], fill=color, width=1)
    # left line
    draw.line([(offset, offset), (offset, offset + length)], fill=color, width=1)

    # top-right corner
    # top line
    draw.line([(img.width - offset, offset), (img.width - offset - length, offset)], fill=color, width=1)
    # right line
    draw.line([(img.width - offset, offset), (img.width - offset, offset + length)], fill=color, width=1)

    # bottom-right corner
    # right line
    draw.line([(img.width - offset, img.height - offset), (img.width - offset, img.height - offset - length)],
              fill=color, width=1)
    # bottom line
    draw.line([(img.width - offset, img.height - offset), (img.width - offset - length, img.height - offset)],
              fill=color, width=1)

    # bottom-left corner
    # left line
    draw.line([(offset, img.height - offset), (offset, img.height - offset - length)], fill=color, width=1)
    # bottom line
    draw.line([(offset, img.height - offset), (offset + length, img.height - offset)], fill=color, width=1)


def draw_polaroid_frame(img: Image, color: str = "white"):
    # create draw image
    draw = ImageDraw.Draw(img, "RGBA")
    offset = 100
    bottom_rectangle_weight = 50

    # bottom line
    draw.rectangle(
        ((offset, img.height - offset - bottom_rectangle_weight * 2), (img.width - offset, img.height - offset)),
        fill=color)

    # general polaroid frame
    draw.rectangle(((offset, offset), (img.width - offset, img.height - offset)), outline=color,
                   fill=(255, 255, 255, 0), width=5)
    img = img.crop((offset, offset, img.width - offset, img.height - offset))
    img.save("./public/cropp.jpg")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #print_hi('PyCharm')
    url = "https://pechat.photo/image/customer/authorized/13fe9d84310e77f13a6d184dbf1232f3/d46b69a8f3d536eccb784bcafcc3cb35.jpg"
    print(urlparse(url).path)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
