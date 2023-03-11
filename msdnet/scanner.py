"""
Scan the path from MSDNetwork
"""

import numpy as np

def smooth_data(x: list[float], wlen: int) -> list[float]:
    win = np.ones(wlen)/wlen
    y = np.convolve(x, win, mode="same")
    return y

class Scanner():
    def __init__(self, path: list[tuple]|None) -> None:
        self.path = path
    
    def rtscan(self, masses_motion, smooth: bool, wlen: int):

        """
        generates the function-table in real time

        masses_motion: dict, positions of the mass
        scan_mode: str, must be [path, network]. If path, scan only network path; if network scan all network -> return 2D vector
        smooth: bool, if True smooth motion
        wlen: int, if smooth == True, set filter window length (moving average). This param must be less than number of masses

        return: network motion, path motion
        """

        motion = masses_motion
        
        n_mass = len(motion)
        net_motion = np.zeros((3, n_mass))

        index = {
            0: "x",
            1: "y",
            2: "z"
        }
        
        # all masses motion
        for i in range(3):
            for j, mass_name in enumerate(motion):
                net_motion[i, j] = motion[mass_name][index[i]]

            if smooth:
                net_motion[i] = smooth_data(x=net_motion[i], wlen=wlen)
            
        path_motion = None if self.path is None else np.zeros(len(self.path))

        if path_motion is not None:
            # path motion
            for n, path in enumerate(self.path):
                mass, position = path[0], path[1]
                current_position = motion[mass][position]
                path_motion[n] = current_position

            if smooth:
                path_motion = smooth_data(x=path_motion, wlen=wlen)
        
        return net_motion, path_motion





