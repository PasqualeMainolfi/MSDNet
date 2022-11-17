"""
MSDNetwork components: mass, spring, damper and hammer

"""


import numpy as np
import librosa

EPS = 1e-12

class Mass:

    def __init__(self, name: str, m: float, pos: list[float], d: float, lock: bool = False) -> None:

        """
        Create mass objcet

        name: str, mass name
        m: float, mass in kg
        pos: list[float], position [x, y, z]
        d: float, damping factor
        lock: bool, if True the mass is locked (anchored) 
        """

        self.name = name
        self.m = m
        self.d = d
        self.lock = lock

        self.start_pos = np.array(pos, dtype=float)

        self.pos = np.array(pos, dtype=float)
        self.acc = np.array([0.0, 0.0, 0.0], dtype=float)
        self.vel = np.array([0.0, 0.0, 0.0], dtype=float)

    # apply force
    def apply_force(self, force: list) -> None:
        f = np.array(force, dtype=float) / self.m
        self.acc += f

    # update mass position
    def update_position(self, dt: float) -> None:

        if not self.lock:

            self.vel = self.vel * self.d
            self.vel = self.vel + self.acc * dt
            self.pos = self.pos + self.vel * dt

        self.acc = self.acc * 0


class Spring:

    def __init__(self, name: str, k: float, length: float, m1: Mass, m2: Mass) -> None:


        """
        Create spring objcet

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
        force = np.subtract(self.m2.pos, self.m1.pos)
        mag = np.linalg.norm(force) + EPS
        ext = mag - self.length
        force = force/mag
        force = force * (self.k * ext)
        self.m1.apply_force(force)
        self.m2.apply_force(-1 * force)


class Damper:

    def __init__(self, c: float, m1: Mass, m2: Mass) -> None:


        """
        Create damper objcet

        c: float, damping factor
        m1: Mass, mass anchored to the left of the spring
        m2: Mass, mass anchored to the left of the spring
        """

        self.c = c
        self.m1 = m1
        self.m2 = m2

    def generate_drag_force(self) -> None:
        drag = np.subtract(self.m2.vel, self.m1.vel)
        mag = np.linalg.norm(drag) + EPS
        drag = drag/mag
        drag = drag * (self.c * np.power(mag, 2))
        self.m1.apply_force(drag)
        self.m2.apply_force(-1 * drag)


class Hammer:

    def __init__(self, masses_network: dict, hit_masses: list[tuple], shape: str) -> None:


        """
        Create hammer objcet

        mass_network: dict, network of connected masses and springs to be struck
        hit_mass: list[tuple] -> [(mass name, coordinate), ...], masses to be struck (hammer path)
        mode: str, type of hammer ["rand", "sine", "sinc", "sig"]
        """


        self.masses = masses_network
        self.shape = shape
        self.hit_masses = hit_masses
        self.__index = {"x": 0, "y": 1, "z": 2}
        self.__force_vector = np.zeros((len(self.hit_masses), 3))
        self.__index_sig_vector = 0
        self.__hammer_audio_signal = None
        self.__len_sig = 0
        self.__sig_sr = None

        self.one_shot = False

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
        return self.__index_sig_vector

    @skip_time.setter
    def skip_time(self, skip: float):
        
        """
        skip: float, skip samples in samples
        """
        
        self.__index_sig_vector = skip

    # generate hammer
    def _generate_hammer(self) -> None:
        q = len(self.hit_masses)
        for n, m in enumerate(self.hit_masses):

            if self.shape == "rand":
                self.__force_vector[n][self.__index[m[1]]] = np.random.uniform(low=-0.707, high=0.707)

            if self.shape == "sine":
                self.__force_vector[n][self.__index[m[1]]] = np.sin(2 * np.pi * n/q)

            if self.shape == "sinc":
                if n != q//2:
                    self.__force_vector[n][self.__index[m[1]]] = np.sin(np.pi * n/q)/(n + 1)
                else:
                    self.__force_vector[n][self.__index[m[1]]] = 1

            if self.shape == "sig":
                index_audio_vec = self.skip_time%self.__len_sig
                self.__force_vector[n][[self.__index[m[1]]]] = self.hammer_audio_signal[index_audio_vec]
                # print(self.__count + self.skip_time)
                self.skip_time += 1

    # generate hammer force
    def generate_hammer_force(self) -> None:
        self._generate_hammer()
        for n, m in enumerate(self.hit_masses):
            self.masses[m[0]].apply_force(self.__force_vector[n])
