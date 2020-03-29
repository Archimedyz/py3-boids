import time
import pygame
from math import pi
from pygame.locals import *
from random import random, randint
import config
import sim_state

from actors.boid import Boid
from data_grid import DataGrid

# defaults/constants
BG_COLOR = (72, 72, 72)
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


def update():
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


def render_paused():
    pause_surface = pygame.Surface(SCREEN_SIZE, pygame.SRCALPHA)
    pause_surface.fill((*config.FONT_LIGHT_GRAY, 64))

    text_paused = FONT.render('PAUSED', True, config.FONT_LIGHT_GRAY)
    text_rect_paused = text_paused.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

    SCREEN.blit(pause_surface, (0, 0))
    SCREEN.blit(text_paused, text_rect_paused)


def render_config():
    text_separation = \
        FONT.render('[1] SEPARATION', True, config.FONT_GREEN if sim_state.SEPARATION else config.FONT_RED)
    text_rect_separation = text_separation.get_rect()
    text_rect_separation.x = 5
    text_rect_separation.y = 5

    text_alignment = \
        FONT.render('[2] ALIGNMENT', True, config.FONT_GREEN if sim_state.ALIGNMENT else config.FONT_RED)
    text_rect_alignment = text_alignment.get_rect()
    text_rect_alignment.x = 5
    text_rect_alignment.y = 25

    text_cohesion = \
        FONT.render('[3] COHESION', True, config.FONT_GREEN if sim_state.COHESION else config.FONT_RED)
    text_rect_cohesion = text_cohesion.get_rect()
    text_rect_cohesion.x = 5
    text_rect_cohesion.y = 45

    SCREEN.blit(text_separation, text_rect_separation)
    SCREEN.blit(text_alignment, text_rect_alignment)
    SCREEN.blit(text_cohesion, text_rect_cohesion)


def render():
    # clear the screen
    SCREEN.fill(BG_COLOR)

    # render the boids
    for boid in BOIDS:
        draw_boid(boid)

    if sim_state.PAUSED:
        render_paused()

    if sim_state.SHOW_CONFIG:
        render_config()

    #re-render
    pygame.display.update()


def reset_key_state(key_state, *exceptions):
    for key in key_state:
        if key in exceptions:
            continue
        key_state[key] = False


def process_events(key_state):
    # variables to track key release
    _1_released = False
    _2_released = False
    _3_released = False
    _c_released = False
    _p_released = False

    # check for events
    pygame.event.pump()
    keys = pygame.key.get_pressed()
    event_types = (e.type for e in pygame.event.get())

    # exit simulation, return -1 to signal termination
    if keys[K_ESCAPE] or keys[K_q] or (pygame.QUIT in event_types):
        return -1

    # check if pause was pressed
    if keys[K_p]:
        key_state['p'] = True
    elif key_state['p']:
        _p_released = True

    # toggle separation rule
    if keys[K_1]:
        key_state['1'] = True
    elif key_state['1']:
        _1_released = True

    # toggle alignment rule
    if keys[K_2]:
        key_state['2'] = True
    elif key_state['2']:
        _2_released = True

    # toggle cohesion rule
    if keys[K_3]:
        key_state['3'] = True
    elif key_state['3']:
        _3_released = True

    # toggle config display
    if keys[K_c]:
        key_state['c'] = True
    elif key_state['c']:
        _c_released = True

    # now that we know which keys have been released, we can act on them
    if _c_released:
        sim_state.SHOW_CONFIG = not sim_state.SHOW_CONFIG
        key_state['c'] = False

    if _p_released:
        sim_state.PAUSED = not sim_state.PAUSED
        key_state['p'] = False

    # if in paused state, return 1 to signal continue
    if sim_state.PAUSED:
        # reset the key state for boid controls to avoid weird behaior
        reset_key_state(key_state, 'p', 'c')
        return 1

    # process all events normally, return 0 to signal normal flow
    if _1_released:
        sim_state.SEPARATION = not sim_state.SEPARATION
        key_state['1'] = False

    if _2_released:
        sim_state.ALIGNMENT = not sim_state.ALIGNMENT
        key_state['2'] = False

    if _3_released:
        sim_state.COHESION = not sim_state.COHESION
        key_state['3'] = False

    return 0


def main_loop():
    prev_update_time = prev_render_time = time.time()

    render()

    delta_update_threshold = 1 / UPS
    delta_render_threshold = 1 / FPS

    keys_state = {
        '1': False,
        '2': False,
        '3': False,
        'c': False,
        'p': False,
    }

    exit_loop = False
    while not exit_loop:
        curr_time = time.time()

        # get the time elapsed since the last update and last render
        delta_update = curr_time - prev_update_time
        delta_render = curr_time - prev_render_time

        game_status = process_events(keys_state)

        if game_status == -1:
            break

        if game_status == 0:
            # update and process event if it's time
            if delta_update > delta_update_threshold:
                # update state
                update()

                # update the prev time
                prev_update_time = time.time()

        # render if it's time
        if delta_render > delta_render_threshold:
            #render state
            render()

            # update the prev time
            prev_render_time = time.time()
    # end of main_loop()


print('Starting . . . ')

BOIDS = [generate_rand_boid() for i in range(config.BOID_COUNT)]
# BOIDS = [Boid((100, 400), Boid.MAX_MAGNITUDE/4, 0), Boid((100, 300), Boid.MAX_MAGNITUDE/4, pi/4)]

main_loop()

# clean up
pygame.display.quit()
pygame.quit()

print('Done!')
