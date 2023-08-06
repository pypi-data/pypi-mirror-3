import math

class Vector:

    def __init__(self, index):
        angle = index * (math.pi / 4)
        self.magnitude = 0
        self.sin = math.sin(angle)
        self.cos = math.cos(angle)
        self.angle = angle

    def __repr__(self):
        return "<mag: %i, angle: %f>" % (self.magnitude, self.angle)

    def grow(self, magnitude):
        self.magnitude += magnitude

    def cancel(self):
        self.magnitude = 0
