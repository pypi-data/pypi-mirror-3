from pygame import Surface

from esp_hadouken.GameChild import *
from esp_hadouken.Input import *
from Row import *
from Heading import *

class Scoreboard(GameChild, Surface):

    active_interval = 0

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        self.init_surface()
        self.set_rect()
        self.heading = Heading(self)
        self.add_rows()
        self.subscribe_to(Input.command_event, self.respond_to_command)
        self.deactivate()

    def init_surface(self):
        config = self.get_configuration()
        step = self.get_step()
        padding = self.get_padding()
        row_height = self.get_row_height()
        height = step * row_height + padding + self.get_heading_height()
        Surface.__init__(self, (config["scoreboard-width"], height))
        self.set_alpha(config["scoreboard-alpha"])

    def get_step(self):
        return self.get_configuration()["scoreboard-interval-length"]

    def get_row_height(self):
        return self.get_configuration()["scoreboard-row-height"]

    def get_padding(self):
        return self.get_configuration()["scoreboard-padding"]

    def get_heading_height(self):
        return self.get_configuration()["scoreboard-heading-height"]
    
    def get_column_widths(self):
        return self.get_configuration()["scoreboard-column-widths"]

    def set_rect(self):
        rect = self.get_rect()
        rect.center = self.get_screen().get_rect().center
        self.rect = rect

    def add_rows(self):
        rows = []
        for ii in range(self.get_step()):
            rows.append(Row(self, ii))
        self.rows = rows

    def respond_to_command(self, event):
        if self.active:
            command = event.command
            if command == "next":
                self.set_active_interval(1)
                self.populate()
            elif command == "previous":
                self.set_active_interval(-1)
                self.populate()

    def set_active_interval(self, increment=0, interval=None):
        if interval is None:
            interval = self.active_interval + increment
        max_interval = self.get_max_interval()
        if interval < 0:
            interval = 0
        elif interval > max_interval:
            interval = max_interval
        self.active_interval = interval

    def get_max_interval(self):
        return len(self.get_high_scores()) / self.get_step()

    def populate(self):
        self.disable_highlights()
        step = self.get_step()
        low = step * self.active_interval
        high = low + step
        interval = self.get_ordered_scores()[low:high]
        interval += [None] * (step - len(interval))
        rows = self.rows
        for ii, score in enumerate(interval):
            score_index = low + ii
            row = rows[ii]
            if score_index == self.get_highlit_score_index():
               row.enable_highlight() 
            row.set_score(score, score_index)
        self.parent.update()

    def disable_highlights(self):
        for row in self.rows:
            row.disable_highlight()

    def get_ordered_scores(self):
        return sorted(self.get_high_scores())

    def activate(self, highlight=True):
        self.active = True
        if highlight:
            self.show_recent_score_interval()
        self.populate()

    def show_recent_score_interval(self):
        ordered = self.get_ordered_scores()
        interval = self.get_highlit_score_index() / self.get_step()
        self.set_active_interval(interval=interval)

    def get_highlit_score_index(self):
        return self.get_ordered_scores().index(self.get_high_scores()[-1])

    def deactivate(self):
        self.active = False

    def update(self):
        if self.active:
            self.clear()
            self.heading.update()
            for row in self.rows:
                row.update()
            self.draw()

    def clear(self):
        self.fill(Color(self.get_configuration()["scoreboard-bg"]))

    def draw(self):
        self.parent.blit(self, self.rect)
