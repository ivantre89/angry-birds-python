import os
import sys
current_path = os.getcwd()
sys.path.insert(0, os.path.join(current_path, "../pymunk-4.0.0"))

import pygame
from pygame.locals import *
from pygame.color import *
import pymunk as pm
from pymunk import Vec2d
import math
from pymunk.pygame_util import from_pygame
import time


pygame.init()
screen = pygame.display.set_mode((1200, 650))
redbird = pygame.image.load("../resources/images/red-bird3.png").convert_alpha()
background2 = pygame.image.load(
    "../resources/images/background3.png").convert_alpha()
wood = pygame.image.load("../resources/images/wood.png").convert_alpha()
wood2 = pygame.image.load("../resources/images/wood2.png").convert_alpha()
sling_image = pygame.image.load(
    "../resources/images/sling-3.png").convert_alpha()
full_sprite = pygame.image.load(
    "../resources/images/full-sprite.png").convert_alpha()
rect = pygame.Rect(181, 1050, 50, 50)
cropped = full_sprite.subsurface(rect).copy()
pig_image = pygame.transform.scale(cropped, (30, 30))
rect = pygame.Rect(251, 357, 86, 22)
beam_image = wood.subsurface(rect).copy()
rect = pygame.Rect(16, 252, 22, 84)
column_image = wood2.subsurface(rect).copy()
clock = pygame.time.Clock()
running = True
# Physics stuff
space = pm.Space()
space.gravity = (0.0, -700.0)

balls = []
pigs = []
polys = []
beams = []
columns = []
poly_points = []
ball_number = 0
polys_dict = {}
mouse_distance = 0
rope_lenght = 90
angle = 0
x_pymunk = 0
y_pymunk = 0
x_pygame_mouse = 0
y_pygame_mouse = 0
count = 0
mouse_pressed = False
t1 = 0

# walls
static_body = pm.Body()
static_lines = [pm.Segment(static_body, (0.0, 060.0), (1200.0, 060.0), 0.0)]
for line in static_lines:
    line.elasticity = 0.95
    line.friction = 1
    line.collision_type = 3
space.add(static_lines)


def flipy(y):
    """Small hack to convert chipmunk physics to pygame coordinates"""
    return -y+600


def flipyv(v):
    h = 600
    return int(v.x), int(-v.y+h)


def vector(p0, p1):
    "(xo,yo), (x1,y1)"
    a = p1[0] - p0[0]
    b = p1[1] - p0[1]
    return (a, b)


def unit_vector(v):
    "(a,b)"
    h = ((v[0]**2)+(v[1]**2))**0.5
    if h == 0:
        h = 0.000000000000001
    ua = v[0] / h
    ub = v[1] / h
    return (ua, ub)


def to_pygame(p):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(p.x), int(-p.y+600)


def to_pygame2(x, y):
    """Small hack to convert pymunk to pygame coordinates"""
    return int(x), int(-y+600)


def create_poly(pos, length, height, mass=5.0):
    """Create the body and shape of a polygon"""
    moment = 1000
    body = pm.Body(mass, moment)
    body.position = Vec2d(pos)
    shape = pm.Poly.create_box(body, (length, height))
    shape.color = THECOLORS['blue']
    shape.friction = 0.5
    shape.collision_type = 2
    space.add(body, shape)
    return shape


def draw_poly(poly, element):
    """Draw beams and columns"""
    ps = poly.get_vertices()
    ps.append(ps[0])
    ps = map(flipyv, ps)
    ps = list(ps)
    color = THECOLORS["red"]
    pygame.draw.lines(screen, color, False, ps)
    if element == 'beams':
        p = poly.body.position
        p = Vec2d(p.x, flipy(p.y))
        angle_degrees = math.degrees(poly.body.angle) + 180
        rotated_logo_img = pygame.transform.rotate(beam_image, angle_degrees)

        offset = Vec2d(rotated_logo_img.get_size()) / 2.
        p = p - offset
        np = p
        # dy = math.sin(math.radians(angle_pure))*35
        # dx = math.cos(math.radians(angle_pure))*35
        screen.blit(rotated_logo_img, (np.x, np.y))
    if element == 'columns':

        p = poly.body.position
        p = Vec2d(p.x, flipy(p.y))
        angle_degrees = math.degrees(poly.body.angle) + 180
        rotated_logo_img = pygame.transform.rotate(column_image, angle_degrees)

        offset = Vec2d(rotated_logo_img.get_size()) / 2.
        p = p - offset
        np = p
        # dx = math.sin(math.radians(-angle_pure))*34
        # dy = math.cos(math.radians(-angle_pure))*34
        screen.blit(rotated_logo_img, (np.x, np.y))


