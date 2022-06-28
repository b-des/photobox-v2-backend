from dataclasses import dataclass
import enum

from PIL import Image
from dataclasses_json import dataclass_json, LetterCase, Undefined
from typing import Optional, Any, Dict

from photobox.models.Src import Src
from photobox.models.FrameOptions import FrameOptions
from photobox.models.Area import Area
from photobox.models.ColorSettings import ColorSettings
from photobox.models.PrintMode import PrintMode
from photobox.models.Size import Size


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class ImagePayload:
    auto_color_enhance: bool
    autoDetect_best_frame: bool
    color_adjustment: ColorSettings
    crop_data: Area
    detect_and_fill_with_gradient: bool
    frame: FrameOptions
    image_print_mode: PrintMode
    quantity: int
    rotate: int
    size: Size
    src: Src
    image: Image = Image
