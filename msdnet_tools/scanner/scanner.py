"""

Scan the path from MSDNetwork

"""

import numpy as np
from msdnet_tools.generic_tools import generate_random_path, smooth_data

class Scanner():

    def __init__(self, masses: dict()) -> None:

        """
        scanner object

        masses: dict[MASSES], from MSDNet
        """

        self.masses = masses
    

    def __rtscan(self, masses_motion, path, smooth: bool, wlen: int):

        """
        generate scanning

        masses_motion: dict, positions of the mass
        path: list, path to scan
        smooth: bool, if True smooth motion
        wlen: int, if smooth == True, set filter window length (moving average). This param must be less than number of masses

        return: path motion
        """

        index = {"x": 0, "y": 1, "z": 2}
        
        path_motion = np.zeros(len(path))

        for n, p in enumerate(path):
            mass, position = p[0], p[1]
            current_position = masses_motion[mass][position]
            path_motion[n] = current_position

            if smooth:
                path_motion = smooth_data(x=path_motion, wlen=wlen)
        
        for i, p in enumerate(path):
            mass, coord = p[0], p[1]
            if self.masses[mass].anchored:
                path_motion[i] = self.masses[mass].start_pos[index[coord]]
        
        return path_motion
    

    def scan(self, masses_motion: dict, path: list[tuple], smooth: bool = False, **kwargs) -> list:

        """
        scan path in a network

        masses_motion: dict[MSDNet], receive from MSDNet run_network
        path: list, path to scan
        smooth: bool, if True smooth motion
        kwargs: wlen, if smooth == True, set filter window length (moving average). This param must be less than number of masses

        return: 1D vector scanned path
        """

        kernel_len = {"wlen": 1}
        kernel_len = kernel_len|kwargs

        if smooth:
            try:
               assert kernel_len["wlen"] < len(self.masses)
            except:
                print("[ERROR] wlen must be less than a number of masses!\n")
                exit(0)
        
            
        path_scan = self.__rtscan(masses_motion=masses_motion, path=path, smooth=smooth, wlen=kernel_len["wlen"])
        return path_scan


    def generate_rand_path(self, path_length: int, coordinate: str = "xyz") -> list[tuple]:

        """
        generate random path

        path_length: int, length of the path (< mass number) 
        coordinate: str, [x, y, z, xyz]

        return: list[tuple]
        """

        rand_path = generate_random_path(masses=self.masses, path_length=path_length, coordinate=coordinate)
        return rand_path