def distance(xo, yo, x, y):
    """
    distance between players
    """
    dx = x - xo
    dy = y - yo
    d = ((dx ** 2) + (dy ** 2)) ** 0.5
    return d


def load_music():
    """Load the musics of a list"""
    song1 = '../resources/sounds/angry-birds.mp3'
    pygame.mixer.music.load(song1)
    pygame.mixer.music.play(-1)


def place_polys():
    p = (950, 80)
    columns.append(create_poly(p, 20, 85))
    p = (1010, 80)
    columns.append(create_poly(p, 20, 85))
    p = (980, 150)
    beams.append(create_poly(p, 85, 20))
    p = (950, 200)
    columns.append(create_poly(p, 20, 85))
    p = (1010, 200)
    columns.append(create_poly(p, 20, 85))
    p = (980, 240)
    beams.append(create_poly(p, 85, 20))


def create_bird(distance, angle, x, y):
    # ticks_to_next_ball = 500
    mass = 5
    radius = 12
    inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
    body = pm.Body(mass, inertia)
    body.position = x, y
    power = distance * 53
    impulse = power * Vec2d(1, 0)
    angle = -angle
    body.apply_impulse(impulse.rotated(angle))
    shape = pm.Circle(body, radius, (0, 0))
    shape.elasticity = 0.95
    shape.friction = 1
    shape.collision_type = 0
    space.add(body, shape)
    balls.append(shape)


def create_pigs(x, y):
    # ticks_to_next_ball = 500
    mass = 5
    radius = 14
    inertia = pm.moment_for_circle(mass, 0, radius, (0, 0))
    body = pm.Body(mass, inertia)
    body.position = x, y
    shape = pm.Circle(body, radius, (0, 0))
    shape.elasticity = 0.95
    shape.friction = 1
    shape.collision_type = 1
    space.add(body, shape)
    pigs.append(shape)


def post_solve_bird_pig(space, arbiter, surface=screen):
    a, b = arbiter.shapes
    bird_body = a.body
    pig_body = b.body
    p = to_pygame(bird_body.position)
    p2 = to_pygame(pig_body.position)
    r = 30
    pygame.draw.circle(surface, THECOLORS["black"], p, r, 4)
    pygame.draw.circle(surface, THECOLORS["red"], p2, r, 4)
    if b in pigs:
        pigs.remove(b)
    space.remove(b, b.body)


def post_solve_bird_wood(space, arbiter):
    if arbiter.total_impulse.length > 1200:
        a, b = arbiter.shapes
        if b in columns:
            columns.remove(b)
        if b in beams:
            beams.remove(b)
        space.remove(b, b.body)


def sling_action():
    global mouse_distance
    global rope_lenght
    global angle
    global x_pymunk
    global y_pymunk
    global x_pygame_mouse
    global y_pygame_mouse
    # Getting mouse position
    x_pymunk, y_pymunk = from_pygame(Vec2d(pygame.mouse.get_pos()), screen)
    x_pygame_mouse, y_pygame_mouse = to_pygame2(x_pymunk, y_pymunk)
    y_pygame_mouse = y_pygame_mouse + 52
    # Fixing bird to the sling rope
    v = vector((sling_x, sling_y), (x_pygame_mouse, y_pygame_mouse))
    uv = unit_vector(v)
    uv1 = uv[0]
    uv2 = uv[1]
    mouse_distance = distance(sling_x, sling_y, x_pygame_mouse, y_pygame_mouse)
    pu = (uv1*rope_lenght+sling_x, uv2*rope_lenght+sling_y)
    bigger_rope = 102
    x_redbird = x_pygame_mouse - 20
    y_redbird = y_pygame_mouse - 20
    if mouse_distance > rope_lenght:
        pux, puy = pu
        pux -= 20
        puy -= 20
        pul = pux, puy
        screen.blit(redbird, pul)
        pu2 = (uv1*bigger_rope+sling_x, uv2*bigger_rope+sling_y)
        pygame.draw.line(screen, (0, 0, 0), (sling2_x, sling2_y), pu2, 5)
        screen.blit(redbird, pul)
        pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y), pu2, 5)
    else:
        mouse_distance += 10
        pu3 = (uv1*mouse_distance+sling_x, uv2*mouse_distance+sling_y)
        pygame.draw.line(screen, (0, 0, 0), (sling2_x, sling2_y), pu3, 5)
        screen.blit(redbird, (x_redbird, y_redbird))
        pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y), pu3, 5)
    # Angle of impulse
    dy = y_pygame_mouse - sling_y
    dx = x_pygame_mouse - sling_x
    if dx == 0:
        dx = 0.00000000000001
    angle = math.atan((float(dy))/dx)


