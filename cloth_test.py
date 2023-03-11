from msdnet import Cloth
import pygame as pg

pg.init()

w, h = 800, 800
win = (w, h)

screen = pg.display.set_mode(win)
clock = pg.time.Clock()
fps = 60

M = 50
D = 0.981
K = 10
C = 10
R = 5
g = [0, 0, 0]

cloth = Cloth(n_masses=30, levels=5, center=(0, 0), scale=(1, 1))
net = cloth.generate_cloth(m=M, d=D, k=K, c=C, r=R)

net.add_gravity(g=g)
net.add_dt(1)

run = True
while run:

    network = net.run_network(use_hammer=False, acc_is_costant=False, clip_pos=(0, 1), canvas_size=win)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()

    for i, mass in enumerate(network):
        m = network[mass]
        x = m["x"] * w
        y = m["y"] * h

        pg.draw.circle(surface=screen, color=(255, 0, 0), center=(x, y), radius=R)

    clock.tick(fps)
    pg.display.update()
    screen.fill((0, 0, 0))

