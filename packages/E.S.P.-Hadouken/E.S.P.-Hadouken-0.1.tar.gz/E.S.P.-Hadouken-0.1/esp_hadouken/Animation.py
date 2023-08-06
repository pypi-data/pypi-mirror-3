import pygame

class Animation:

    def __init__(self, frame_duration):
        self.reset_ticks()
        self.updates_this_cycle = 1
        self.overflow = 0
        self.update_count = 1
        self.actual_frame_duration = 0
        self.target_frame_duration = frame_duration
        self.stopping = False

    def reset_ticks(self):
        self.last_ticks = self.get_ticks()

    def play(self):
        while not self.stopping:
            self.advance_frame()
            self.update_frame_duration()
            self.update_overflow()
        self.stopping = False

    def advance_frame(self):
#         while self.update_count > 0:
            self.sequence()
#             self.update_count -= 1

    def update_frame_duration(self):
        last_ticks = self.last_ticks
        actual_frame_duration = self.get_ticks() - last_ticks
        last_ticks = self.get_ticks()
        wait_duration = self.get_configuration()["display-wait-duration"]
        while actual_frame_duration < self.target_frame_duration:
            pygame.time.wait(wait_duration)
            actual_frame_duration += self.get_ticks() - last_ticks
            last_ticks = self.get_ticks()
        self.actual_frame_duration = actual_frame_duration
        self.last_ticks = last_ticks

    def get_ticks(self):
        return pygame.time.get_ticks()

    def update_overflow(self):
        self.update_count = 1
        target_frame_duration = self.target_frame_duration
        overflow = self.overflow
        overflow += self.actual_frame_duration - target_frame_duration
        while overflow > target_frame_duration:
            self.update_count += 1
            overflow -= target_frame_duration
        overflow = self.overflow

    def stop(self):
        self.stopping = True

    def clear_queue(self):
        self.update_count = 1
