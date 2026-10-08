import sys
from pathlib import Path
import os 
import random
import string

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from helpers.config import get_settings, Settings
    # from ..helpers.config import get_settings, Settings
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
        self.database_dir = os.path.join(
            self.base_dir,
            "assets/database"
        )

    def generate_random_string(self, length: int = 12) -> str:
        
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))


    def get_database_path(self, database_name: str):

        database_path =  os.path.join(self.database_dir, database_name)
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        return database_path

