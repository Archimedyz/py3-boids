class PartitionGrid:
    def __init__(self, width, height, wraparound):
        self._width = width
        self._height = height
        self._wraparound = wraparound
        
        self._data = [[[] for j in range(width)] for i in range(height)]
        
    def push_data(self, data, cell_func):
        c = self.get_coords(cell_func)

        cell = self._data[c[0]][c[1]]

        
        cell.append(data)

    def pop_data(self, data, cell_func):
        c = self.get_coords(cell_func)

        cell = self._data[c[0]][c[1]]

        return cell.remove(data)
        
    def get_cell_by_coordinates(self, x, y):
        if self._wraparound:
            x %= self._height
            y %= self._width

        # TODO: throw error if out of bounds

        return self._data[x][y]

    def get_cell(self, cell_func):
        c = self.get_coords(cell_func)

        return self._data[c[0]][c[1]]

    def get_cell_group(self, cell_func):
        coordinates = cell_func()

        x = coordinates[0]
        y = coordinates[1]

        c1 = self.get_cell_by_coordinates(x-1, y-1)
        c2 = self.get_cell_by_coordinates(x-1, y  )
        c3 = self.get_cell_by_coordinates(x-1, y+1)
        c4 = self.get_cell_by_coordinates(x  , y-1)
        c5 = self.get_cell_by_coordinates(x  , y  )
        c6 = self.get_cell_by_coordinates(x  , y+1)
        c7 = self.get_cell_by_coordinates(x+1, y-1)
        c8 = self.get_cell_by_coordinates(x+1, y  )
        c9 = self.get_cell_by_coordinates(x+1, y+1)
        
        return c1 + c2 + c3 + c4 + c5 + c6 + c7 + c8 + c9

    def get_coords(self, cell_func):
        coordinates = cell_func()
        
        if self._wraparound:
            coordinates[0] %= self._height
            coordinates[1] %= self._width
        
        # TODO: throw error if out of bounds

        return coordinates

    def print_grid(self):
        for row in self._data:
            print(row)

def f1():
    return [1, 1]
    
def f2():
    return [0, 0]
    
def f3():
    return [4, 2]
    
def f4():
    return [3, 7]

grid = PartitionGrid(3, 4, True)

grid.print_grid()

print(f'-----------------')

grid.push_data(1, f1)
grid.push_data(2, f2)
grid.push_data(3, f3)
grid.push_data(4, f4)
grid.push_data(7, f4)

grid.print_grid()

print(f'-----------------')

out = grid.get_cell_group(f4)

grid.print_grid()
print(f'> {out}')
print(f'-----------------')


