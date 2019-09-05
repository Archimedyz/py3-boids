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

def update(boid):
    boid.update()

def render(seconds_elapsed, boid):
    screen.fill(bg_color)

    text = font.render(f'{seconds_elapsed} fish . . .', True, (255, 255, 255), (159, 182, 205))
    textRect = text.get_rect()
    textRect.x = 5
    textRect.y = 5

    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

    pygame.display.update()

font = pygame.font.Font(None, 17)

def main_loop():
    exit_loop = False
    start_time = time.time()
    prev_time_s = start_time
    prev_time = start_time
    curr_time = start_time
    seconds_elapsed = 0
    boid = Boid([400, 300], 10, 0, ([60, 0], [-20, 40], [-20, -40]))
    render(seconds_elapsed, boid)
    while not exit_loop:
        delta_s = curr_time - prev_time_s
        delta = curr_time - prev_time
        if delta_s > 1:
            seconds_elapsed += 1
            prev_time_s = curr_time

        if delta > 1 / fps:
            update(boid)
            render(seconds_elapsed, boid)
            prev_time = curr_time
        curr_time = time.time()

        # check for events
        pygame.event.pump()
        keys = pygame.key.get_pressed()
        if keys[K_ESCAPE]:
            exit_loop = True
    
    return seconds_elapsed
        
print('Starting . . . ')

total_seconds = main_loop()

print(f'Done! Ran for {total_seconds} sec.')