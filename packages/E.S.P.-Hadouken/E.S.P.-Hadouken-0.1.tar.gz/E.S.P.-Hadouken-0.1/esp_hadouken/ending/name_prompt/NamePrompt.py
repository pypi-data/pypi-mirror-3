from pygame import Surface, Color
from pygame.locals import *

from esp_hadouken.GameChild import *
from Cell import *

class NamePrompt(GameChild, Surface):

    cell_count = 3
    transparent_color = Color("brown")

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.subscribe_to_events()
        self.add_cells()
        self.deactivate()

    def init_surface(self):
        size = self.get_configuration()["scoreboard-prompt-dimensions"]
        Surface.__init__(self, size)
        self.set_transparent()
        rect = self.get_rect()
        rect.center = self.parent.get_rect().center
        self.rect = rect

    def set_transparent(self):
        color = self.transparent_color
        self.set_colorkey(color)
        self.fill(color)

    def subscribe_to_events(self):
        self.subscribe_to(KEYDOWN, self.respond_to_key)

    def respond_to_key(self, event):
        if self.active:
            key = event.key
            if key >= K_a and key <= K_z:
                self.get_active_cell().set_char(key)
                self.change_active_cell(1)
                self.parent.update()
            elif key == K_BACKSPACE:
                if self.get_active_cell().is_blank():
                    self.change_active_cell(-1)
                self.get_active_cell().reset()
                self.parent.update()

    def get_active_cell(self):
        return self.cells[self.active_cell_index]

    def change_active_cell(self, increment):
        limit = len(self.cells) - 1
        index = self.active_cell_index + increment
        if index > limit:
            index = limit
        elif index < 0:
            index = 0
        self.active_cell_index = index

    def add_cells(self):
        cells = []
        for ii in range(self.cell_count):
            cells.append(Cell(self, ii))
        self.cells = cells
        self.active_cell_index = 0

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def update(self):
        if self.active:
            self.draw()

    def draw(self):
        self.parent.blit(self, self.rect)

    def get_initials(self):
        return "".join(map(str, self.cells))
