import time
import pygame
from math import pi, atan2
from pygame.locals import *
from random import random, randint

from actors.boid import Boid
from partition_grid import PartitionGrid

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

grid = PartitionGrid(grid_width, grid_height, True)

def grid_func(boid):
    def func():
        pos = boid.get_pos()
        return [int(pos[1]) % grid_height, int(pos[0]) % grid_width]
    return func

def generate_boid():
    pos = [randint(0, screen_size[0]), randint(0, screen_size[1])]
    magnitude = Boid.MAX_MAGNITUDE * 0.75
    theta = 2 * random() * pi

    return Boid(pos, magnitude, theta)

def update(boids, delta_theta, delta_magnitude):
    for b in boids:
        # if b.get_id() == m_boid_id:
        #     b.update_speed(delta_magnitude, delta_theta)
        b_f = grid_func(b)
        grid.pop_data(b, b_f)

        surrounding_boids = grid.get_cell_group(b_f)

        b.update(surrounding_boids, screen_size)

        grid.push_data(b, grid_func(b))

def draw_boid(boid):
    # draw a boid to the screen
    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

def render(boids):
    # clear the screen
    screen.fill(bg_color)

    # render the boids
    for b in boids:
        draw_boid(b)

    #re-render
    pygame.display.update()

def main_loop():
    prev_update_time = prev_render_time = time.time()
    
    boids = [generate_boid() for i in range(BOID_COUNT)]

    for boid in boids:
        grid.push_data(boid, grid_func(boid))

    render(boids)

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
            update(boids, delta_theta, delta_magnitude)

            # update the prev time
            prev_update_time = time.time()

        # render if it's time
        if delta_render > delta_render_threshold:
            render(boids)

            # update the prev time
            prev_render_time = time.time()
    
    # end of main_loop()
        
print('Starting . . . ')

main_loop()

# clean up
pygame.display.quit()
pygame.quit()

print('Done!')