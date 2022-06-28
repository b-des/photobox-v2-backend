from dataclasses import dataclass
from typing import Optional, Any

from dataclasses_json import dataclass_json, Undefined


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Src:
    thumbnail: str
    full: Optional[str] = ""
    adjusted: Optional[str] = ""
