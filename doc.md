## **MSDNet**

```code
create masses-springs-dampers network

ATTRIBUTES:

=================

.masses -> dict of all masses obj
.springs -> dict of all springs obj
.dampers -> dict of all dampers obj

.mass_params -> dict of mass parameters (key: weights, start, anchored)
.masses_motion -> dict of motion of masses (keys: x, y, z, xyz)
.spring_params -> dict of spring parameters (keys: stiffness, length, link)

.external_forces -> dict of all extenal forces (keys: force -> keys: force, start_force, where, mode)

.path -> network path

=================

PROPERTY:

=================

dt -> sample time in sec.

=================

METHODS:

=================

add_mass(
    name: str, 
    m: float, 
    pos: list[float], 
    d: float, 
    anchored: bool = False
) -> None

add mass to the network

Args:
    name: str, mass name
    m: float, mass in kg
    pos: list[float], position [x, y, z]
    d: float, air friction factor
    anchored: bool, if True the mass is anchored

=================

lock_unlock_mass(
    name: str, 
    anchored: bool
) -> None

anchor the mass

Args:
    name: str, mass name
    anchored: bool, if True the mass is anchored

=================

add_spring(
    name: str, 
    k: float, 
    length: float, 
    m1: str, 
    m2: str
) -> None

add spring to the network

Args:
    name: str, spring name
    k: float, stiffness in N/m
    length: float, spring length in m
    m1: str, name of the mass anchored to the left
    m2: str, name of the mass anchored to rhe right

=================

add_damper(
    name: str, 
    c: float, 
    spring: str
) -> None

add damper to the network

Args:
    name: str, damper name
    c: float, damping factor
    spring: str, name of spring to add the damper

=================

add_external_force(
    name: str, 
    direction: 
    list[float], 
    masses: str|list[str] = "all", 
    mode: str = "always_on"
) -> None:

add external force to the network

Args:
    name: str, force name
    direction: list[float] -> [x, y, z]
    masses: str|list[str], "all" or list of masses. If "all", force is applied on all masses. It is possible, or, to pass the list of masses to which to apply the force
    mode: str, types of hammer shots ["one_shot", "always_on", "rand_shot"]:
        one_shot -> apply force only once (first iteration)
        always_on -> apply force at each iteration
        rand_shot -> apply force probabilistically

=================

add_hammer(
    shape: str = "rand", 
    mode: str = "one_shot", 
    **kwargs
) -> None:

add hammer to the network

Args:
    hammer_path: list[tuple], masses to hit -> [(mass_name, coordinate), ...] 
    shape: str, the shaope of the hammer head -> ["rand", "sine", "sinc", "sig"]. If sig, mode = "always_on"
    mode: str, types of hammer shots ["one_shot", "always_on", "rand_shot"]:
        one_shot -> apply force only once (first iteration)
        always_on -> apply force at each iteration
        rand_shot -> apply force probabilistically (see kwargs -> shot_prob)
    kwargs:
        path_to_sig: str, signal directory path -> sig shape
        sr: int, signal sample rate -> sig shape
        skip: float, skip time loaded audio signal, in sec. -> sig shape
        rand_path: bool, if True it change the hammer path randomly at each iteration, if False the path is always the same
        rand_path_coordinate: str, if True it change the hammer path coordinates randomly at each iteration, if False the coordinate is "xyz"
        shot_prob: float, 0.0 - 1.0 the hammer shot probability at each iteration in mode rand_shot

=================

add_hammer_path(
    path: list[tuple]
) -> None:

add hammer path

Args:
    path: list[tuple], masses hammer path

=================

add_path(
    path: list[tuple]
) -> None:

add path

Args:
    path: list[tuple], masses path

=================
    
generate_random_path(
    path_length: int,
    coordinate: str = "xyz"
    ) -> list[tuple]:

generate random path

Args:
    path_length: int, length of the path (< mass number) 
    coordinate: str, [x, y, z, xyz]

Return
    list[tuple] ->[("mass_name", "coordinate"), ...]

=================

activate_network(
    use_hammer: bool = False, 
    clip_pos: tuple|None = None
) -> Generator:

set the network in motion

Args:
    use_hammer: bool, if True use the hammer
    clip_pos: tuple or None, clip position in a range (min, max)

Return:
    Dict Generator (network motion -> dict[mass_name][coordinate])

=================

scan_network(
    masses_motion: Generator, 
    smooth: bool = False, 
    **kwargs
) -> Generator:

scan path in a network

Args:
    masses_motion: Generator, generate this input from scan_network method
    smooth: bool, if True smooth motion
    kwargs: wlen, if smooth == True, set filter window length (moving average). This param must be less than number of masses

Return
    Array Generator -> [net_motion: 2D vector of all network motion. ROW = number of masses, COL = 3 (x, y, z), path_motion: 1D vector path network motion]

=================

show_network_in_motion(
    table: Generator,  
    axes_lim: tuple, 
    refresh_time: int = 10
) -> None:


plot network animation

Args:
    table: Generator, function table generator
    axes_lim: tuple, axes limit
    refresh_time: int, refresh time

=================

show_path_in_motion(
    table: Generator,  
    axes_lim: tuple, 
    refresh_time: int = 10
) -> None:


plot path animation

Args:
    table: Generator, function table generator
    axes_lim: tuple, axes limit
    refresh_time: int, refresh time

=================

```