"""
MSDN (Mass-Spring-Damper Network)

"""

from typing import Generator
from msdnet.network_components import Mass, Spring, Damper, Hammer
from msdnet.scanner import Scanner
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


class MSDNet():
    def __init__(self) -> None:
        
        self.masses = dict()
        self.springs = dict()
        self.dampers = dict()

        self.mass_params = dict() # mass parameters
        self.masses_motion = dict() # motion of masses
        self.spring_params = dict() # spring parameters

        self.external_forces = dict()

        self.hammer = Hammer(masses_network=self.masses)

        self.path = None

        self.__dt = 0.1

    @property
    def dt(self):
        return self.__dt
    
    @dt.setter
    def dt(self, dtime: float):

        """
        set sampling time

        dtime: int, sample time (in sec)
        """
        
        self.__dt = dtime
    
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
            "length": length,
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

    def add_external_force(self, name: str, direction: list[float], masses: str|list[str] = "all", mode: str = "always_on") -> None:

        """
        add external force to the network

        name: str, force name
        direction: list[float] -> [x, y, z]
        masses: str|list[str], "all" or list of masses. If "all", force is applied on all masses. It is possible, or, to pass the list of masses to which to apply the force
        mode: str, types of hammer shots ["one_shot", "always_on", "rand_shot"]:
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
                    ff = f/self.masses[mass].m
                    self.masses[mass].apply_force(ff)
            if isinstance(w, list):
                for mass in w:
                    ff = f/self.masses[mass].m
                    self.masses[mass].apply_force(ff)
            if mode in ["one_shot", "rand_shot"]:
                self.external_forces[force]["force"] *= 0
            if mode == "rand_shot":
                v, p = np.random.rand(), np.random.rand() * 0.01
                if v < p:
                    direc = np.random.choice([-1, 1])
                    self.external_forces[force]["force"] = direc * self.external_forces[force]["start_force"]

    
    def add_hammer(self, shape: str = "rand", mode: str = "one_shot", **kwargs) -> None:

        """
        add hammer to the network

        hammer_path: list[tuple], masses to hit -> [(mass_name, coordinate), ...] 
        shape: str, the shaope of the hammer head -> ["rand", "sine", "sinc", "sig"]. If sig, mode = "always_on"
        mode: str, types of hammer shots ["one_shot", "always_on", "rand_shot"]:
            one_shot -> apply force only once (first iteration)
            always_on -> apply force at each iteration
            rand_shot -> apply force probabilistically (see kwargs -> shot_prob)
        kwargs:
            path_to_sig: str, signal directory path -> sig shape
            sr: int, signal sample rate -> sig shape
            skip: float, skip time loaded audio signal, in sec. -> sig shape
            rand_path: bool, if True it change the hammer path randomly at each iteration, if False the path is always the same
            rand_path_coordinate: str, if True it change the hammer path coordinates randomly at each iteration, if False the coordinate is "xyz"
            shot_prob: float, 0.0 - 1.0 the hammer shot probability at each iteration in mode rand_shot
        """
        
        try:
            assert mode in ["one_shot", "always_on", "rand_shot"]
            assert shape in ["sine", "sinc", "rand", "sig"] 
        except:
            print("[ERROR] mode or shape not yet implemented!\n")
            exit(0)
        
        try:
            assert self.hammer.hammer_path is not None
        except:
            print("[ERROR] hammer path not found!\n")
            exit(0)

        self.hammer.mode = mode
        self.hammer.shape = shape

        params = {
            "path_to_sig": "", 
            "sr": 44100, 
            "skip": 0,
            "rand_path": False,
            "rand_path_coordinate": "xyz",
            "shot_prob": 0.01
        }
        
        params = params | kwargs

        if shape == "sig":
            self.__hammer_mode = "always_on"
            path_to_sig = params["path_to_sig"]
            sr = params["sr"]
            skip = params["skip"]
            self.hammer.hammer_audio_signal = (path_to_sig, sr)
            self.hammer.skip_time = int(skip * sr)

        self.hammer.hammer_rand_path = params["rand_path"]
        self.hammer.hammer_rand_path_coordinate = params["rand_path_coordinate"]
        self.hammer.shot_prob = params["shot_prob"]
    
    def add_hammer_path(self, path: list[tuple]) -> None:

        """
        add hammer path

        path: list[tuple], masses hammer path
        """

        self.hammer.hammer_path = path

    def add_path(self, path: list[tuple]) -> None:

        """
        add path

        path: list[tuple], masses path
        """

        self.path = path
    
    def generate_random_path(self, path_length: int, coordinate: str = "xyz") -> list[tuple]:

        """
        generate random path

        path_length: int, length of the path (< mass number) 
        coordinate: str, [x, y, z, xyz]

        return: list[tuple]
        """

        coord = ["x", "y", "z", "xyz"]

        try:
            assert coordinate in coord
            assert path_length <= len(self.masses)
        except:
            print("[ERROR] path_length must be less than number of masses; coordinate must be x, y, z or xyz or !\n")
            exit(0)

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
    
    def activate_network(self, use_hammer: bool = False, clip_pos: tuple|None = None) -> Generator:

        """
        set the network in motion

        use_hammer: bool, if True use the hammer
        clip_pos: tuple or None, clip position in a range (min, max)

        return: Dict Generator (network motion -> dict[mass_name][coordinate])
        """

        # self.__reset_network()

        # set initial position before force
        motion = {}
        for m in self.masses:
            motion[m] = {
                "x": self.masses[m].pos[0], 
                "y": self.masses[m].pos[1], 
                "z": self.masses[m].pos[2]
            }

        shot = True

        while True:
            
            yield motion

            for spring in self.springs:
                self.springs[spring].generate_spring_force()

            for damper in self.dampers:
                self.dampers[damper].generate_drag_force()
            
            if use_hammer:
                if shot:
                    self.hammer.generate_hammer_force()
                    if self.hammer.mode in ["one_shot", "rand_shot"]:
                        shot = False
                if self.hammer.mode == "rand_shot":
                    shot = bool(np.random.binomial(1, p=self.hammer.shot_prob))
                    if shot and self.hammer.hammer_rand_path:
                        self.hammer.hammer_path = self.generate_random_path(
                            path_length=np.random.randint(low=1, high=len(self.masses) + 1),
                            coordinate=self.hammer.hammer_rand_path_coordinate
                        )
            
            if self.external_forces:
                self.__generate_external_force()
            
            for mass in self.masses:
                motion[mass]["x"] = self.masses[mass].pos[0] 
                motion[mass]["y"] = self.masses[mass].pos[1] 
                motion[mass]["z"] = self.masses[mass].pos[2] 
                
                self.masses[mass].update_position(dt=self.__dt)

                if clip_pos is not None:
                    min_clip, max_clip = clip_pos[0], clip_pos[1]
                    for i, p in enumerate(self.masses[mass].pos):
                        if p < min_clip: self.masses[mass].pos[i] = min_clip
                        if p > max_clip: self.masses[mass].pos[i] = max_clip

            
        
    def scan_network(self, masses_motion: Generator, smooth: bool = False, **kwargs) -> Generator:

        """
        scan path in a network

        masses_motion: Generator, generate this input from scan_network method
        smooth: bool, if True smooth motion
        kwargs: wlen, if smooth == True, set filter window length (moving average). This param must be less than number of masses

        return: Array Generator -> [net_motion: 2D vector of all network motion. ROW = number of masses, COL = 3 (x, y, z), path_motion: 1D vector path network motion]
        """
        
        scan = Scanner(path=self.path)

        kernel_len = {"wlen": 1}
        kernel_len = kernel_len|kwargs

        if smooth:
            try:
               assert kernel_len["wlen"] < len(self.masses)
            except:
                print("[ERROR] wlen must be less than a number of masses!\n")
                exit(0)
        
        while True:
            motion = next(masses_motion)
            net_scan, path_scan = scan.rtscan(masses_motion=motion, smooth=smooth, wlen=kernel_len["wlen"])

            if smooth:
                for m, mass in enumerate(self.masses):
                    if self.masses[mass].anchored:
                        for i in range(3):
                            net_scan[i, m] = self.masses[mass].start_pos[i]
                
                if path_scan is not None:

                    index = {
                        "x": 0,
                        "y": 1,
                        "z": 2
                    }
                    
                    for i, element in enumerate(self.path):
                        mass, coord = element[0], element[1]
                        if self.masses[mass].anchored:
                            path_scan[i] = self.masses[mass].start_pos[index[coord]]

            yield (net_scan, path_scan)

    def show_network_in_motion(self, table: Generator,  axes_lim: tuple, refresh_time: int = 10) -> None:

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
            x, y, z = t[0][0], t[0][1], t[0][2]
            ax.clear()
            ax.set_title(f"NETWORK IN MOTION [N = {len(x)} MASSES]", weight="bold")
            ax.set_ylim(axes_lim)
            ax.set_zlim(axes_lim)
            ax.plot(x, y, z, c="k", lw=0.7, marker="o", linestyle="dashed", markerfacecolor="r")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")
            ax.set_zlabel("Z")
        
        animation = FuncAnimation(fig, update, interval=refresh_time, repeat=False)
        plt.show()
    
    def show_path_in_motion(self, table: Generator,  axes_lim: tuple, refresh_time: int = 10) -> None:

        """
        plot path animation

        table: Generator, function table generator
        axes_lim: tuple, axes limit
        refresh_time: int, refresh time
        """

        fig, ax = plt.subplots(figsize=(15, 10))

        def update(i):
            t = next(table)
            y = t[1]
            x = [i for i in range(len(y))] 
            ax.clear()
            ax.set_title(f"PATH IN MOTION [N = {len(x)} MASSES]", weight="bold")
            ax.set_ylim(axes_lim)
            ax.plot(x, y, c="k", lw=0.3, marker="o", linestyle="dashed", markerfacecolor="r")
            ax.set_xlabel("X")
            ax.set_ylabel("Y")

        animation = FuncAnimation(fig, update, interval=refresh_time, repeat=False)
        plt.show()



