import config
from math import pi, sin, cos, atan2
from sys import float_info

half_pi = pi / 2

class Boid:
    MAX_MAGNITUDE = 10
    VIEW_DISTANCE = 75
    _VIEW_ANGLE = 0.75 * pi
    _D_THETA_PER_UPDATE = pi / 50
    _D_MAGNITUDE_PER_UPDATE = 0.075
    
    _next_id = 0

    def __init__(self, init_position, init_magnitude, init_theta):        
        self._pos = [init_position[0], init_position[1]] # force to a list to allow reassignment.
        self._magnitude = min(max(init_magnitude, 0), Boid.MAX_MAGNITUDE)
        self._theta = normalize_angle(init_theta)
        self._poly = [(8, 0), (-8, 6), (-8, -6)]
        self._color = (180, 0, 120)
        self._id = f'boid_{Boid._next_id}'
        
        Boid._next_id += 1 
        
    def get_id(self):
        return self._id

    def get_pos(self):
        return self._pos
    
    def get_color(self):
        return self._color

    def get_vec(self):
        return (self._magnitude, self._theta)

    def get_poly(self):
        a = rotate(self._poly[0], self._theta)
        b = rotate(self._poly[1], self._theta)
        c = rotate(self._poly[2], self._theta)
        return transpose([a, b, c], self._pos)

    def enforce_bounds(self, screen_size):
        # safety check: limit theta to +/- pi
        self._theta = normalize_angle(self._theta)

        # safety check: limit magnitude to [0, 8]
        self._magnitude = min(max(self._magnitude, 0), Boid.MAX_MAGNITUDE)

        # wrapping behavior: wrap around to other end
        if self._pos[0] > screen_size[0] or self._pos[0] < 0:
            self._pos[0] %= screen_size[0] + 1
        if self._pos[1] > screen_size[1] or self._pos[1] < 0:
            self._pos[1] %= screen_size[1] + 1

    def update(self, boid_groups, screen_size):
        # enforce bounding
        self.enforce_bounds(screen_size)

        self._color = (0, 0, 0)

        # if the boid is not moving, it need not do anything to avoid the collision
        if self._magnitude == 0:
            return

        # iterate over each boid group
        for group in boid_groups:
            #iterate over each boid in the group
            for other in group:
                if other.get_id() == self._id: continue
                if config.Separation:
                    self.avoid_collision(other)
            
        # get update the position based on the speed
        delta = to_vector(self._magnitude, self._theta)
        self._pos[0] += delta[0]
        self._pos[1] += delta[1]
    
    def update_speed(self, d_megnitude, d_theta):
        # update theta
        self._theta += d_theta
        self._magnitude += d_megnitude

    def avoid_collision(self, other):
        # determine if the other's relative position to self
        o_pos = other.get_pos()
        diff_pos = (o_pos[0]-self._pos[0], o_pos[1]-self._pos[1])

        # if the other is too far from self, we cannot see it
        if diff_pos[0]**2 + diff_pos[1]**2 > Boid.VIEW_DISTANCE**2: return

        # determine the other boid's angle relative to self
        if diff_pos[0] == 0:
            angle_from_boid = half_pi if diff_pos[1] >= 0 else -half_pi
        else:
            angle_from_boid = atan2(diff_pos[1], diff_pos[0])

        # adjust relative angle
        adjusted_angle = normalize_angle(angle_from_boid - self._theta)
        
        # if we cannot see the other boid, do nothing
        if adjusted_angle >= Boid._VIEW_ANGLE or adjusted_angle <= -Boid._VIEW_ANGLE: return

        # we can see another boid!
        self._color = (180, 0, 120)

        # get the other's adjusted vector angle 
        o_vec = other.get_vec()
        o_adjusted_theta = normalize_angle(o_vec[1] - self._theta)

        ## first we consider some edge cases
        if float_equals(adjusted_angle, 0): 
            # case 1: boid is directly in front
            if o_vec[0] == 0:
                # case 1.1: stationary boid, move out of the way   
                self._theta += Boid._D_THETA_PER_UPDATE
                return
            elif float_equals(o_adjusted_theta, 0):                
                # case 1.2: moving away directly away. if too slow, dodge it otherwise no need to do anything
                if o_vec[0] < self._magnitude:
                    self._theta += Boid._D_THETA_PER_UPDATE
                return
        # note, we do not need to consider a boids directly behind as we cannot see them
        # at this point, we know there is no boid directly in front, but if it's not moving, don't need to avoid it.
        if o_vec[0] == 0:
            return

        # last thing to check is if a collision will occur
        if not in_range(o_adjusted_theta, (0, normalize_angle(pi + adjusted_angle))):
            return
    
        # finally, since a collision may occur, we veer away from the other boid
        self._theta += Boid._D_THETA_PER_UPDATE if adjusted_angle <= 0 else -Boid._D_THETA_PER_UPDATE


def to_vector(magnitude, theta):
    return [magnitude * cos(theta), magnitude * sin(theta)]

def rotate(coord, theta):
    return [coord[0] * cos(theta) - coord[1] * sin(theta), coord[0] * sin(theta) + coord[1] * cos(theta)]

def transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords

def normalize_angle(theta):
    if theta > pi:
        theta -= 2*pi
    elif theta <= -pi:
        theta += 2*pi    
    return theta

def float_equals(val1, val2):
    return -float_info.epsilon <= val1 - val2 <= float_info.epsilon

def in_range(value, range):
    if range[0] > range[1]:
        return range[0] >= value >= range[1]
    return range[1] >= value >= range[0]
