import os
from pathlib import Path


class BasicView:

    MAX_FONT = ("Helvetica", 25)
    BUTTON_FONT = ("Helvetica", 14)
    PAD_Y = 40
    BACKGROUND_COLOR = 'white'
    WORKING_DIR = Path(os.getcwd())
    PRIVATE_KEY_DIR = os.path.join(Path(os.getcwd()),"ssh_private")

    def __init__(self, root, images):
        self.root = root
        self.images = images