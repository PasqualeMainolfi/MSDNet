from msdnet import Cloth

M = 50
D = 0.981
K = 10
C = 10
R = 5
g = (0, 0.000015, 0)

cloth = Cloth(n_masses=30, levels=10, origin=(0, 0.3), scale=(1, 0.1), g=g, dt=1)
net = cloth.generate_cloth(m=M, d=D, k=K, c=C, r=R)
net.render(canvas_size=(800, 800), clip_pos=(0, 1), fps=60)
