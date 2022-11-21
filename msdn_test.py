from utils.msdn import MSDNetwork


net = MSDNetwork()

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

# masse
p = -0.5
for m in range(N_MASS):
    net.add_mass(name=f"m{m}", m=M, pos=[p, p, 0], d=D, anchored=False)
    p += 1/(N_MASS - 1)

net.lock_unlock_mass(name="m0", anchored=True)
net.lock_unlock_mass(name=f"m{N_MASS - 1}", anchored=True)

# add gravity
# net.add_external_force(name="gravity", direction=[0, -9.8, 0])

# molle
for s in range(N_SPRING):
    net.add_spring(name=f"s{s}", k=K, length=L, m1=f"m{s}", m2=f"m{s+1}")

# smorzatori
for d in range(N_DAMPER):
    net.add_damper(name=f"d{d}", c=C, spring=f"s{d}")

# path
path = []
for i in range(N_MASS):
    p = (f"m{i}", "y")
    path.append(p)

net.add_path(path=path)

hammer_path = net.generate_random_path(path_length=15, coordinate="y")
net.add_hammer(hammer_path=path, shape="sine", mode="one_shot")

masses_motion = net.start_motion(use_hammer=True)
scan = net.scan_network(masses_motion=masses_motion, scan_mode="network")

net.plot_all_network(table=scan, axes_lim=[-0.75, 0.75]) 