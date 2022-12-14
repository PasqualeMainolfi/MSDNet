## **MSDNet MASS-SPRING-DAMPER NETWORK** 

MSDNet is a tool for building complex mass-spring-damper networks in python.  

1. Import and create network obj
```python
from msdnet import MSDNet

net = MSDNet()
```

2. Define network params
```python

N_MASS = 30 # number of masses
N_SPRING = N_MASS - 1 # number of springs
N_DAMPER = N_SPRING # number of dampers

DT = 0.5 # sample time

L = 0.1 # spring length
M = 8 # mass in kg
D = 0.999 # drag coeff
K = 2.5 # stiffness in N/m
C = 0.3 # damp coeff

net.dt = DT # set sample time
```

3. Add mass, spring and dampers to network
```python
"""
add masses:

name: str, mass name
m: float, mass in kg
pos: list[float], position [x, y, z]
d: float, damping factor
anchored: bool, if True the mass is anchored
"""
p = -0.5
for m in range(N_MASS):
    net.add_mass(name=f"m{m}", m=M, pos=[p, p, 0], d=D, anchored=False)
    p += 1/(N_MASS - 1)

"""
add springs

name: str, spring name
k: float, stiffness in N/m
length: float, spring length in m
m1: str, name of the mass anchored to the left
m2: str, name of the mass anchored to rhe right
"""
for s in range(N_SPRING):
    net.add_spring(name=f"s{s}", k=K, length=L, m1=f"m{s}", m2=f"m{s+1}")

"""
add dampers

name: str, damper name
c: float, damping factor
spring: str, name of spring to add the damper
"""
for d in range(N_DAMPER):
    net.add_damper(name=f"d{d}", c=C, spring=f"s{d}")
```

4. If you want... you can add any external force, ie: gravity
```python
"""add external force to the network

name: str, force name
direction: list[float] -> [x, y, z]
"""
net.add_external_force(name="gravity", direction=[0, -9.8, 0])
```
5. If you want... you can add a path 
```python
path = []
for i in range(N_MASS):
    p = (f"m{i}", "y")
    path.append(p)

net.add_path(path=path)
```
6. And a hammer to hit a network
```python
# generate random hammer path (masses to hit)
hammer_path = net.generate_random_path(path_length=7, coordinate="y")
# add hammer path to network
net.add_hammer_path(path=hammer_path)
# create hammer
net.add_hammer(shape="sine", mode="one_shot")
```
7. Active and scan network
```python
# activate
masses_motion = net.activate_network(use_hammer=True, clip_pos=(-1, 1))
# scan, return a array generator -> [net_motion: 2D vector of all network motion. ROW = number of masses, COL = 3 (x, y, z), path_motion: 1D vector path network motion]
# if smooth is True, smooth signal (see code)
net_scan = net.scan_network(masses_motion=masses_motion, smooth=False)
```
8. You can watch the network in motion
```python
# path motion
net.show_path_in_motion(table=net_scan, axes_lim=[-1, 1]) 
# or all network
net.show_network_in_motion(table=net_scan, axes_lim=[-1, 1]) 
``` 

some video example...



https://user-images.githubusercontent.com/53559987/203181291-58da1f3e-614f-4378-9784-d6e6ba9f1849.mp4



https://user-images.githubusercontent.com/53559987/203181391-29682941-ecaa-44e1-9544-cbdda019e736.mp4



for any questions: mnlpql@gmail.com  
© PasqualeMainolfi2022
