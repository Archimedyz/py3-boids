from math import pi, sin, cos, atan2

class Boid:
    _next_id = 0
    _view_angle = 1.5 * pi
    _view_distance = 75
    _d_theta_per_update = pi / 50
    _d_magnitude_per_update = 0.075

    def __init__(self, init_position, init_magnitude, init_theta):        
        self._pos = init_position
        self._magnitude = init_magnitude
        self._theta = init_theta
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

    def enforce_bounds(self):
        # safety check: limit theta to +/- pi
        self._theta = bound_theta(self._theta)

        # safety check: limit magnitude to [0, 8]
        self._magnitude = min(max(self._magnitude, 0), 8)

    def update(self, all_boids):
        # enforce bounding
        self.enforce_bounds()

        self._color = (0, 0, 0)

        # check for potential collisions
        for other in all_boids:
            if other.get_id() == self._id: continue
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
        if diff_pos[0]**2 + diff_pos[1]**2 > Boid._view_distance**2: return

        # determine the other boid's angle relative to self
        if o_pos[0]-self._pos[0] == 0:
            angle_from_boid = pi/2 if o_pos[1] >= self._pos[1] else -pi/2
        else:
            angle_from_boid = atan2(diff_pos[1], diff_pos[0])

        # adjust relative angle
        adjusted_angle = bound_theta(angle_from_boid - self._theta)
        
        # if we cannot see the other boid, do nothing
        if Boid._view_angle/2 <= adjusted_angle or adjusted_angle <= -Boid._view_angle/2: return

        # TEMP
        self._color = (180, 0, 120)

        # get the other's adjusted vector angle 
        o_vec = other.get_vec()
        o_adjusted_theta = bound_theta(o_vec[1] - self._theta)

        # if the relative position and relative vector are 


def to_vector(magnitude, theta):
    return [magnitude * cos(theta), magnitude * sin(theta)]

def rotate(coord, theta):
    return [coord[0] * cos(theta) - coord[1] * sin(theta), coord[0] * sin(theta) + coord[1] * cos(theta)]

def transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords

def bound_theta(theta):
    if theta > pi:
        theta -= 2*pi
    elif theta <= -pi:
        theta += 2*pi    
    return theta