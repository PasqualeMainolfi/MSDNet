"""

MSDNetwork components: mass, spring, damper

"""


import numpy as np

def magnitude(v: list) -> float:
    y = np.asarray(v)
    m = np.sqrt(y.dot(y))
    return m

def normalize(v: list) -> list:
    y = v.copy()
    m = magnitude(v)
    n = y/m if m > 0 else y
    return n

def limit(v: list, max_value: float) -> list:
    mag = magnitude(v)
    norm = v/mag if mag > 0 else v
    if mag >= max_value:
        return norm * max_value
    return v


class Mass():

    def __init__(self, name: str, m: float, pos: list[float], d: float, radius: float, g: list[float, float, float], anchored: bool = False) -> None:

        """
        Create mass

        name: str, mass name
        m: float, mass in kg
        pos: list[float], position [x, y, z]
        d: float, damping factor
        anchored: bool, if True the mass is anchored
        """

        self.name = name
        self.m = m
        self.d = d
        self.radius = radius
        self.anchored = anchored
        self.g = np.array(g, dtype=float) * self.m

        p = np.array(pos, dtype=float)
        self.start_pos = p.copy()

        self.pos = p.copy()
        self.prev_pos = self.pos.copy()
        self.vel = np.zeros(3)
        self.acc = np.zeros(3)

        self.is_pressed = False
        self.is_anchored_press = False

    # apply force
    def apply_force(self, force: list[float]) -> None:
        f = np.array(force, dtype=float)/self.m
        self.acc += f

    # update mass position using Verlet
    def update_position(self, dt: float, acc_is_costant: bool = False, clip_pos: tuple|None = None) -> None:

                
        if not self.anchored and not self.is_anchored_press:
            # Verlet
            # x[n + 1] = x[n] + (x[n]-x[n - 1]/dt)dt + a * dt^2 = 2x[n] - x[n - 1] + a * dt**2
            # v[n + 1] = (x[n] - x[n - 1]/dt) * dt = x[n] - x[n - 1]
            self.acc += self.g # add gravity
            for i in range(3):
                self.vel[i] = self.pos[i] - self.prev_pos[i]
            self.prev_pos = self.pos.copy()
            self.pos += self.vel * self.d + self.acc * dt**2
        
        if not acc_is_costant:
            self.acc = np.zeros(3)

        if clip_pos:
            for i in range(3):
                if self.pos[i] <= clip_pos[0]:
                    self.pos[i], self.prev_pos[i] = clip_pos[0], self.pos[i]
                    self.vel[i] *= -0.987
                if self.pos[i] >= clip_pos[1]:
                    self.pos[i], self.prev_pos[i] = clip_pos[1], self.pos[i]
                    self.vel[i] *= -0.987

class Spring():

    def __init__(self, name: str, k: float, length: float, m1: Mass, m2: Mass) -> None:


        """
        Create spring

        name: str, spring name
        k: float, stiffness in N/m
        length: float, spring length in m
        m1: Mass, mass anchored to the left of the spring
        m2: Mass, mass anchored to the left of the spring
        """

        self.name = name
        self.k = k
        self.length = length
        self.m1 = m1
        self.m2 = m2


    def generate_spring_force(self) -> None:

        """
        F = -k · x (Hooke's law)
        """

        force = np.subtract(self.m2.pos, self.m1.pos)
        mag = magnitude(v=force)
        x = mag - self.length
        force_direction = normalize(force)
        f = force_direction * (self.k * x)
        self.m1.apply_force(f)
        self.m2.apply_force(-f)


class Damper():

    def __init__(self, name: str, c: float, m1: Mass, m2: Mass) -> None:


        """
        Create damper
        name: str, damper name
        c: float, drag coefficient
        m1: Mass, mass anchored to the left of the spring
        m2: Mass, mass anchored to the left of the spring
        """

        self.name = name
        self.c = c
        self.m1 = m1
        self.m2 = m2
    
    def generate_drag_force(self) -> None:

        """
        F = 0.5 · pv^2 · C · A = -c·v^2
        """
        
        drag = np.subtract(self.m2.vel, self.m1.vel)
        mag = magnitude(v=drag)
        drag_direction = normalize(drag)
        d = drag_direction * self.c * np.power(mag, 2)
        self.m1.apply_force(d)
        self.m2.apply_force(-d)