space.add_collision_handler(0, 1, post_solve=post_solve_bird_pig)
space.add_collision_handler(0, 2, post_solve=post_solve_bird_wood)
load_music()
place_polys()
create_pigs(980, 100)
create_pigs(985, 180)

while running:
    # Drawing background
    screen.fill((130, 200, 100))
    screen.blit(background2, (0, -50))
    sling_x, sling_y = 135, 450
    sling2_x, sling2_y = 160, 450
    rect = pygame.Rect(50, 0, 70, 220)
    screen.blit(sling_image, (138, 420), rect)
    # Input handling
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            running = False
        elif event.type == KEYDOWN and event.key == K_p:
            pygame.image.save(screen, "bouncing_balls.png")
        if pygame.mouse.get_pressed()[0]:
            mouse_pressed = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            mouse_pressed = False
            t1 = time.time()
            xo = 154
            yo = 156
            if mouse_distance > rope_lenght:
                mouse_distance = rope_lenght
            if x_pygame_mouse < sling_x+5:
                create_bird(mouse_distance, angle, xo, yo)
            else:
                create_bird(-mouse_distance, angle, xo, yo)

    if mouse_pressed:
        sling_action()
    else:
        if time.time() - t1 > 1:
            screen.blit(redbird, (130, 426))
        else:
            pygame.draw.line(screen, (0, 0, 0), (sling_x, sling_y-8),
                             (sling2_x, sling2_y-7), 5)
    # Draw stuff
    balls_to_remove = []
    for ball in balls:
        if ball.body.position.y < 0:
            balls_to_remove.append(ball)

        p = to_pygame(ball.body.position)
        x, y = p
        x -= 22
        y -= 20
        screen.blit(redbird, (x, y))
        pygame.draw.circle(screen, THECOLORS["blue"], p, int(ball.radius), 2)

    for ball in balls_to_remove:
        space.remove(ball, ball.body)
        balls.remove(ball)
    for line in static_lines:
        body = line.body
        pv1 = body.position + line.a.rotated(body.angle)
        pv2 = body.position + line.b.rotated(body.angle)
        p1 = to_pygame(pv1)
        p2 = to_pygame(pv2)
        pygame.draw.lines(screen, THECOLORS["lightgray"], False, [p1, p2])
    pigs_to_remove = []
    for pig in pigs:
        if pig.body.position.y < 0:
            pigs_to_remove.append(pig)

        p = to_pygame(pig.body.position)
        x, y = p
        x -= 22
        y -= 20
        screen.blit(pig_image, (x+7, y+4))
        pygame.draw.circle(screen, THECOLORS["blue"], p, int(pig.radius), 2)
    for column in columns:
        draw_poly(column, 'columns')
    for beam in beams:
        draw_poly(beam, 'beams')
    # Update physics
    dt = 1.0/60.0
    for x in range(1):
        space.step(dt)
    # Drawing second part of the sling
    rect = pygame.Rect(0, 0, 60, 200)
    screen.blit(sling_image, (120, 420), rect)
    # Flip screen
    pygame.display.flip()
    clock.tick(50)
    pygame.display.set_caption("fps: " + str(clock.get_fps()))
