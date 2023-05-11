import os
from pathlib import Path


class BasicView:

    MAX_FONT = ("Helvetica", 25)
    BUTTON_FONT = ("Helvetica", 14)
    PAD_Y = 40
    BACKGROUND_COLOR = 'white'
    WORKING_DIR = Path(os.getcwd())
    PRIVATE_KEY_DIR = os.path.join(Path(os.getcwd()),"ssh_private")
    PUBLIC_KEY_DIR = os.path.join(Path(os.getcwd()), "ssh_public")
    salt = os.environ.get("SALT", "default_salt").encode()

    def __init__(self, root, images,public_keys=None, private_keys=None):
        self.root = root
        self.private_keys= private_keys
        self.public_keys = public_keys
        self.images = images