import time
import pygame
from math import pi
from pygame.locals import *
from random import random, randint
import config

from actors.boid import Boid
from data_grid import DataGrid

# defaults/constants
BG_COLOR = (159, 182, 205)
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 750
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
UPS = 60  # updates per second
FPS = 60  # frames per second
M_BOID_0 = 'boid_0'

# setup
pygame.init()
SCREEN = pygame.display.set_mode(SCREEN_SIZE)

FONT = pygame.font.Font(None, 24)
FONT_DARK_RED = (64, 0, 0)
FONT_DARK_GREEN = (0, 64, 0)
FONT_DARK_BLUE = (0, 0, 64)

pygame.display.set_caption('Boids')
SCREEN.fill(BG_COLOR)

GRID_WIDTH = SCREEN_WIDTH // Boid.VIEW_DISTANCE
if SCREEN_WIDTH % Boid.VIEW_DISTANCE != 0:
    GRID_WIDTH += 1

GRID_HEIGHT = SCREEN_HEIGHT // Boid.VIEW_DISTANCE
if SCREEN_HEIGHT % Boid.VIEW_DISTANCE != 0:
    GRID_HEIGHT += 1


def get_grid_coords(boid):
    pos = boid.get_pos()
    return [
        int((pos[1] // Boid.VIEW_DISTANCE) % GRID_HEIGHT),
        int((pos[0] // Boid.VIEW_DISTANCE) % GRID_WIDTH)
        ]


def generate_rand_boid():
    pos = [randint(0, SCREEN_SIZE[0]), randint(0, SCREEN_SIZE[1])]
    magnitude = Boid.MAX_MAGNITUDE
    theta = 2 * random() * pi

    return Boid(pos, magnitude, theta)


def update(delta_theta, delta_magnitude):
    # initialize the grid to improve updates
    grid = DataGrid(GRID_WIDTH, GRID_HEIGHT, True)
    for boid in BOIDS:
        grid.push_data(boid, get_grid_coords(boid))

    # instead of iterating over the boids and always fetching its cell
    # and surrounding cells, fetch each cell only once, and iterate
    # over the boids in each cell
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            # fetch the cell, and the cell-group
            cell = grid.get_cell([i, j])
            cell_group = grid.get_cell_group([i, j])

            # now iterate over the boids in this cell
            for boid in cell:
                boid.update(cell_group, SCREEN_SIZE)


def draw_boid(boid):
    # draw a boid to the screen
    pygame.draw.polygon(SCREEN, boid.get_color(), boid.get_poly())


def render_config():
    text_separation = \
        FONT.render('SEPARATION', True, FONT_DARK_GREEN if config.SEPARATION else FONT_DARK_RED)
    text_rect_separation = text_separation.get_rect()
    text_rect_separation.x = 5
    text_rect_separation.y = 5

    text_alignment = \
        FONT.render('ALIGNMENT', True, FONT_DARK_GREEN if config.ALIGNMENT else FONT_DARK_RED)
    text_rect_alignment = text_alignment.get_rect()
    text_rect_alignment.x = 5
    text_rect_alignment.y = 20

    text_cohesion = \
        FONT.render('COHESION', True, FONT_DARK_GREEN if config.COHESION else FONT_DARK_RED)
    text_rect_cohesion = text_cohesion.get_rect()
    text_rect_cohesion.x = 5
    text_rect_cohesion.y = 35

    SCREEN.blit(text_separation, text_rect_separation)
    SCREEN.blit(text_alignment, text_rect_alignment)
    SCREEN.blit(text_cohesion, text_rect_cohesion)


def render():
    # clear the screen
    SCREEN.fill(BG_COLOR)

    # render the boids
    for boid in BOIDS:
        draw_boid(boid)

    if config.SHOW_CONFIG:
        render_config()

    #re-render
    pygame.display.update()


def main_loop():
    prev_update_time = prev_render_time = time.time()

    render()

    delta_update_threshold = 1 / UPS
    delta_render_threshold = 1 / FPS

    _1_is_pressed = False
    _2_is_pressed = False
    _3_is_pressed = False
    _c_is_pressed = False

    exit_loop = False
    while not exit_loop:
        curr_time = time.time()

        # get the time elapsed since the last update and last render
        delta_update = curr_time - prev_update_time
        delta_render = curr_time - prev_render_time

        # check for events
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        event_types = (e.type for e in pygame.event.get())

        if keys[K_ESCAPE] or keys[K_q] or (pygame.QUIT in event_types):
            break

        # toggle separation rule
        if keys[K_1]:
            _1_is_pressed = True
        elif _1_is_pressed:
            config.SEPARATION = not config.SEPARATION
            _1_is_pressed = False

        # toggle alignment rule
        if keys[K_2]:
            _2_is_pressed = True
        elif _2_is_pressed:
            config.ALIGNMENT = not config.ALIGNMENT
            _2_is_pressed = False

        # toggle cohesion rule
        if keys[K_3]:
            _3_is_pressed = True
        elif _3_is_pressed:
            config.COHESION = not config.COHESION
            _3_is_pressed = False

        # toggle config display
        if keys[K_c]:
            _c_is_pressed = True
        elif _c_is_pressed:
            config.SHOW_CONFIG = not config.SHOW_CONFIG
            _c_is_pressed = False

        # update and process event if it's time
        if delta_update > delta_update_threshold:
            delta_theta = 0
            delta_magnitude = 0

            # turning
            if keys[K_LEFT]:
                delta_theta -= 0.0628
            if keys[K_RIGHT]:
                delta_theta += 0.0628

            # acceleration
            if keys[K_UP]:
                delta_magnitude += 0.075
            if keys[K_DOWN]:
                delta_magnitude -= 0.075

            # update state
            update(delta_theta, delta_magnitude)

            # update the prev time
            prev_update_time = time.time()

        # render if it's time
        if delta_render > delta_render_threshold:
            render()

            # update the prev time
            prev_render_time = time.time()
    # end of main_loop()


print('Starting . . . ')

BOIDS = [generate_rand_boid() for i in range(config.BOID_COUNT)]
# boids = [Boid((100, 400), Boid.MAX_MAGNITUDE/4, 0), Boid((100, 300), Boid.MAX_MAGNITUDE/4, pi/4)]

main_loop()

# clean up
pygame.display.quit()
pygame.quit()

print('Done!')
