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
g = [0, 0.000002, 0]

cloth = Cloth(n_masses=30, levels=15, origin=(0, 0.3), scale=(1, 0.5), g=g, dt=1)
net = cloth.generate_network(m=M, d=D, k=K, c=C, r=R)

run = True
while run:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()

    network = net.run_network(use_hammer=False, acc_is_costant=False, clip_pos=(0, 1), canvas_size=win)
    net.render(surface=screen, canvas_size=(w, h))

    clock.tick(fps)
    pg.display.update()
    screen.fill((0, 0, 0))
