import numpy as np

def generate_random_path(masses: dict, path_length: int, coordinate: str = "xyz") -> list[tuple]:

    """
    generate random path

    masses: dict, masses network
    path_length: int, length of the path (< mass number) 
    coordinate: str, [x, y, z, xyz]

    return: list[tuple]
    """

    coord = ["x", "y", "z", "xyz"]

    try:
        assert coordinate in coord
        assert path_length <= len(masses)
    except:
        print("[ERROR] path_length must be less than number of masses; coordinate must be x, y, z or xyz or !\n")
        exit(0)

    path_coord = list(masses.keys())
    path = []
    i = 0
    while i < path_length:
        m = np.random.choice(path_coord)
        c = np.random.choice(coord[:-1]) if coordinate == "xyz" else coordinate
        path.append((m, c))
        path_coord.pop(path_coord.index(m))
        i += 1

    return path


def smooth_data(x: list[float], wlen: int) -> list[float]:
    win = np.ones(wlen)/wlen
    y = np.convolve(x, win, mode="same")
    return y