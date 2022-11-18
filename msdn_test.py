from utils.msdn import MSDNetwork

net = MSDNetwork()

# masse
net.add_mass(name="m0", m=0.15, pos=[0, 0, 0], d=0.99, anchored=True)
net.add_mass(name="m1", m=0.15, pos=[1, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m2", m=0.15, pos=[2, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m3", m=0.15, pos=[3, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m4", m=0.15, pos=[4, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m5", m=0.15, pos=[5, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m6", m=0.15, pos=[6, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m7", m=0.15, pos=[7, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m8", m=0.15, pos=[8, 0, 0], d=0.99, anchored=False)
net.add_mass(name="m9", m=0.15, pos=[9, 0, 0], d=0.99, anchored=False)

# molle
net.add_spring(name="s0", k=0.3, length=0.01, m1="m0", m2="m1")
net.add_spring(name="s1", k=0.3, length=0.01, m1="m1", m2="m2")
net.add_spring(name="s2", k=0.3, length=0.01, m1="m2", m2="m3")
net.add_spring(name="s3", k=0.3, length=0.01, m1="m3", m2="m4")
net.add_spring(name="s4", k=0.3, length=0.01, m1="m4", m2="m5")
net.add_spring(name="s5", k=0.3, length=0.01, m1="m5", m2="m6")
net.add_spring(name="s6", k=0.3, length=0.01, m1="m6", m2="m7")
net.add_spring(name="s7", k=0.3, length=0.01, m1="m7", m2="m8")
net.add_spring(name="s8", k=0.3, length=0.01, m1="m8", m2="m9")

# smorzatori
net.add_damper(name="d1", c=0.1, spring="s1")
net.add_damper(name="d2", c=0.1, spring="s2")
net.add_damper(name="d3", c=0.1, spring="s3")
net.add_damper(name="d4", c=0.1, spring="s4")
net.add_damper(name="d5", c=0.1, spring="s5")
net.add_damper(name="d6", c=0.1, spring="s6")
net.add_damper(name="d7", c=0.1, spring="s7")

net.dt = 0.3
net.nresample = 1024

path = [("m0", "y"), ("m1", "y"), ("m2", "y"), ("m3", "y"), ("m4", "y"), ("m5", "y"), ("m6", "y"), ("m7", "y"), ("m8", "y"), ("m9", "y")]
net.add_path(path=path)

net.add_hammer(hammer_path=path, shape="rand", mode="one_shot")

table = net.run(use_hammer=True)
net.plot_network(table=table, ylim=[-3, 3], refresh_time=10)