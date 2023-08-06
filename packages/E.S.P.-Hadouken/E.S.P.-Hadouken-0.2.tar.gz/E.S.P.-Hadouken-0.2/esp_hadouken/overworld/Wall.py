from esp_hadouken.GameChild import *
from esp_hadouken.sprite.Sprite import *

class Wall(GameChild):

    def __init__(self, overworld):
        GameChild.__init__(self, overworld)
        self.set_sprites()

    def set_sprites(self):
        path = self.get_resource("overworld-wall-path")
        y = self.get_configuration()["overworld-wall-y"]
        display_surface = self.parent
        left = Sprite(self, path, display_surface)
        right = Sprite(self, path, display_surface)
        right.flip()
        left.place(y=y)
        right.place(display_surface.get_width() - right.rect.w, y)
        self.sprites = left, right

    def show(self):
        for sprite in self.sprites:
            sprite.show()

    def update(self):
        for sprite in self.sprites:
            sprite.update()

    def collide_with(self, sprite):
        for sprite in self.sprites:
            if sprite.rect.colliderect(sprite.rect):
                return True
        return False

    def get_rects(self):
        return [sprite.rect for sprite in self.sprites]

    def get_bottom(self):
        return self.sprites[0].rect.bottom
