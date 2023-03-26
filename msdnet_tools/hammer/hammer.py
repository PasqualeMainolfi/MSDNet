"""

Hammer object

"""

from msdnet_tools.generic_tools import generate_random_path
import numpy as np

#TODO: add force to all masses

class Hammer():

    def __init__(self) -> None:


        """
        Create hammer

        hammer_path: list[tuple] -> [(mass name, coordinate), ...], masses to be struck (hammer path)
        shape: str, type of hammer ["rand", "sine", "sinc"]
        """

        self.shape = None
        self.hammer_path = None
        self.one_shot = False
        self.mode = None
        self.hammer_rand_path = False
        self.hammer_rand_path_coordinate = "xyz"
        self.shot_prob = 0.01
        self.is_shot = True
    
    def create_hammer(self, shape: str = "rand", mode: str = "one_shot", rand_path: bool = False, rand_path_coordinate: str = "xyz", shot_prob: float = 0.01) -> None:

        """
        create hammer

        hammer_name: str, hammer name
        hammer_path: list[tuple], masses to hit -> [(mass_name, coordinate), ...] 
        shape: str, the shaope of the hammer head -> ["rand", "sine", "sinc", "sig"]. If sig, mode = "always_on"
        mode: str, types of hammer shots ["one_shot", "always_on", "rand_shot"]:
            one_shot -> apply force only once (first iteration)
            always_on -> apply force at each iteration
            rand_shot -> apply force probabilistically (see kwargs -> shot_prob)
        rand_path: bool, if True it change the hammer path randomly at each iteration, if False the path is always the same
        rand_path_coordinate: str, if True it change the hammer path coordinates randomly at each iteration, if False the coordinate is "xyz"
        shot_prob: float, 0.0 - 1.0 the hammer shot probability at each iteration in mode rand_shot
        """
        
        try:
            assert mode in ["one_shot", "always_on", "rand_shot"]
            assert shape in ["sine", "sinc", "rand"] 
        except:
            print("[ERROR] mode or shape not yet implemented!\n")
            exit(0)
        
        self.mode = mode
        self.shape = shape
        self.hammer_rand_path = rand_path
        self.hammer_rand_path_coordinate = rand_path_coordinate
        self.shot_prob = shot_prob
    

    def add_hammer_path(self, path: list[tuple]) -> None:

        """
        add hammer path

        path: list[tuple], hammer path
        """

        self.hammer_path = path


    def __generate_shot(self) -> None:

        try:
            assert self.hammer_path is not None
        except:
            print("[ERROR] hammer path not found!\n")
            exit(0)

        coord = {"x": 0, "y": 1, "z": 2}
        
        q = len(self.hammer_path)
        force_vector = np.zeros((q, 3))

        for n, m in enumerate(self.hammer_path):

            ndx = m[1]

            if self.shape == "rand":
                force_vector[n][coord[ndx]] = np.random.uniform(low=-1, high=1)

            if self.shape == "sine":
                force_vector[n][coord[ndx]] = np.sin(2 * np.pi * n/q)

            if self.shape == "sinc":
                if n != q//2:
                    force_vector[n][coord[ndx]] = np.sin(np.pi * n/q)
                else:
                    force_vector[n][coord[ndx]] = 1
        
        return force_vector


    def __generate_force(self, masses: dict) -> None:

        """
        generate and apply hammer force

        masses: dict, masses network
        """

        force_vector = self.__generate_shot()

        for n, m in enumerate(self.hammer_path):
            masses[m[0]].apply_force(force_vector[n])
        
        
    def apply_hammer_force(self, masses) -> None:

        try:
            assert self.hammer_path is not None
        except:
            print("[ERROR] hammer path not found!\n")
            exit(0)
        
        if self.is_shot:
            self.__generate_force(masses=masses)
            if self.mode == "one_shot":
                self.is_shot = False
        if self.mode == "rand_shot":
            self.is_shot = bool(np.random.binomial(1, p=self.shot_prob))
            if self.is_shot and self.hammer_rand_path:
                self.hammer_path = self.generate_rand_path(
                    masses=masses,
                    path_length=np.random.randint(low=1, high=len(self.masses) + 1),
                    coordinate=self.hammer_rand_path_coordinate
                )
    
    def generate_rand_path(self, masses: dict, path_length: int, coordinate: str = "xyz") -> list[tuple]:

        """
        generate random path

        masses: dict, masses network
        path_length: int, length of the path (< mass number) 
        coordinate: str, [x, y, z, xyz]

        return: list[tuple]
        """

        rand_path = generate_random_path(masses=masses, path_length=path_length, coordinate=coordinate)
        return rand_path