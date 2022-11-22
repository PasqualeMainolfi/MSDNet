from utils.msdn import MSDNet


net = MSDNet()

N_MASS = 30
N_SPRING = N_MASS - 1
N_DAMPER = N_SPRING

DT = 0.5

l = 1/N_MASS

L = (l**2 + l**2)**0.5
M = 8
D = 0.999
K = 2.5
C = 0.3

net.dt = DT

# masses
p = -0.5
for m in range(N_MASS):
    net.add_mass(name=f"m{m}", m=M, pos=[p, p, 0], d=D, anchored=False)
    p += 1/(N_MASS - 1)

net.lock_unlock_mass(name="m0", anchored=True)
net.lock_unlock_mass(name=f"m{N_MASS - 1}", anchored=True)

# add gravity
net.add_external_force(name="gravity", direction=[0, -9.8, 0])

# springs
for s in range(N_SPRING):
    net.add_spring(name=f"s{s}", k=K, length=L, m1=f"m{s}", m2=f"m{s+1}")

# dampers
for d in range(N_DAMPER):
    net.add_damper(name=f"d{d}", c=C, spring=f"s{d}")

# path
path = []
for i in range(N_MASS):
    p = (f"m{i}", "y")
    path.append(p)

net.add_path(path=path)

hammer_path = net.generate_random_path(path_length=7, coordinate="y")
net.add_hammer_path(path=path)
net.add_hammer(shape="sine", mode="one_shot")

masses_motion = net.activate_network(use_hammer=True, clip_pos=(-1, 1))
net_scan = net.scan_network(masses_motion=masses_motion)

net.show_network_in_motion(table=net_scan, axes_lim=[-1, 1]) 
# net.show_path_in_motion(table=net_scan, axes_lim=[-1, 1]) 
