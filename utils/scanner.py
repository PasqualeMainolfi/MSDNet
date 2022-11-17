"""
Scan the path from MSDNetwork
"""

import numpy as np
from scipy import signal


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
    
    def rtscan(self, masses_motion: dict, maprange: list, nresample: int) -> list[float]:

        """
        generates the function-table in real time

        masses_motion: dict, positions of the mass
        maprange: list, range min and max
        nresample: int, resample function table to nresample (table length)

        return: list[float], function-table
        """
        
        motion = masses_motion
        for n, path in enumerate(self.__path):
            mass = path[0]
            position = path[1]
            current_position = motion[mass][position]
            self.__vector_path[n] = current_position
        
        y = signal.resample(self.__vector_path, nresample)
        y = np.interp(y, [y.min(), y.max()], maprange) if maprange is not None else y

        return y 

