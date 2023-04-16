class BasicView:

    MAX_FONT = ("Helvetica", 25)
    BUTTON_FONT = ("Helvetica", 14)
    PAD_Y = 40
    BACKGROUND_COLOR = 'white'

    def __init__(self, root, images):
        self.root = root
        self.images = images