from pygame import font

from GameChild import *

class Font(font.Font, GameChild):

    def __init__(self, parent, size):
        GameChild.__init__(self, parent)
        font.Font.__init__(self, self.get_resource("font-path"), size)
