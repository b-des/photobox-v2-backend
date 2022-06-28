from dataclasses import dataclass

from dataclasses_json import dataclass_json, Undefined

from photobox.models.FrameType import FrameType


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class FrameOptions:
    color: str
    thickness: int
    type: FrameType
