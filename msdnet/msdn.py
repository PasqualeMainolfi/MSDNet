"""
MSDN (Mass-Spring-Damper Network)

"""

from msdnet.network_components import Mass, Spring, Damper
import numpy as np
from msdnet.interact import Interact
import pygame as pg

class MSDNet():

    def __init__(self) -> None:
        
        self.masses = dict()
        self.springs = dict()
        self.dampers = dict()

        self.mass_params = dict() # mass parameters
        self.masses_motion = dict() # motion of masses
        self.spring_params = dict() # spring parameters

        self.external_forces = dict()

        self.motion = dict()

        self.g = np.zeros(3)
        self.dt = 0.1
    

    def add_dt(self, dtime: float) -> None:

        """
        set sampling time

        dtime: int, sample time (in sec)
        """
        
        self.dt = dtime
    

    def add_gravity(self, g: list[float, float, float]) -> None:
        self.g = np.array(g, dtype=float)
    

    def add_mass(self, name: str, m: float, pos: list[float], d: float, r: float, anchored: bool = False) -> None:

        """
        add mass to the network

        name: str, mass name
        m: float, mass in kg
        pos: list[float], position [x, y, z]
        d: float, air friction factor
        r: float, radius of mass
        anchored: bool, if True the mass is anchored
        """


        mass = Mass(name=name, m=m, pos=pos, d=d, radius=r, anchored=anchored, g=self.g)
        self.masses[name] = mass

        self.mass_params[name] = {
            "start": pos,
            "weight": m,
            "radius": r,
            }

        self.masses_motion[name] = {
            "x": [],
            "y": [],
            "z": [],
            "xyz": []
        }
        
        self.motion[name] = {"x": pos[0], "y": pos[1], "z": pos[2]}


    def lock_unlock_mass(self, name: str, anchored: bool):

        """
        anchor the mass

        name: str, mass name
        anchored: bool, if True the mass is anchored
        """

        self.masses[name].anchored = anchored


    def add_spring(self, name: str, k: float, length: float, m1: str, m2: str) -> None:

        """
        add spring to the network

        name: str, spring name
        k: float, stiffness in N/m
        length: float, spring length in m
        m1: str, name of the mass anchored to the left
        m2: str, name of the mass anchored to rhe right
        """

        spring = Spring(name=name, k=k, length=length, m1=self.masses[m1], m2=self.masses[m2])
        self.springs[name] = spring
        self.spring_params[name] = {
            "stiffness": k,
            "length": length,
            "link": f"{self.masses[m1].name} < -- > {self.masses[m2].name}",
            "m1": self.masses[m1].name,
            "m2": self.masses[m2].name
        }
    

    def add_damper(self, name: str, c: float, spring: str) -> None:

        """
        add damper to the network

        name: str, damper name
        c: float, damping factor
        spring: str, name of spring to add the damper
        """

        damper = Damper(name=name, c=c, m1=self.springs[spring].m1, m2=self.springs[spring].m2)
        self.dampers[name] = damper
        self.spring_params[spring].update({"damper": name, "c": c})


    def add_external_force(self, name: str, direction: list[float], masses: str|list[str] = "all", mode: str = "always_on") -> None:

        """
        add external force to the network

        name: str, force name
        direction: list[float] -> [x, y, z]
        masses: str|list[str], "all" or list of masses. If "all", force is applied on all masses. It is possible, or, to pass the list of masses to which to apply the force
        mode: str, shot -> ["one_shot", "always_on", "rand_shot"]:
            one_shot -> apply force only once (first iteration)
            always_on -> apply force at each iteration
            rand_shot -> apply force probabilistically
        """
        
        params = {
            "force": np.array(direction, dtype=float),
            "start_force": np.array(direction, dtype=float),
            "where": masses,
            "mode": mode
        }

        self.external_forces[name] = params
    

    def __generate_external_force(self):

        for force in self.external_forces:

            f = self.external_forces[force]["force"]
            w = self.external_forces[force]["where"]
            mode = self.external_forces[force]["mode"]

            if w == "all":
                for mass in self.masses:
                    self.masses[mass].apply_force(f)
            if isinstance(w, list):
                for mass in w:
                    self.masses[mass].apply_force(f)
            if mode in ["one_shot", "rand_shot"]:
                self.external_forces[force]["force"] *= 0
            if mode == "rand_shot":
                v, p = np.random.rand(), np.random.rand() * 0.01
                if v < p:
                    direc = np.random.choice([-1, 1])
                    self.external_forces[force]["force"] = direc * self.external_forces[force]["start_force"]

    
    def reset_network(self) -> None:

        """
        reset network... take the network to zero time
        """

        for mass in self.masses:
            self.masses[mass].pos = self.masses[mass].start_pos
            self.masses[mass].vel = np.zeros(3)
            self.masses[mass].acc = np.zeros(3)
            for coord in self.masses_motion[mass]:
                self.masses_motion[mass][coord] = []
    

    def __in_motion(self, clip_pos, acc_is_costant=False) -> None:

        for spring in self.springs:
            self.springs[spring].generate_spring_force()

        for damper in self.dampers:
            self.dampers[damper].generate_drag_force()
        
        if self.external_forces:
            self.__generate_external_force()
        
        for mass in self.masses:
            self.motion[mass]["x"] = self.masses[mass].pos[0] 
            self.motion[mass]["y"] = self.masses[mass].pos[1] 
            self.motion[mass]["z"] = self.masses[mass].pos[2] 
            
            self.masses[mass].update_position(dt=self.dt, acc_is_costant=acc_is_costant, clip_pos=clip_pos)

    
    def run_network(self, clip_pos: tuple|None = None, acc_is_costant: bool = False) -> dict["MSDNet"]:

        """
        set network in motion

        same as activate network, but it is not a Generator
        return -> dict[mass][pos] -> current position of all masses. 
            The dictionary contains all the masses and, each mass is a dictionary 
            which contains x, y, z
        """
        
        self.__in_motion(clip_pos=clip_pos, acc_is_costant=acc_is_costant)
        return self.motion

    
    def render(self, canvas_size: tuple[int, int], clip_pos: tuple[float, float], fps: int = 60, acc_is_costant: bool = False) -> None:

        """
        render and show network with pygame

        surface: pg.Surface
        event: pg.event, main loop events
        canvas_size: tuple[int, int], canvas size
        """

        pg.init()

        w, h = canvas_size[0], canvas_size[1]
        win = (w, h)
        screen = pg.display.set_mode(win)
        clock = pg.time.Clock()
        fps = fps

        interact = Interact(network=self.motion, masses=self.masses, canvas_size=canvas_size)

        run = True
        while run:
            self.run_network(clip_pos=clip_pos, acc_is_costant=acc_is_costant)

            for event in pg.event.get():
                if event.type == pg.QUIT:
                    run = False
                    pg.quit()

                interact.interact_with_mass(event=event)

            w = canvas_size[0]
            h = canvas_size[1]

            for mass in self.motion:
                m = self.motion[mass]
                x = m["x"] * w
                y = m["y"] * h

                pg.draw.circle(surface=screen, color=(255, 0, 0), center=(x, y), radius=self.masses[mass].radius)
            
            for spring in self.spring_params:
                m1_name= self.spring_params[spring]["m1"]
                m2_name = self.spring_params[spring]["m2"]

                m1 = self.motion[m1_name]
                m2 = self.motion[m2_name]

                x1, y1 = m1["x"] * w, m1["y"] * h
                x2, y2 = m2["x"] * w, m2["y"] * h

                pg.draw.line(screen, color=(255, 255, 255), start_pos=(x1, y1), end_pos=(x2, y2))
            
            clock.tick(fps)
            pg.display.update()
            screen.fill((0, 0, 0))