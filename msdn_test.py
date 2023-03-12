from msdnet import MSDNet


net = MSDNet()

N_MASS = 10
N_SPRING = N_MASS - 1
N_DAMPER = N_SPRING

DT = 0.7

l = 1/N_MASS

L = (l**2 + l**2)**0.5
M = 15
D = 0.99
K = 0.1
C = 15

net.dt = DT

# masses
p = 0
for m in range(N_MASS):
    net.add_mass(name=f"m{m}", m=M, pos=[p, .5, 0], r=0, d=D, anchored=False)
    p += 1/(N_MASS - 1)

net.lock_unlock_mass(name="m0", anchored=True)
net.lock_unlock_mass(name=f"m{N_MASS - 1}", anchored=True)

# add gravity
# net.add_external_force(name="gravity", direction=[0, -9.8, 0])

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

# net.add_hammer(hammer_name="sine_hammer", shape="sine", mode="always_on", rand_path=False, rand_path_coordinate="xyz", shot_prob=0.1)
# net.add_hammer_path(hammer_name="sine_hammer", path=path)

net.add_external_force(name="force 1", direction=[.5, -10, 0], masses="all", mode="one_shot")

masses_motion = net.activate_network(use_hammer=True, clip_pos=(-1, 1))
net_scan = net.scan_network(masses_motion=masses_motion, smooth=False, wlen=10)

net.show_network_in_motion(table=net_scan, axes_lim=[-1, 1]) # show 3D net motion
# net.show_path_in_motion(table=net_scan, axes_lim=[-1, 1]) # show path motion
# print(net.hammers["sine_hammer"].shot)
