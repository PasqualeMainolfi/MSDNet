from msdnet_tools.shapes import String
from msdnet_tools.hammer import Hammer

M = 50
D = 0.981
K = 30
C = 10
R = 5
g = (0, 0.0, 0)

# create Hammer
hammer = Hammer()
hammer.create_hammer(shape="sine", mode="rand_shot")

string = String(n_masses=30, origin=(0, 0.3), scale=(1, 0.5), g=g, dt=1)
net = string.generate_string_msdnet(m=M, d=D, k=K, c=C, r=R, anchored_mass=[1, 30])
hamemr_path = hammer.generate_rand_path(masses= net.masses, path_length=30, coordinate="y")
hammer.add_hammer_path(path=hamemr_path)
hammer.apply_hammer_force(masses=net.masses)
net.render(canvas_size=(800, 800), clip_pos=(0, 1), fps=60)
