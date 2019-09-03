class Boid:
    def __init__(self, init_pos, init_vec):
        self._pos = init_pos
        self._vec = init_vec
        self._poly = [(self._pos[0], self._pos[1] - 6), (self._pos[0] - 3, self._pos[1] + 4), (self._pos[0] + 3, self._pos[1] + 4)] # top, left, right
        self._color = (180, 0, 120)
        
    def get_pos(self):
        return self._pos
    
    def get_vec(self):
        return self._vec

    def get_poly(self):
        return self._poly

    def get_color(self):
        return self._color

    def update(self):
        # update the position
        self._pos[0] += self._vec[0]
        self._pos[1] += self._vec[1]

        # update the polygon
        # TODO update orientation
        self._poly[0] = (self._pos[0], self._pos[1] - 6)
        self._poly[1] = (self._pos[0] - 3, self._pos[1] + 4)
        self._poly[2] = (self._pos[0] + 3, self._pos[1] + 4)
        