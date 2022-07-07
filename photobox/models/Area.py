from dataclasses_json import dataclass_json, LetterCase, Undefined
from dataclasses import dataclass


@dataclass_json(letter_case=LetterCase.CAMEL, undefined=Undefined.EXCLUDE)
@dataclass
class Area:
    x: float
    y: float
    width: float
    height: float
