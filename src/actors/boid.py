import math

class Boid:
    def __init__(self, init_position, init_magnitude, init_theta, init_poly):
        self._pos = init_position
        self._magnitude = init_magnitude
        self._theta = init_theta
        self._poly = init_poly
        self._color = (180, 0, 120)
        
    def get_pos(self):
        return self._pos
    
    def get_color(self):
        return self._color

    def get_poly(self):
        a = rotate(self._poly[0], self._theta)
        b = rotate(self._poly[1], self._theta)
        c = rotate(self._poly[2], self._theta)
        return transpose([a, b, c], self._pos)

    def update(self, d_theta):
        # update theta
        self._theta += d_theta

        # safety checks
        if self._theta > 2 * math.pi:
            self._theta -= 2 * math.pi
        elif self._theta < -2 * math.pi:
            self._theta += 2 * math.pi
    
def to_vector(magnitude, theta):
    return [magnitude * math.cos(theta), magnitude * math.sin(theta)]

def rotate(coord, theta):
    return [coord[0] * math.cos(theta) - coord[1] * math.sin(theta), coord[0] * math.sin(theta) + coord[1] * math.cos(theta)]

def transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords