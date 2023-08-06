from pygame import Surface, Color
from pygame.locals import *

from esp_hadouken.GameChild import *
from esp_hadouken.Font import *

class Row(GameChild, Surface):

    def __init__(self, parent, index):
        GameChild.__init__(self, parent)
        self.index = index
        self.disable_highlight()
        self.init_surface()
        self.set_rect()
        self.set_column_surfaces()

    def enable_highlight(self):
        self.highlit = True

    def disable_highlight(self):
        self.highlit = False

    def init_surface(self):
        parent = self.parent
        width = parent.get_width() - parent.get_padding()
        Surface.__init__(self, (width, parent.get_row_height()))
        self.fill(self.get_color())

    def get_color(self):
        config = self.get_configuration()
        if self.highlit:
            color = config["scoreboard-highlight-color"]
        elif not self.index % 2:
            color = config["scoreboard-row-color-1"]
        else:
            color = config["scoreboard-row-color-2"]
        return Color(color)

    def set_rect(self):
        rect = self.get_rect()
        parent = self.parent
        index = self.index
        padding = parent.get_padding()
        heading = parent.get_heading_height()
        rect.top = padding / 2 + index * parent.get_row_height() + heading
        rect.centerx = parent.get_rect().centerx
        self.rect = rect

    def set_column_surfaces(self):
        self.rank_surf, self.rank_surf_r = self.set_column_surface(0)
        self.initials_surf, self.initials_surf_r = self.set_column_surface(1)
        self.total_surf, self.total_surf_r = self.set_column_surface(2)
        self.split_surfs, self.split_surfs_rs = [], []
        for ii in range(3, 8):
            surf, rect = self.set_column_surface(ii)
            self.split_surfs.append(surf)
            self.split_surfs_rs.append(rect)

    def set_column_surface(self, index):
        ratios = self.parent.get_column_widths()
        relative = self.get_size()
        surf = Surface((relative[0] * ratios[index], relative[1]))
        surf.fill(self.get_color())
        indent = 0
        for ratio in ratios[:index]:
            indent += ratio * relative[0]
        rect = surf.get_rect()
        rect.left = indent
        return surf, rect

    def set_score(self, score, rank):
        self.render_rank(rank)
        self.render_initials(score)
        self.render_total(score)
        if score is None:
            splits = [None] * 5
        else:
            splits = [score.octo, score.horse, score.diortem, score.circulor,
                      score.tooth]
        for ii, split in enumerate(splits):
            self.render_split(ii, split)

    def render_rank(self, rank):
        size = self.get_configuration()["scoreboard-rank-size"]
        rend = Font(self, size).render(str(rank + 1), True, self.get_text_color(),
                                       self.get_color())
        rect = rend.get_rect()
        dest = self.rank_surf
        dest.fill(self.get_color())
        rect.center = dest.get_rect().center
        dest.blit(rend, rect)

    def get_text_color(self):
        return Color(self.get_configuration()["scoreboard-text-color"])

    def render_initials(self, score):
        self.initials_surf.fill(self.get_color())
        if score is None:
            return
        x = 0
        margin = self.get_configuration()["scoreboard-initials-margin"]
        size = self.get_height() - margin * 2
        for letter in score.player:
            self.render_initial(letter, x, size)
            x += size + margin

    def get_blank_char(self):
        return self.get_configuration()["scoreboard-blank-char"]

    def render_initial(self, letter, x, size):
        square = Surface((size, size))
        if letter == self.get_blank_char():
            color = self.get_configuration()["scoreboard-initials-blank-color"]
            color = Color(color)
        else:
            color = self.get_glyph_palette()[ord(letter.lower()) - K_a]
        square.fill(color)
        font_size = self.get_configuration()["scoreboard-initials-size"]
        rend = Font(self, font_size).render(letter, True, self.get_text_color(),
                                            color)
        square_rect = square.get_rect()
        rend_rect = rend.get_rect()
        rend_rect.center = square_rect.center
        square.blit(rend, rend_rect)
        square_rect.centery = self.get_rect().centery
        square_rect.left = x
        self.initials_surf.blit(square, square_rect)

    def render_total(self, score):
        dest = self.total_surf
        dest.fill(self.get_color())
        if score is None:
            return
        text = self.build_time_string(score.total)
        size = self.get_configuration()["scoreboard-total-size"]
        rend = Font(self, size).render(text, True, self.get_text_color(),
                                       self.get_color())
        rect = rend.get_rect()
        rect.center = dest.get_rect().center
        dest.blit(rend, rect)

    def build_time_string(self, time):
        return "%i:%02i" % divmod(int(time), 60)

    def get_blank_time(self):
        return self.get_blank_char()

    def render_split(self, index, time):
        dest = self.split_surfs[index]
        dest.fill(self.get_color())
        if time is None:
            return
        text = self.build_time_string(time)
        size = self.get_configuration()["scoreboard-split-size"]
        rend = Font(self, size).render(text, True, self.get_text_color(),
                                       self.get_color())
        rect = rend.get_rect()
        rect.center = dest.get_rect().center
        dest.blit(rend, rect)

    def update(self):
        self.clear()
        self.draw()

    def clear(self):
        self.fill(self.get_color())

    def draw(self):
        self.blit(self.rank_surf, self.rank_surf_r)
        self.blit(self.initials_surf, self.initials_surf_r)
        self.blit(self.total_surf, self.total_surf_r)
        for ii, surf in enumerate(self.split_surfs):
            self.blit(surf, self.split_surfs_rs[ii])
        self.parent.blit(self, self.rect)
