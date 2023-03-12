from msdnet import String
import pygame as pg

pg.init()

w, h = 800, 800
win = (w, h)

screen = pg.display.set_mode(win)
clock = pg.time.Clock()
fps = 60

M = 50
D = 0.981
K = 30
C = 10
R = 10
g = (0, 0.000002, 0)

string = String(n_masses=30, origin=(0, 0.3), scale=(1, 0.5), g=g, dt=1)
net = string.generate_string(m=M, d=D, k=K, c=C, r=R, anchored_mass=[1, 30])

run = True
while run:

    for event in pg.event.get():
        if event.type == pg.QUIT:
            run = False
            pg.quit()

    network = net.run_network(use_hammer=False, acc_is_costant=False, clip_pos=(0, 1))
    net.render(surface=screen, canvas_size=(w, h), event=event)

    clock.tick(fps)
    pg.display.update()
    screen.fill((0, 0, 0))
