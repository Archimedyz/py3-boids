import time
import pygame
from math import pi, atan2
from pygame.locals import *

from actors.boid import Boid

# defaults/constants
bg_color = (159, 182, 205)
screen_size = (800, 600)
fps = 60

# setup
pygame.init()
screen = pygame.display.set_mode(screen_size)

font = pygame.font.Font(None, 24)
font_dark_red = (64, 0, 0) 
font_dark_blue = (0, 0, 64) 

pygame.display.set_caption('Boids')
screen.fill(bg_color)

m_boid_id = 'boid_0'

boids = [Boid([100, 500], 0, -pi/4), Boid([400, 300], 0, pi/4)]

# initialize the draw function


def update(boids, delta_theta, delta_magnitude):
    for b in boids:
        if b.get_id() == m_boid_id:
            b.update_speed(delta_magnitude, delta_theta)

        b.update(boids)

def draw_boid(boid):
    # draw a boid to the screen
    pygame.draw.polygon(screen, boid.get_color(), boid.get_poly())

def render_boid_info(boid):
    pos = boid.get_pos()
    vec = boid.get_vec()
    text = font.render(f'({pos[0]}, {pos[1]}) - [theta: {vec[1]}]', True, font_dark_red)
    text_rect = text.get_rect()
    text_rect.center = (screen_size[0] // 2, 10)

    screen.blit(text, text_rect)

def temp_render(boids):
    pos_0 = boids[0].get_pos()
    pos_1 = boids[1].get_pos()
    diff = (pos_1[0] - pos_0[0], pos_1[1] - pos_0[1])
    theta = atan2(diff[1], diff[0])
    text = font.render(f'~({diff[0]}, {diff[1]}) - [~theta: {theta}]', True, font_dark_blue)
    text_rect = text.get_rect()
    text_rect.center = (screen_size[0] // 2, 25)

    screen.blit(text, text_rect)

def render(boids):
    # clear the screen
    screen.fill(bg_color)

    # render the boids
    for b in boids:
        draw_boid(b)

        if(b.get_id() == m_boid_id):
            render_boid_info(b)
    
    temp_render(boids)

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