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

    def update(self, d_theta, d_megnitude):
        # update theta
        self._theta += d_theta
        self._magnitude += d_megnitude

        # enforce bounding
        self.enforce_bounds()

        # get update the position based on the speed
        delta = to_vector(self._magnitude, self._theta)
        self._pos[0] += delta[0]
        self._pos[1] += delta[1]

    def enforce_bounds(self):
        # safety check: limit theta to +/- 2 pi
        if self._theta > 2 * math.pi:
            self._theta -= 2 * math.pi
        elif self._theta < -2 * math.pi:
            self._theta += 2 * math.pi

        # safety check: limit magnitude to [0, 8]
        self._magnitude = min(max(self._magnitude, 0), 8)

def to_vector(magnitude, theta):
    return [magnitude * math.cos(theta), magnitude * math.sin(theta)]

def rotate(coord, theta):
    return [coord[0] * math.cos(theta) - coord[1] * math.sin(theta), coord[0] * math.sin(theta) + coord[1] * math.cos(theta)]

def transpose(coords, vec):
    updated_coords = []
    for point in coords:
        updated_coords.append([point[0] + vec[0], point[1] + vec[1]])
    return updated_coords