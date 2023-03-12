from msdnet import MSDNet

class Shape:
    def __init__(self, n_masses: int, origin: tuple[float, float], scale: tuple[float, float], g: tuple[float, float, float], dt: float) -> None:
        
        """
        create Shape object

        n_masses: int, the number of masses
        center: tuple[float, float], center of cloth in cartesian coordinates between 0 and 1
        scale: tuple[float, flaot], scale factor on xy axis (must be between 0 and 1)
        g: tuple[float, float, float], gravity vector
        dt: float, delta time

        """
        
        self.n_masses = n_masses
        self.origin = origin
        self.size = scale

        self.g = g
        self.dt = dt


class Cloth(Shape):

    def __init__(self, n_masses: int, levels: int, origin: tuple[float, float], scale: tuple[float, float], g: tuple[float, float, float], dt: float) -> None:

        """
        create Cloth object

        levels: int, number of levels
        """
        
        super().__init__(n_masses, origin, scale, g, dt)
        
        if self.n_masses%levels != 0:
            raise("[ERROR] the number of masses must be a multiple of the levels number!")
            exit(0)
        
        self.levels = levels
        self.xlen = self.size[0]/(self.n_masses + 1)
        self.ylen = self.size[1]/(levels + 1)

    def generate_cloth(self, m: float, d: float, k: float, c: float, r: float) -> dict[MSDNet]:

        """
        generate network

        m: float, weight
        d: float, damping
        k: float, stiffness
        c: float, drag
        r: float, radius of mass

        """

        cloth = MSDNet()
        cloth.add_gravity(self.g)
        cloth.add_dt(self.dt)

        # add masses
        dy = self.ylen
        for i in range(self.levels):
            dx = self.xlen
            for j in range(self.n_masses):
                cloth.add_mass(name=f"l{i}m{j}", m=m, pos=[dx + self.origin[0], dy + self.origin[1], 0], r=r, d=d, anchored=False)
                if i == 0:
                    cloth.lock_unlock_mass(name=f"l{i}m{j}", anchored=True)
                dx += self.xlen
            dy += self.ylen
        
        # add springs and dampers hor
        for i in range(self.levels):
            for j in range(1, self.n_masses):
                cloth.add_spring(name=f"l{i}sh{j}", k=k, length=self.xlen, m1=f"l{i}m{j - 1}", m2=f"l{i}m{j}")
                cloth.add_damper(name=f"l{i}d{j}", c=c, spring=f"l{i}sh{j}")
        
        # add springs and dampers ver
        for i in range(1, self.levels):
            for j in range(self.n_masses):
                cloth.add_spring(name=f"l{i}sv{j}", k=k, length=self.ylen, m1=f"l{i - 1}m{j}", m2=f"l{i}m{j}")
                cloth.add_damper(name=f"l{i}d{j}", c=c, spring=f"l{i}sv{j}")

        return cloth

class String(Shape):

    def __init__(self, n_masses: int, origin: tuple[float, float], scale: tuple[float, float], g: tuple[float, float, float], dt: float) -> None:

        """
        create String object

        """

        super().__init__(n_masses, origin, scale, g, dt)

        self.xlen = self.size[0]/(self.n_masses + 1)
    
    def generate_network(self, m: float, d: float, k: float, c: float, r: float, anchored_mass: list[int] = []) -> dict[MSDNet]:

        """
        generate network

        m: float, weight
        d: float, damping
        k: float, stiffness
        c: float, drag
        r: float, radius of mass
        anchored_mass: list[int], specify wich masses you want to be anchored. For example, if you want mass 1 and mass 3 -> [1, 3] (from 1 to n_masses)

        """

        string = MSDNet()
        string.add_gravity(self.g)
        string.add_dt(self.dt)

        dx = self.xlen
        for i in range(self.n_masses):
            string.add_mass(name=f"m{i}", m=m, pos=[dx + self.origin[0], self.origin[1], 0], r=r, d=d, anchored=False)
            dx += self.xlen
        
        if anchored_mass:
            for n in anchored_mass:
                string.lock_unlock_mass(name=f"m{n - 1}", anchored=True)
        
        for i in range(1, self.n_masses):
            string.add_spring(name=f"s{i}", k=k, length=self.xlen, m1=f"m{i - 1}", m2=f"m{i}")
            string.add_damper(name=f"d{i}", c=c, spring=f"s{i}")

        return string



