"""
Scan the path from MSDNetwork
"""

import numpy as np
import sys

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
    def __init__(self, path: list[tuple]) -> None:
        self.path = path
    
    def rtscan(self, masses_motion):

        """
        generates the function-table in real time

        masses_motion: dict, positions of the mass
        scan_mode: str, must be [path, network]. If path, scan only network path; if network scan all network -> return 2D vector

        return: 1D or 2D vector
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
        
        path_motion = None if self.path is None else np.zeros(len(self.path))

        if path_motion is not None:
            # path motion
            for n, path in enumerate(self.path):
                mass, position = path[0], path[1]
                current_position = motion[mass][position]
                path_motion[n] = current_position
        
        return net_motion, path_motion





