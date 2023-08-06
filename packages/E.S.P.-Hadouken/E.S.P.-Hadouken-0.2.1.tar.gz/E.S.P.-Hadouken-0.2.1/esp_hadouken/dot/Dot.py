from pygame import mask
from pygame.locals import *

from esp_hadouken.GameChild import *
from esp_hadouken.sprite.Sprite import *
from engine.Engine import *

class Dot(Sprite):

    def __init__(self, parent, bounds, wrap):
        GameChild.__init__(self, parent)
        self.init_sprite(bounds, wrap)
        self.set_engine()
        self.set_outline()
        self.paint()
        self.enable_updates()

    def init_sprite(self, bounds, wrap):
        configuration = self.get_configuration()
        image_path = self.get_resource("dot-image-path")
        initial_blink_freq = configuration["dot-initial-blink-frequency"]
        max_blink_freq = configuration["dot-max-blink-frequency"]
        parent = self.parent
        Sprite.__init__(self, parent, image_path, parent, bounds, wrap,
                        initial_blink_freq, max_blink_freq)

    def set_engine(self):
        magnitude = self.get_configuration()["dot-thrust-magnitude"]
        self.engine = Engine(self, magnitude)

    def set_outline(self):
        ma = mask.from_surface(self.image)
        width, height = ma.get_size()
        outline = []
        for x in range(width):
            for y in range(height):
                if ma.get_at((x, y)):
                    if x in (0, width - 1) or y in (0, height - 1) or \
                        (not ma.get_at((x, y - 1)) or not \
                         ma.get_at((x, y + 1))):
                            outline.append((x, y))
        self.outline = outline

    def disable_updates(self):
        self.disabled = True

    def enable_updates(self):
        self.disabled = False

    def update(self):
        if self.visible and not self.disabled:
            self.engine.update()
            offset = self.engine.calculate_offset()
            if offset[0] is not (0.0, 0.0):
                self.move(offset)
            self.last_offset = offset
            Sprite.update(self)

    def halt(self):
        self.engine.halt()
