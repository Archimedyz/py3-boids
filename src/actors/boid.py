import config
from math import atan2, cos, pi, sin, sqrt
from sys import float_info

half_pi = pi / 2

class Boid:
    MAX_MAGNITUDE = 10
    VIEW_DISTANCE = 75
    SQUARED_VIEW_DISTANCE = VIEW_DISTANCE ** 2
    _VIEW_ANGLE = 0.75 * pi
    _D_THETA_PER_UPDATE = pi / 50
    _D_MAGNITUDE_PER_UPDATE = 0.075
    
    _next_id = 0

    def __init__(self, init_position, init_magnitude, init_theta):        
        self._pos = [init_position[0], init_position[1]] # force to a list to allow reassignment.
        self._magnitude = min(max(init_magnitude, 0), Boid.MAX_MAGNITUDE)
        self._theta = normalize_angle(init_theta)

        # "private" properties
        self._poly = [(8, 0), (-8, 6), (-8, -6)]
        self._color = (180, 0, 120)
        self._id = f'boid_{Boid._next_id}'

        # properties to help w/ computation later
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None

        # finally update the id counter
        Boid._next_id += 1 

    def reset_computation_properties(self):
        self.diff_pos = None
        self.squared_distance = None
        self.adjusted_angle = None


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
            # iterate over each boid in the group
            for other in group:
                # don't check self
                if other.get_id() == self._id:
                    continue

                self.reset_computation_properties()

                # if one of the rules is active, check for visibility. If the other boid is not visible, we cannot act on it.
                if (config.SEPARATION or config.ALIGNMENT or config.COHESION) and \
                    not self.can_see(other):
                    continue

                # follow the 3 rules if active
                if config.SEPARATION:
                    self.avoid_collision(other)
                if config.ALIGNMENT:
                    self.align(other)
            
        # get update the position based on the speed
        delta = to_vector(self._magnitude, self._theta)
        self._pos[0] += delta[0]
        self._pos[1] += delta[1]
    
    def update_speed(self, d_megnitude, d_theta):
        # update theta
        self._theta += d_theta
        self._magnitude += d_megnitude

    def can_see(self, other):
        # determine if the other's relative position to self
        o_pos = other.get_pos()
        self.diff_pos = (o_pos[0]-self._pos[0], o_pos[1]-self._pos[1])

        # if the other is too far from self, we cannot see it
        if self.diff_pos[0] > Boid.VIEW_DISTANCE or \
            self.diff_pos[1] > Boid.VIEW_DISTANCE:
            return False
        
        # now we can compute and store the distance squared
        self.squared_distance = self.diff_pos[0]**2 + self.diff_pos[1]**2
        if self.squared_distance > Boid.SQUARED_VIEW_DISTANCE:
            return False

        # determine the other boid's angle relative to self
        if self.diff_pos[0] == 0:
            angle_from_boid = half_pi if self.diff_pos[1] >= 0 else -half_pi
        else:
            angle_from_boid = atan2(self.diff_pos[1], self.diff_pos[0])

        # adjust relative angle
        self.adjusted_angle = normalize_angle(angle_from_boid - self._theta)
        
        # if we cannot see the other boid, do nothing
        if self.adjusted_angle >= Boid._VIEW_ANGLE or self.adjusted_angle <= -Boid._VIEW_ANGLE:
            return False

        # we can see the other boid!
        self._color = (180, 0, 120)

        return True

    def avoid_collision(self, other):
        # get the other's adjusted vector angle 
        o_vec = other.get_vec()
        o_adjusted_theta = normalize_angle(o_vec[1] - self._theta)

        ## first we consider some edge cases
        if float_equals(self.adjusted_angle, 0): 
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
        if not in_range(o_adjusted_theta, (0, normalize_angle(pi + self.adjusted_angle))):
            return
    
        # finally, since a collision may occur, we veer away from the other boid
        if self.adjusted_angle <= 0:
            self._theta += Boid._D_THETA_PER_UPDATE
        else:
            self._theta -= Boid._D_THETA_PER_UPDATE

    def align(self, other):
        # we should only try to align with boids going in the same general direction
        # the rule will be that the angle difference cannot be more than pi/2
        o_vec = other.get_vec()
        angle_diff = o_vec[1] - self._theta

        # the absolute value must be less than pi/2
        if not -pi/2 <= angle_diff <= pi/2:
            return

        # optionally, if both boids are already going in the same direction, there is nothing to do.
        if float_equals(angle_diff, 0):
            return

        # otherwise, we will try to fall into it's trajectory, but based on our distance to it.
        multiplier = 1 if self.squared_distance < 1 else 1 / sqrt(self.squared_distance)
        self._theta += angle_diff * multiplier

        

# END class Boid

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
