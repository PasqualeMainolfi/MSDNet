from msdnet import MSDNet
import pygame as pg
import numpy as np

pg.init()

w, h = 800, 800
win = (w, h)

screen = pg.display.set_mode(win)
clock = pg.time.Clock()
fps = 60

net = MSDNet()

N_MASS = 30
N_SPRING = N_MASS - 1
N_DAMPER = N_SPRING

DT = 1

l = 1/(N_MASS + 1)

L = l
M = 50
D = 0.981
K = 10
C = 5
R = 5
g = (0, 0.00001, 0)

net.add_gravity(g=g)
net.add_dt(DT)

# masses level 1
p = l
for m in range(N_MASS):
    net.add_mass(name=f"l1m{m}", m=M, pos=[p, 0.1, 0], r=R, d=D, anchored=False)
    net.lock_unlock_mass(name=f"l1m{m}", anchored=True)
    p += l

# masse level 2
p = l
for m in range(N_MASS):
    net.add_mass(name=f"l2m{m}", m=M, pos=[p, 0.15, 0], r=R, d=D, anchored=False)
    p += l

p = l
for m in range(N_MASS):
    net.add_mass(name=f"l3m{m}", m=M, pos=[p, 0.20, 0], r=R, d=D, anchored=False)
    p += l

# springs level 1
for s in range(N_SPRING):
    net.add_spring(name=f"l1s{s}", k=K, length=L, m1=f"l1m{s}", m2=f"l1m{s+1}")

# springs level 2
for s in range(N_SPRING):
    net.add_spring(name=f"l2s{s}", k=K, length=L, m1=f"l2m{s + 1}", m2=f"l2m{s}")

# springs level 3
for s in range(N_SPRING):
    net.add_spring(name=f"l3s{s}", k=K, length=L, m1=f"l3m{s + 1}", m2=f"l3m{s}")


# springs level inter 1
for s in range(N_MASS):
    net.add_spring(name=f"li1s{s}", k=K, length=0.05, m1=f"l1m{s}", m2=f"l2m{s}")

# springs level inter 2
for s in range(N_MASS):
    net.add_spring(name=f"li2s{s}", k=K, length=0.05, m1=f"l2m{s}", m2=f"l3m{s}")




# dampers
for d in range(N_DAMPER):
    net.add_damper(name=f"l1d{d}", c=C, spring=f"l1s{d}")

# dampers
for d in range(N_DAMPER):
    net.add_damper(name=f"l2d{d}", c=C, spring=f"l2s{d}")

# dampers
for d in range(N_DAMPER):
    net.add_damper(name=f"l3d{d}", c=C, spring=f"l3s{d}")

# dampers
for d in range(N_MASS):
    net.add_damper(name=f"li1d{d}", c=C, spring=f"li1s{d}")

# dampers
for d in range(N_MASS):
    net.add_damper(name=f"li2d{d}", c=C, spring=f"li2s{d}")


N = N_MASS * 3
pos_mass_motion = [None for _ in range(N)]


run = True
while run:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()

    network = net.run_network(use_hammer=False, acc_is_costant=False, clip_pos=(0, 1))

    for mass in network:
        m = network[mass]
        x = m["x"] * w
        y = m["y"] * h

        pg.draw.circle(surface=screen, color=(255, 255, 0), center=(x, y), radius=R)

    clock.tick(fps)
    pg.display.update()
    screen.fill((0, 0, 0))

