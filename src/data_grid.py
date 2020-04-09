class DataGrid:
    def __init__(self, width, height, wraparound):
        self._width = width
        self._height = height
        self._wraparound = wraparound

        self._data = [[[] for j in range(width)] for i in range(height)]
        self._cell_groups = [[[] for j in range(width)] for i in range(height)]

        self._precompute_cell_groups()


    def push_data(self, data, coords):
        coords = self._process_coords(coords)
        cell = self._data[coords[0]][coords[1]]
        cell.append(data)


    def pop_data(self, data, coords):
        coords = self._process_coords(coords)
        cell = self._data[coords[0]][coords[1]]
        return cell.remove(data)


    def get_cell(self, coords):
        coords = self._process_coords(coords)
        return self._data[coords[0]][coords[1]]


    def get_cell_group(self, coords):
        x, y = coords[0] % self._height, coords[1] % self._width
        return self._cell_groups[x][y]


    def _process_coords(self, coords):
        if self._wraparound:
            coords[0] %= self._height
            coords[1] %= self._width

        return coords


    def _precompute_cell_groups(self):
        for x in range(self._height):
            for y in range(self._width):
                c1 = self.get_cell([x-1, y-1])
                c2 = self.get_cell([x-1, y  ])
                c3 = self.get_cell([x-1, y+1])
                c4 = self.get_cell([x  , y-1])
                c5 = self.get_cell([x  , y  ])
                c6 = self.get_cell([x  , y+1])
                c7 = self.get_cell([x+1, y-1])
                c8 = self.get_cell([x+1, y  ])
                c9 = self.get_cell([x+1, y+1])

                self._cell_groups[x][y] = [c1, c2, c3, c4, c5, c6, c7, c8, c9]
