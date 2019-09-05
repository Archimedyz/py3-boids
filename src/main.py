import time
import pygame
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

def update(boid, delta_theta, delta_magnitude):
    boid.update(delta_theta, delta_magnitude)

def render(seconds_elapsed, boid):
    # clear the screen
    screen.fill(bg_color)

    # draw all objects tot he screen
    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

    #rerender 
    pygame.display.update()

def main_loop():
    exit_loop = False
    start_time = time.time()
    prev_time_s = start_time
    prev_time = start_time
    curr_time = start_time
    seconds_elapsed = 0
    boid = Boid([400, 300], 0, 0, ([8, 0], [-8, 6], [-8, -6]))
    render(seconds_elapsed, boid)
    while not exit_loop:
        delta_s = curr_time - prev_time_s
        delta = curr_time - prev_time
        if delta_s > 1:
            seconds_elapsed += 1
            prev_time_s = curr_time

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

            update(boid, delta_theta, delta_magnitude)
            render(seconds_elapsed, boid)
            prev_time = curr_time
        curr_time = time.time()
    
    return seconds_elapsed
        
print('Starting . . . ')

total_seconds = main_loop()

pygame.display.quit()
pygame.quit()

print(f'Done! Ran for {total_seconds} sec.')