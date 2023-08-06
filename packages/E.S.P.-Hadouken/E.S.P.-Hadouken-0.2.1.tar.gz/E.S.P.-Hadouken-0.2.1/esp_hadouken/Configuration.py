import re
import os
from sys import argv
from os.path import exists, join

import pygame

class Configuration(dict):

    assignment_operator = "="
    comments_operator = "#"
    field_separator = ","
    keys_prefix = "keys_"
    
    int_parameters = [
        "display-frame-duration", "display-wait-duration",
        "introduction-diortem-y", "overworld-toy-y", "overworld-wall-y",
        "overworld-dot-y", "joy-advance", "overworld-bandits-margin",
        "ending-score-size", "background-music-channel-id",
        "octo-level-min-gap", "octo-level-barrier-height",
        "octo-level-scroll-speed", "level-checker-width",
        "tooth-level-scroll-speed", "circulor-level-scroll-speed",
        "diortem-level-scroll-speed", "horse-level-scroll-speed",
        "horse-level-step-limit", "level-exit-alpha", "joy-pause",
        "introduction-prompt-size", "introduction-controls-height",
        "introduction-controls-size", "introduction-controls-offset",
        "introduction-controls-alpha", "timer-max-time",
        "scoreboard-palette-length", "scoreboard-prompt-margin",
        "scoreboard-prompt-text-size", "scoreboard-palette-brightness",
        "ending-input-message-y", "ending-input-message-size",
        "scoreboard-padding", "scoreboard-row-height",
        "scoreboard-interval-length", "scoreboard-width", "scoreboard-alpha",
        "scoreboard-rank-size", "scoreboard-total-size",
        "scoreboard-initials-size", "scoreboard-split-size",
        "scoreboard-initials-margin", "scoreboard-heading-height",
        "scoreboard-heading-checker-count", "scoreboard-heading-margin",
        "scoreboard-heading-title-size", "scoreboard-heading-title-indent",
        "scoreboard-heading-title-offset", "distance-text-size"]

    float_parameters = [
        "dot-thrust-magnitude", "dot-initial-blink-frequency",
        "dot-max-blink-frequency", "introduction-entrance-speed",
        "introduction-exit-speed", "level-max-dot-displacement",
        "tooth-level-switch-frequency", "circulor-level-speed",
        "distance-modifier"]

    list_parameters = [
        "keys-up", "keys-right", "keys-down", "keys-left", "keys-quit",
        "keys-pause", "sprite-inner-palette", "sprite-outer-palette",
        "keys-advance", "keys-capture-screen", "keys-reset",
        "octo-level-palette", "horse-level-palette", "diortem-level-palette",
        "circulor-level-palette", "tooth-level-palette", "keys-pause",
        "keys-mute", "keys-skip", "keys-previous", "keys-next",
        "game-platforms"]

    tuple_parameters = [
        "introduction-toy-position", "introduction-prompt-position",
        "display-dimensions", "octo-level-dimensions",
        "octo-level-dot-position", "octo-level-bandit-position",
        "octo-level-rect-position", "diortem-level-dimensions",
        "diortem-level-dot-position", "diortem-level-bandit-position",
        "horse-level-dimensions", "horse-level-dot-position",
        "horse-level-bandit-position", "circulor-level-dimensions",
        "circulor-level-dot-position", "circulor-level-bandit-position",
        "tooth-level-dimensions", "tooth-level-dot-position",
        "tooth-level-bandit-position", "ending-toy-size", "ending-toy-position",
        "ending-plate-position", "octo-level-void-padding",
        "octo-level-spawn-range", "level-blink-frequency-range",
        "tooth-level-void-padding", "tooth-level-radius-range",
        "tooth-level-spawn-range", "diortem-level-void-padding",
        "diortem-level-segment-width-range", "diortem-level-shift-range",
        "diortem-level-segment-height-range", "diortem-level-leg-range",
        "circulor-level-height-range", "circulor-level-base-range",
        "circulor-level-void-padding", "horse-level-size-range",
        "horse-level-void-padding", "scoreboard-prompt-dimensions",
        "scoreboard-column-widths", "distance-dimensions"]

    boolean_parameters = []
    true_values = ["yes", "y", "true", "t", "1"]

    path_values = [
        "dot-image-path", "introduction-bg-path", "toy-image-path",
        "overworld-bg-path", "overworld-wall-path", "screen-capture-save-dir",
        "overworld-bandits-path", "level-bandit-sprite-path", "ending-bg-path",
        "ending-plate-path", "introduction-audio-path", "overworld-audio-path",
        "level-audio-path", "ending-audio-path", "horse-level-maze-path",
        "level-failure-sound", "level-success-sound", "sfx-path",
        "level-exit-path", "pause-image-path", "display-icon-path", "font-path",
        "resources-install-path", "scoreboard-scores-path"]
    
    def __init__(self, local=False):
        self.local = local
        self.set_file_path()
        self.parse()

    def set_file_path(self):
        path = "config"
        installed_path = join("/usr/local/share/esp-hadouken/", path)
        if exists(installed_path) and self.use_installed_file():
            path = installed_path
        self.file_path = path

    def use_installed_file(self):
        if "-l" in argv or self.local:
            return False
        return True
    
    def parse(self):
        for line in file(self.file_path):
            line = line.strip()
            if len(line) > 0 and line[0] != self.comments_operator:
                (lval, rval) = map(
                    str.strip, line.split(self.assignment_operator))
                if lval in self.int_parameters:
                    rval = int(rval)
                if lval in self.float_parameters:
                    rval = float(rval)
                if lval in self.boolean_parameters:
                    rval = True if self.is_true_value(rval) else False
                if lval in self.path_values:
                    rval = self.translate_path(rval)
                if lval in self.tuple_parameters:
                    rval = eval(rval)
                if lval in self.list_parameters:
                    rval = map(str.strip, rval.split(self.field_separator))
                    if self.is_key_assignment(lval):
                        rval = map(lambda key: getattr(pygame, key), rval)
                self[lval] = rval

    def translate_path(self, rval):
        new = ""
        if rval[0] == "/":
            new += "/"
        return new + os.path.join(*rval.split("/"))

    def is_true_value(self, rval):
        return rval.lower() in self.true_values

    def is_key_assignment(self, lval):
        pattern = "^" + self.keys_prefix + "*"
        return re.match(pattern, lval) is not None
