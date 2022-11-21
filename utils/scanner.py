"""
Scan the path from MSDNetwork
"""

import numpy as np
from scipy import signal, interpolate

# def inter(x, n):
#     k = n - 1
#     j = (len(x) * n) - k
#     y = np.zeros(j)
#     h = 0
#     for i in range(1, len(x)):
#         step = (x[i] - x[i - 1])/n
#         for m in range(n):
#             y[m + h] = x[i - 1] + (step * m)
#             y[h] = x[i - 1]
#         h += n
#     y[-1] = x[-1]
#     return y


class Scanner():
    def __init__(self) -> None:
        self.__path = None
        self.__vector_path = None
    
    @property
    def path(self):
        return self.__path
    
    @path.setter
    def path(self, path: list[float]) -> None:
        self.__path = path
        self.__vector_path = np.zeros(len(path))

    def __rtscan_path(self, masses_motion):

        v = self.__vector_path
        motion = masses_motion

        # scan path
        for n, path in enumerate(self.__path):
            mass, position = path[0], path[1]
            current_position = motion[mass][position]
            v[n] = current_position
        
        y = v
        return y
    
    def __rtscan_network(self, masses_motion):

        motion = masses_motion
        n_mass = len(motion)
        v = np.zeros((3, n_mass))

        index = {
            0: "x",
            1: "y",
            2: "z"
        }
        
        # all massee motion
        for i in range(3):
            for j, mass_name in enumerate(motion):
                v[i, j] = motion[mass_name][index[i]]

        y = v
        return y

    
    def rtscan(self, masses_motion: dict, scan_mode: str) -> list:

        

        """
        generates the function-table in real time

        masses_motion: dict, positions of the mass
        scan_mode: str, must be [path, network]. If path, scan only network path; if network scan all network -> return 2D vector

        return: 1D or 2D vector
        """

        if scan_mode == "path":
            y = self.__rtscan_path(masses_motion=masses_motion)
        else:
            y = self.__rtscan_network(masses_motion=masses_motion)

        return y






