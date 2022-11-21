"""
MSDN (Mass-Spring-Damper Network)

"""

from typing import Generator
from utils.network_components import Mass, Spring, Damper, Hammer
from utils.scanner import Scanner
import numpy as np
import sys
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# TODO: add hammer interaction
# TODO: add function for set network start displacement


class MSDNetwork():
    def __init__(self) -> None:
        self.masses = dict()
        self.springs = dict()
        self.dampers = dict()

        self.mass_params = dict() # mass parameters
        self.masses_motion = dict() # motion of masses
        self.spring_params = dict() # spring parameters

        self.external_forces = dict()

        self._hammer_mode = None
        self.hammer = None

        self.scan = Scanner()
        self._scan_mode = None

        self._dt = 0.1

    @property
    def dt(self):
        return self._dt
    
    @dt.setter
    def dt(self, dtime: int):

        """
        set sampling time

        dtime: int, sample time (in sec)
        """
        
        self._dt = dtime
    
    def add_mass(self, name: str, m: float, pos: list[float], d: float, anchored: bool = False) -> None:

        """
        add mass to the network

        name: str, mass name
        m: float, mass in kg
        pos: list[float], position [x, y, z]
        d: float, air friction factor
        anchored: bool, if True the mass is anchored
        """

        mass = Mass(name=name, m=m, pos=pos, d=d, anchored=anchored)
        self.masses[name] = mass

        self.mass_params[name] = {
            "weight": m,
            "start": pos,
            "anchored": anchored
            }

        self.masses_motion[name] = {
            "x": [],
            "y": [],
            "z": [],
            "xyz": []
        }
        
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
            "lenght": length,
            "link": f"{self.masses[m1].name} < -- > {self.masses[m2].name}"
        }
    
    def add_damper(self, name: str, c: float, spring: str) -> None:

        """
        add damper to the network

        name: str, damper name
        c: float, damping factor
        spring: str, name of spring to add the damper
        """

        damper = Damper(c=c, m1=self.springs[spring].m1, m2=self.springs[spring].m2)
        self.dampers[name] = damper
        self.spring_params[spring].update({"damper": name, "c": c})

    def add_external_force(self, name: str, direction: list[float]) -> None:

        """
        add external force to the network

        name: str, force name
        direction: list[float] -> [x, y, z]
        """
        
        self.external_forces[name] = direction
    
    def __generate_external_force(self):
        for force in self.external_forces:
            f = np.array(self.external_forces[force], dtype=float)
            for mass in self.masses:
                f /= self.masses[mass].m
                self.masses[mass].apply_force(f)

    
    def add_hammer(self, hammer_path: list[tuple], shape: str, mode: str = "one_shot", **kwargs) -> None:

        """
        add hammer to the network

        hammer_path: list[tuple], masses to hit -> [(mass_name, coordinate), ...] 
        shape: str, hammer type -> ["rand", "sine", "sinc", "sig"]. If sig, mode = "always_on"
        mode: str, hammer mode ["one_shot", "always_on"]
        always_on: bool, if True strikes continuously
        kwargs:
            path: str, signal path -> sig shape
            sr: int, signal sample rate -> sig shape
            skip: float, skip time loaded audio signal, in sec. -> sig shape
        """
        
        self._hammer_mode = mode

        try:
            assert mode in ["one_shot", "always_on"]
            assert shape in ["sine", "sinc", "rand", "sig"] 
        except:
            print("[ERROR] mode or shape not implemented!\n")
            sys.exit(0)

        hammer = Hammer(masses_network=self.masses, hammer_path=hammer_path, shape=shape)

        sig_mode_params = {
            "path": "", 
            "sr": 44100, 
            "skip": 0
        }
        
        sig_mode_params = sig_mode_params | kwargs

        if hammer.shape == "sig":
            self._hammer_mode = "always_on"
            path = sig_mode_params["path"]
            sr = sig_mode_params["sr"]
            skip = sig_mode_params["skip"]
            hammer.hammer_audio_signal = (path, sr)
            hammer.skip_time = int(skip * sr)

        self.hammer = hammer

    def add_path(self, path: list[tuple]) -> None:

        """
        add path

        path: list[tuple], masses path
        """

        self.scan.path = path
    
    def generate_random_path(self, path_length: int, coordinate: str = "xyz") -> list[tuple]:

        """
        generate random path

        path_lenght: int, length of the path (< mass number) 
        coordinate: str, [x, y, z, xyz]

        return: list[tuple]
        """

        coord = ["x", "y", "z", "xyz"]

        try:
            assert coordinate in coord
            assert path_length <= len(self.masses)
        except:
            print("[ERROR] path_lenght must be less than number of masses; coordinate must be x, y, z or xyz or !\n")
            sys.exit(0)

        path_coord = list(self.masses.keys())
        path = []
        i = 0
        while i < path_length:
            m = np.random.choice(path_coord)
            c = np.random.choice(coord[:-1]) if coordinate == "xyz" else coordinate
            path.append((m, c))
            path_coord.pop(path_coord.index(m))
            i += 1
        return path
    
    def __reset_network(self) -> None:

        """
        reset network... take the network to zero time
        """

        for mass in self.masses:
            self.masses[mass].pos = self.masses[mass].start_pos
            self.masses[mass].vel = np.zeros(3)
            self.masses[mass].acc = np.zeros(3)
            for coord in self.masses_motion[mass]:
                self.masses_motion[mass][coord] = []
    
    def start_motion(self, maprange: list = None, use_hammer: bool = False) -> Generator:

        """
        set the network in motion

        use_hammer: bool, if True use the hammer

        return: Dict Generator with network motion dict (generator[mass_name][coordinate])
        """

        self.__reset_network()

        motion = {}
        for m in self.masses:
            motion[m] = {"x": None, "y": None, "z": None}

        while True:
            
            for spring in self.springs:
                self.springs[spring].generate_spring_force()

            for damper in self.dampers:
                self.dampers[damper].generate_drag_force()
            
            if use_hammer:
                self.hammer.generate_hammer_force()
                use_hammer = False if self._hammer_mode == "one_shot" else True
            
            if self.external_forces:
                self.__generate_external_force()
            
            for mass in self.masses:
                motion[mass]["x"] = self.masses[mass].pos[0] 
                motion[mass]["y"] = self.masses[mass].pos[1] 
                motion[mass]["z"] = self.masses[mass].pos[2] 
                
                self.masses[mass].update_position(dt=self._dt)
            
            yield motion
        
    def scan_network(self, masses_motion: Generator, scan_mode: str = "path") -> Generator:

        """
        scan path in a network

        masses_motion: Generator, masses motion Generator from start_motion method
        scan_mode: str, must be [path, network]. If path, scan only network path; if network scan all network -> return 2D vector

        return: Generator of 1D or 2D network motion vector
        """

        try:
            assert scan_mode in ["path", "network"]
        except:
            print("[ERROR] scan must be path or network!\n")
            sys.exit(0)
        
        self._scan_mode = scan_mode
        
        while True:
            motion = next(masses_motion)
            y = self.scan.rtscan(masses_motion=motion, scan_mode=scan_mode)
            yield y

    def plot_all_network(self, table: Generator,  axes_lim: tuple, refresh_time: int = 10) -> None:

        """
        plot network animation

        table: Generator, function table generator
        axes_lim: tuple, axes limit
        refresh_time: int, refresh time
        """

        fig, ax = plt.subplots(figsize=(15, 10))
        ax = plt.axes(projection="3d")

        def update(i):
            t = next(table)
            x, y, z = t[0], t[1], t[2]
            ax.clear()
            ax.set_title(f"NETWORK IN MOTION [N = {len(x)} MASSES]", weight="bold")
            ax.set_ylim(axes_lim)
            ax.set_zlim(axes_lim)
            ax.plot(x, y, z,"-o", c="k", lw=0.5)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
        
        animation = FuncAnimation(fig, update, interval=refresh_time)
        plt.show()
    
    def plot_network_path(self, table: Generator,  axes_lim: tuple, refresh_time: int = 10) -> None:

        """
        plot network animation

        table: Generator, function table generator
        axes_lim: tuple, axes limit
        refresh_time: int, refresh time
        """

        fig, ax = plt.subplots(figsize=(15, 10))

        def update(i):
            t = next(table)
            y = t
            x = [i for i in range(len(y))] 
            ax.clear()
            ax.set_title(f"PATH IN MOTION [N = {len(x)} MASSES]", weight="bold")
            ax.set_ylim(axes_lim)
            ax.plot(x, y,"-o", c="k", lw=0.5)
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

        animation = FuncAnimation(fig, update, interval=refresh_time)
        plt.show()



