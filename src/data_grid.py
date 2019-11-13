class DataGrid:
    def __init__(self, width, height, wraparound):
        self._width = width
        self._height = height
        self._wraparound = wraparound

        self._data = [[[] for j in range(width)] for i in range(height)]

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
        x, y = coords[0], coords[1]

        c1 = self.get_cell([x-1, y-1])
        c2 = self.get_cell([x-1, y  ])
        c3 = self.get_cell([x-1, y+1])
        c4 = self.get_cell([x  , y-1])
        c5 = self.get_cell([x  , y  ])
        c6 = self.get_cell([x  , y+1])
        c7 = self.get_cell([x+1, y-1])
        c8 = self.get_cell([x+1, y  ])
        c9 = self.get_cell([x+1, y+1])

        return c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9

    def _process_coords(self, coords):
        if self._wraparound:
            coords[0] %= self._height
            coords[1] %= self._width

        # TODO: throw error if out of bounds

        return coords

    def print_grid(self):
        for row in self._data:
            print(row)
