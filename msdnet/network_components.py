"""
MSDNetwork components: mass, spring, damper and hammer

"""


import numpy as np
import librosa

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

    # apply force
    def apply_force(self, force: list[float]) -> None:
        f = np.array(force, dtype=float)/self.m
        self.acc += f

    # update mass position using Verlet
    def update_position(self, dt: float, acc_is_costant: bool = False, clip_pos: tuple|None = None) -> None:

                
        if not self.anchored:
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



class Hammer():

    def __init__(self, masses_network) -> None:


        """
        Create hammer

        mass_network: dict, network of connected masses and springs to be struck
        hammer_path: list[tuple] -> [(mass name, coordinate), ...], masses to be struck (hammer path)
        shape: str, type of hammer ["rand", "sine", "sinc", "sig"]
        """


        self.masses = masses_network
        self.shape = None
        self.hammer_path = None

        self.one_shot = False
        self.mode = None
        self.hammer_rand_path = False
        self.hammer_rand_path_coordinate = "xyz"
        self.shot_prob = 0.01

    @property
    def hammer_audio_signal(self):
        return self.__hammer_audio_signal

    @hammer_audio_signal.setter
    def hammer_audio_signal(self, audio_param: tuple) -> None:

        """
        audio_param: tuple, path and sample rate of audio sig 
        """

        source, sr = audio_param
        sig, _ = librosa.load(source, sr=sr)
        self.__hammer_audio_signal = sig
        self.__len_sig = len(sig)
        self.__sig_sr = sr

    @property
    def skip_time(self):
        return self.__audio_vector_index

    @skip_time.setter
    def skip_time(self, skip: float):
        
        """
        skip: float, skip samples in samples
        """
        
        self.__audio_vector_index = skip

    # generate hammer
    def generate_shot(self) -> None:

        coord = {
            "x": 0,
            "y": 1,
            "z": 2
        }

        try:
            assert self.hammer_path is not None
        except:
            print("[ERROR] hammer path not found!\n")
            exit(0)
        
        q = len(self.hammer_path)
        self.__force_vector = np.zeros((q, 3))

        for n, m in enumerate(self.hammer_path):

            ndx = m[1]

            if self.shape == "rand":
                self.__force_vector[n][coord[ndx]] = np.random.uniform(low=-1, high=1)

            if self.shape == "sine":
                self.__force_vector[n][coord[ndx]] = np.sin(2 * np.pi * n/q)

            if self.shape == "sinc":
                if n != q//2:
                    self.__force_vector[n][coord[ndx]] = np.sin(np.pi * n/q)
                else:
                    self.__force_vector[n][coord[ndx]] = 1

            if self.shape == "sig":
                index_audio_vec = self.skip_time%self.__len_sig
                self.__force_vector[n][coord[ndx]] = self.hammer_audio_signal[index_audio_vec]
                # print(self.__count + self.skip_time)
                self.skip_time += 1

        if self.shape != "sig":
            fac = np.random.choice([1, -1])
            self.__force_vector *= fac

    # generate hammer force
    def generate_hammer_force(self) -> None:
        self.generate_shot()
        for n, m in enumerate(self.hammer_path):
            self.masses[m[0]].apply_force(self.__force_vector[n])
