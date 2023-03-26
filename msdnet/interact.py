"""
Interact with MSDNetwork
"""

import pygame as pg
import numpy as np


class Interact():
    def __init__(self, network: dict, masses: dict, canvas_size: tuple[int, int]) -> None:
        self.net = network
        self.masses = masses
        self.width = canvas_size[0]
        self.height = canvas_size[1]
        self.mouse = pg.mouse

    def interact_with_mass(self, event: pg.event):

        for mass in self.net:
            curr_pos = np.array([self.net[mass]["x"] * self.width, self.net[mass]["y"] * self.height], dtype=float)
            mouse_pos = self.mouse.get_pos()
            mouse_pos = np.array([mouse_pos[0], mouse_pos[1]], dtype=float)
            dist = np.sqrt(np.sum(np.square(curr_pos - mouse_pos)))

            if dist < self.masses[mass].radius:
                if self.mouse.get_pressed()[2]:
                    self.masses[mass].anchored = False

                if event.type == pg.MOUSEBUTTONDOWN:
                    self.masses[mass].is_pressed = True
                    self.masses[mass].is_anchored_press = True
                if event.type == pg.MOUSEBUTTONUP:
                    for mass_pressed in self.masses:
                        self.masses[mass_pressed].is_pressed = False
                        self.masses[mass_pressed].is_anchored_press = False
            
                if self.mouse.get_pressed()[0] and self.masses[mass].is_pressed:
                    self.masses[mass].pos = np.array([self.mouse.get_pos()[0]/self.width, self.mouse.get_pos()[1]/self.height, 0])
                    self.masses[mass].prev_pos = self.masses[mass].pos
