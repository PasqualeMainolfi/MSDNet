"""
MSDN (Mass-Spring-Damper Network)

"""

from typing import Generator, Union
from utils.network_components import Mass, Spring, Damper, Hammer
from utils.scanner import Scanner
from utils.plot_network import PlotMSDNetwork
import numpy as np
import sys


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
        shape: str, hammer type -> ["rand", "sine", "sinc", "sig"]
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
        except:
            print("[ERROR] hammer mode not implemented!\n")
            sys.exit(0)

        hammer = Hammer(masses_network=self.masses, hammer_path=hammer_path, shape=shape)

        sig_mode_params = {
            "path": "", 
            "sr": 44100, 
            "skip": 0
        }
        
        sig_mode_params = sig_mode_params | kwargs

        if hammer.shape == "sig":
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

        path_lenght: int, length of the path
        coordinate: str, [x, y, z, xyz]

        return: list[tuple]
        """

        coord = ["x", "y", "z", "xyz"]

        try:
            assert coordinate in coord
        except:
            print("[ERROR] coordinate must be [x, y, z, xyz]!\n")
            sys.exit(0)
        
        path = []
        for i in range(path_length):
            m = np.random.choice(list(self.masses.keys()))
            c = np.random.choice(coord[:-1]) if coordinate == "xyz" else coordinate
            path.append((m, c))
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
    
    def run(self, maprange: list = None, use_hammer: bool = False, scanning: bool = True, plot_mode: bool = False) -> Union[Generator, dict]:

        """
        set the network in motion

        maprange: list or None, if not None rescale in range [min, max]
        use_hammer: bool, if True use the hammer
        scanning: bool, if True generate wavetable, False generate motion data
        plot_mode: bool, if True plot the animation

        return: Union[Iterator, dict]
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
            
            if scanning:
                ft = self.scan.rtscan(masses_motion=motion, maprange=maprange)
                y = ft
            else:
                y = motion
            
            yield y
    
    def plot_network(self, table: Generator, ylim: tuple, refresh_time: float) -> None:

        """
        plot network animation

        table: Generator, function table generator
        ylim: tuple, limit on y axis
        refresh_time: float, refresh time
        """

        n = len(self.scan.path)

        p = PlotMSDNetwork()
        p.rtplot(table=table, table_length=n, ylim=ylim, refresh_time=refresh_time)

            

    






