import time
import pygame
from math import pi, atan2
from pygame.locals import *
from random import random, randint

from actors.boid import Boid
from data_grid import DataGrid

# defaults/constants
bg_color = (159, 182, 205)
screen_width = 800
screen_height = 600
screen_size = (screen_width, screen_height)
ups = 60 # updates per second
fps = 60 # frames per second
m_boid_id = 'boid_0'

# setup
pygame.init()
screen = pygame.display.set_mode(screen_size)

font = pygame.font.Font(None, 24)
font_dark_red = (64, 0, 0)
font_dark_green = (0, 64, 0)
font_dark_blue = (0, 0, 64)

pygame.display.set_caption('Boids')
screen.fill(bg_color)

BOID_COUNT = 100

grid_width = screen_width // Boid.VIEW_DISTANCE
if screen_width % Boid.VIEW_DISTANCE != 0:
    grid_width += 1

grid_height = screen_height // Boid.VIEW_DISTANCE
if screen_height % Boid.VIEW_DISTANCE != 0:
    grid_height += 1

def get_grid_coords(boid):
    pos = boid.get_pos()
    return [int((pos[1] // Boid.VIEW_DISTANCE) % grid_height), int((pos[0] // Boid.VIEW_DISTANCE) % grid_width)]

def generate_rand_boid():
    pos = [randint(0, screen_size[0]), randint(0, screen_size[1])]
    magnitude = Boid.MAX_MAGNITUDE
    theta = 2 * random() * pi

    return Boid(pos, magnitude, theta)

def update(delta_theta, delta_magnitude):
    # initialize the grid to improve updates
    grid = DataGrid(grid_width, grid_height, True)
    for boid in boids:
        grid.push_data(boid, get_grid_coords(boid))

    # instead of iterating over the boids and always fetching its cell
    # and surrounding cells, fetch each cell only once, and iterate
    # over the boids in each cell
    for i in range(grid_height):
        for j in range(grid_width):
            # fetch the cell, and the cell-group
            cell = grid.get_cell([i, j])
            cell_group = grid.get_cell_group([i, j])

            # now iterate over the boids in this cell
            for boid in cell:
                # if boid.get_id() == m_boid_id:
                #     boid.update_speed(delta_magnitude, delta_theta)
                boid.update(cell_group, screen_size)

def draw_boid(boid):
    # draw a boid to the screen
    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

def render():
    # clear the screen
    screen.fill(bg_color)

    # render the boids
    for boid in boids:
        draw_boid(boid)

    #re-render
    pygame.display.update()

def main_loop():
    prev_update_time = prev_render_time = time.time()
    
    render()

    delta_update_threshold = 1 / ups
    delta_render_threshold = 1 / fps

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
            exit_loop = True

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

boids = [generate_rand_boid() for i in range(BOID_COUNT)]
# boids = [Boid((100, 400), Boid.MAX_MAGNITUDE/4, 0)]

main_loop()

# clean up
pygame.display.quit()
pygame.quit()

print('Done!')
