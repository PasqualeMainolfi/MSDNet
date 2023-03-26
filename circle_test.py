from msdnet_tools.shapes import Circle

M = 50
D = 0.981
K = 30
C = 10
R = 5
g = (0, 0, 0)

circle = Circle(n_masses=30, origin=(0.5, 0.5), scale=(0.5, 0.5), g=g, dt=1)
net = circle.generate_circle_msdnet(m=M, d=D, k=K, c=C, r=R, anchored_mass=[])
net.render(canvas_size=(800, 800), clip_pos=(0, 1), fps=60)
