"""
MSDNetwork components: mass, spring, damper and hammer

"""


import numpy as np
import librosa

def magnitude(v: list) -> float:
    eps = 1e-12
    m_ = np.linalg.norm(v)
    m = m_ if m_ != 0 else eps
    return m

class Mass():

    def __init__(self, name: str, m: float, pos: list[float], d: float, anchored: bool = False) -> None:

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
        self.anchored = anchored

        p = np.array(pos, dtype=float)
        self.start_pos = p.copy()

        self.pos = p
        self.acc = np.zeros(3)
        self.vel = np.zeros(3)

    # apply force
    def apply_force(self, force: list[float]) -> None:
        f = np.array(force, dtype=float)/self.m
        self.acc += f

    # update mass position
    def update_position(self, dt: float) -> None:

        if not self.anchored:

            self.vel = self.vel * self.d
            self.vel = self.vel + self.acc * dt
            self.pos = self.pos + self.vel * dt
        
        self.acc = np.zeros(3)


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
        force = force/mag
        force = force * self.k * x
        self.m1.apply_force(force)
        force *= -1
        self.m2.apply_force(force)


class Damper():

    def __init__(self, c: float, m1: Mass, m2: Mass) -> None:


        """
        Create damper

        c: float, drag coefficient
        m1: Mass, mass anchored to the left of the spring
        m2: Mass, mass anchored to the left of the spring
        """

        self.c = c
        self.m1 = m1
        self.m2 = m2

    def generate_drag_force(self) -> None:

        """
        F = 0.5 · pv^2 · C · A = -c·v^2
        """
        
        drag = np.subtract(self.m2.vel, self.m1.vel)
        mag = magnitude(v=drag)
        drag = drag/mag
        drag = drag * self.c * np.power(mag, 2)
        self.m1.apply_force(drag)
        drag *= -1
        self.m2.apply_force(drag)


class Hammer():

    def __init__(self, masses_network: dict, hammer_path: list[tuple], shape: str) -> None:


        """
        Create hammer

        mass_network: dict, network of connected masses and springs to be struck
        hit_mass: list[tuple] -> [(mass name, coordinate), ...], masses to be struck (hammer path)
        mode: str, type of hammer ["rand", "sine", "sinc", "sig"]
        """


        self.masses = masses_network
        self.shape = shape
        self.hammer_path = hammer_path
        self.__force_vector = np.zeros((len(self.hammer_path), 3))
        self.__audio_vector_index = 0
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
        return self.__audio_vector_index

    @skip_time.setter
    def skip_time(self, skip: float):
        
        """
        skip: float, skip samples in samples
        """
        
        self.__audio_vector_index = skip

    # generate hammer
    def _generate_displacement(self) -> None:

        coord = {
            "x": 0,
            "y": 1,
            "z": 2
        }

        q = len(self.hammer_path)
        
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

    # generate hammer force
    def generate_hammer_force(self) -> None:
        self._generate_displacement()
        for n, m in enumerate(self.hammer_path):
            self.masses[m[0]].apply_force(self.__force_vector[n])
