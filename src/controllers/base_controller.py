import sys
from pathlib import Path
import os 
import random
import string

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from ..helpers.config import get_settings, Settings
except ImportError:  # pragma: no cover
    from helpers.config import get_settings, Settings


class BaseController:
    def __init__(self):
        self.app_settings = get_settings()

        self.base_dir = os.path.dirname(os.path.dirname(__file__))
        self.file_dir = os.path.join(
            self.base_dir,
            "assets/files"
        )
    def generate_random_string(self, length: int = 12) -> str:
        
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


