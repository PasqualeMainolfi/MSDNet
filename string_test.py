from msdnet import String

M = 50
D = 0.981
K = 30
C = 10
R = 3
g = (0, 0.000002, 0)

string = String(n_masses=30, origin=(0, 0.3), scale=(1, 0.5), g=g, dt=1)
net = string.generate_string(m=M, d=D, k=K, c=C, r=R, anchored_mass=[1, 30])
net.render(canvas_size=(800, 800), clip_pos=(0, 1), fps=60)
