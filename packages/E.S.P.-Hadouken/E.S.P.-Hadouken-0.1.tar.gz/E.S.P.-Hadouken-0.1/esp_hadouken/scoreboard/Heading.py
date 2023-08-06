from pygame import Surface, Color, Rect

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Heading(GameChild, Surface):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_rect()
        self.add_labels()
        self.render_title()

    def init_surface(self):
        parent = self.parent
        width = parent.get_width() - parent.get_padding()
        Surface.__init__(self, (width, parent.get_heading_height()))
        self.fill(Color(self.get_configuration()["scoreboard-heading-bg"]))

    def set_rect(self):
        rect = self.get_rect()
        offset = self.parent.get_padding() / 2
        rect.topleft = offset, offset
        self.rect = rect

    def add_labels(self):
        labels = []
        margin = self.get_margin()
        for ii in range(5):
            labels.append(Label(self, ii))
        self.labels = labels

    def render_title(self):
        config = self.get_configuration()
        size = config["scoreboard-heading-title-size"]
        text = config["scoreboard-heading-title"]
        color = Color(config["scoreboard-heading-title-color"])
        rend = Font(self, size).render(text, True, color)
        rect = rend.get_rect()
        offset = config["scoreboard-heading-title-offset"]
        rect.centery = self.get_rect().centery + offset
        rect.left = config["scoreboard-heading-title-indent"]
        self.blit(rend, rect)

    def get_margin(self):
        return self.get_configuration()["scoreboard-heading-margin"]

    def update(self):
        for label in self.labels:
            label.update()
        self.draw()

    def draw(self):
        self.parent.blit(self, self.rect)


class Label(GameChild, Surface):

    def __init__(self, parent, index):
        GameChild.__init__(self, parent)
        self.index = index
        self.init_surface()
        self.set_rect()

    def init_surface(self):
        parent = self.parent
        size = parent.get_height() - parent.get_margin()
        Surface.__init__(self, (size, size))
        self.paint()

    def paint(self):
        palette = self.get_palette()
        count = self.get_configuration()["scoreboard-heading-checker-count"]
        size = tuple([self.get_width() / count] * 2)
        for ii in range(count):
            for jj in range(count):
                rect = Rect((ii * size[0], jj * size[0]), size)
                self.fill(Color(palette[(ii + jj) % len(palette)]), rect)

    def get_palette(self):
        index = self.index
        if index == 0:
            level = "octo"
        elif index == 1:
            level = "horse"
        elif index == 2:
            level = "diortem"
        elif index == 3:
            level = "circulor"
        else:
            level = "tooth"
        return self.get_configuration()[level + "-level-palette"]

    def set_rect(self):
        rect = self.get_rect()
        rect.left = self.calculate_indent()
        rect.centery = self.parent.get_rect().centery
        self.rect = rect

    def calculate_indent(self):
        parent = self.parent
        width = parent.get_width()
        columns = parent.parent.get_column_widths()
        offset = (columns[3] * width - self.get_width()) / 2
        return sum(columns[:self.index + 3]) * width + offset

    def update(self):
        self.draw()

    def draw(self):
        self.parent.blit(self, self.rect)
