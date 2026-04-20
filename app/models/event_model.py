from dataclasses import dataclass
from typing import Optional
from PyQt5.QtGui import QImage

@dataclass
class SecurityEvent:
    tag: str
    msg: str
    color: str
    date: str
    time: str
    image: Optional[QImage] = None
    has_image_db: bool = False
    id: Optional[int] = None