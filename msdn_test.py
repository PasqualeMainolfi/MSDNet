from utils.msdn import MSDNetwork

net = MSDNetwork()

# masse
net.add_mass(name="wall_sx", m=1, pos=[0, 1, 0], d=1, lock=True)
net.add_mass(name="m1", m=1, pos=[1, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m2", m=1, pos=[2, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m3", m=1, pos=[3, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m4", m=1, pos=[4, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m5", m=1, pos=[5, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m6", m=1, pos=[6, 1, 0], d=0.9999, lock=False)
net.add_mass(name="m7", m=1, pos=[7, 1, 0], d=0.9999, lock=False)
net.add_mass(name="wall_dx", m=1, pos=[8, 1, 0], d=1, lock=True)

# masse a terra y
net.add_mass(name="m8", m=1, pos=[1, 0, 0], d=1, lock=True)
net.add_mass(name="m9", m=1, pos=[2, 0, 0], d=1, lock=True)
net.add_mass(name="m10", m=1, pos=[3, 0, 0], d=1, lock=True)
net.add_mass(name="m11", m=1, pos=[4, 0, 0], d=1, lock=True)
net.add_mass(name="m12", m=1, pos=[5, 0, 0], d=1, lock=True)
net.add_mass(name="m13", m=1, pos=[6, 0, 0], d=1, lock=True)
net.add_mass(name="m14", m=1, pos=[7, 0, 0], d=1, lock=True)

# masse a terra z
# net.add_mass(name="m16", m=1, pos=[1, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m17", m=1, pos=[2, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m18", m=1, pos=[3, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m19", m=1, pos=[4, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m20", m=1, pos=[5, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m21", m=1, pos=[6, 1, -1], d=.9999, lock=True)
# net.add_mass(name="m22", m=1, pos=[7, 1, -1], d=.9999, lock=True)

# molle
net.add_spring(name="s_wall_sx", k=30, length=1, m1="m1", m2="wall_sx")
net.add_spring(name="s1", k=30, length=1, m1="m2", m2="m1")
net.add_spring(name="s2", k=30, length=1, m1="m3", m2="m2")
net.add_spring(name="s3", k=30, length=1, m1="m4", m2="m3")
net.add_spring(name="s4", k=30, length=1, m1="m5", m2="m4")
net.add_spring(name="s5", k=30, length=1, m1="m6", m2="m5")
net.add_spring(name="s6", k=30, length=1, m1="m7", m2="m6")
net.add_spring(name="s_wall_dx", k=30, length=1, m1="wall_dx", m2="m7")

# molle a terra y
net.add_spring(name="s7", k=30, length=1, m1="m1", m2="m8")
net.add_spring(name="s8", k=30, length=1, m1="m2", m2="m9")
net.add_spring(name="s9", k=30, length=1, m1="m3", m2="m10")
net.add_spring(name="s10", k=30, length=1, m1="m4", m2="m11")
net.add_spring(name="s11", k=30, length=1, m1="m5", m2="m12")
net.add_spring(name="s12", k=30, length=1, m1="m6", m2="m13")
net.add_spring(name="s13", k=30, length=1, m1="m7", m2="m14")

# molle a terra z
# net.add_spring(name="s14", k=10, length=1, m1="m1", m2="m16")
# net.add_spring(name="s15", k=10, length=1, m1="m2", m2="m17")
# net.add_spring(name="s16", k=10, length=1, m1="m3", m2="m18")
# net.add_spring(name="s17", k=10, length=1, m1="m4", m2="m19")
# net.add_spring(name="s18", k=10, length=1, m1="m5", m2="m20")
# net.add_spring(name="s19", k=10, length=1, m1="m6", m2="m21")
# net.add_spring(name="s20", k=10, length=1, m1="m7", m2="m22")

# smorzatori
net.add_damper(name="d1", c=0.0001, spring="s7")
net.add_damper(name="d2", c=0.0001, spring="s8")
net.add_damper(name="d3", c=0.0001, spring="s9")
net.add_damper(name="d4", c=0.0001, spring="s10")
net.add_damper(name="d5", c=0.0001, spring="s11")
net.add_damper(name="d6", c=0.0001, spring="s12")
net.add_damper(name="d7", c=0.0001, spring="s13")

# net.add_damper(name="d8", c=0.1, spring="s14")
# net.add_damper(name="d9", c=0.1, spring="s15")
# net.add_damper(name="d10", c=0.1, spring="s16")
# net.add_damper(name="d11", c=0.1, spring="s17")
# net.add_damper(name="d12", c=0.1, spring="s18")
# net.add_damper(name="d13", c=0.1, spring="s19")
# net.add_damper(name="d14", c=0.1, spring="s20")

net.dt = 10
net.nresample = 4096

path = [("wall_sx", "z"), ("m1", "z"), ("m2", "z"), ("m3", "z"), ("m4", "z"), ("m5", "z"), ("m6", "z"), ("m7", "z"), ("m5", "z"), ("m6", "z"), ("m7", "z"), ("m4", "z"), ("m5", "z"), ("m6", "z"), ("wall_dx", "z")]
net.add_path(path=path)

hammer_path = net.generate_random_path(path_length=10, coordinate="z")
net.add_hammer(hammer_path=hammer_path, shape="sine", mode="one_shot")

table = net.run(use_hammer=True)
net.plot_network(table=table, ylim=[-1, 1], refresh_time=10)