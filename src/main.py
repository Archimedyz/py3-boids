import time
import pygame
from math import pi
from pygame.locals import *

from actors.boid import Boid

# defaults/constants
bg_color = (159, 182, 205)
screen_size = (800, 600)
fps = 60

# setup
pygame.init()
screen = pygame.display.set_mode(screen_size)
pygame.display.set_caption('Boids')
screen.fill(bg_color)

boids = [Boid([100, 500], 0, -pi/4), Boid([100, 100], 0, pi/4)]

# initialize the draw function


def update(boids, delta_theta, delta_magnitude):
    for b in boids:
        if b.get_id() == 'boid_0':
            b.update_speed(delta_magnitude, delta_theta)

        b.update(boids)

def draw_boid(boid):
    # draw a boid to the screen
    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

def render(boids):
    # clear the screen
    screen.fill(bg_color)

    # render the boids
    for b in boids:
        draw_boid(b)

    #rerender 
    pygame.display.update()

def main_loop():
    start_time = time.time()
    prev_time = start_time
    curr_time = start_time
        
    render(boids)
    
    exit_loop = False
    while not exit_loop:
        # get the time elapsed since the last update 
        delta = curr_time - prev_time
        
        # check for events
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        event_types = (e.type for e in pygame.event.get())

        if keys[K_ESCAPE] or (pygame.QUIT in event_types):
            exit_loop = True

        # update and render if it's time
        if delta > 1 / fps:
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

            # update and render state
            update(boids, delta_theta, delta_magnitude)
            render(boids)

            # update prev_time
            prev_time = curr_time
            
        curr_time = time.time()
    
    # end of main_loop()
        
print('Starting . . . ')

main_loop()

# clean up
pygame.display.quit()
pygame.quit()

print('Done!')