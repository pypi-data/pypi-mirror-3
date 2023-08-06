from os import write
from time import time

from esp_hadouken.GameChild import *

class HighScores(GameChild, list):

    def __init__(self, parent):
        GameChild.__init__(self, parent)
        list.__init__(self, [])
        self.read()

    def read(self):
        for line in open(self.get_path()):
            line = line.strip()
            if line:
                self.append(Score(*line.split(" ")))

    def get_path(self):
        return self.get_resource("scoreboard-scores-path")

    def add(self, player):
        timer = self.get_timer()
        score = Score(time(), player, timer.total(), *timer.values())
        self.append(score)
        self.write(score)

    def write(self, score):
        scores = open(self.get_path(), "a")
        scores.write(str(score) + "\n")

    def get_most_recent_player(self):
        return self[-1].player


class Score:

    def __init__(self, *args):
        self.date = int(args[0])
        self.player = args[1]
        self.total, self.octo, self.horse, self.diortem, self.circulor, \
                    self.tooth = map(float, args[2:])

    def __str__(self):
        return "%i %s %.3f %.3f %.3f %.3f %.3f %.3f" % \
               (self.date, self.player, self.total, self.octo, self.horse,
                self.diortem, self.circulor, self.tooth)

    def __lt__(self, other):
        return self.total < other.total

    def __repr__(self):
        return self.__str__()
