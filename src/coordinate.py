class Coordinate():
    """
    Class for coordinate operations
    """
    up = (-1,0)
    left = (0,-1)
    down = (1,0)
    right = (0,1)
    upleft = (-1,-1)
    upright = (-1, 1)
    downleft = (1,-1)
    downright = (1,1)
    
    directions = [up, left, down, right]
    all_directions = [*directions, upleft, upright, downleft, downright]

    dirdict = {
        'up': up,
        'left': left,
        'down': down,
        'right': right,
    }
    
    def __init__(self, coords):
        """
        Given coords as a tuple of integers, sets x, y values
        """

        #Validate that provided coordinates is tuple of integers
        if not isinstance(coords, tuple):
            raise TypeError('Invalid coordinate input: Coordinate constructor requires coords of type tuple')
        elif not all([type(_) == int for _ in coords]):
             raise TypeError('Invalid coordinate input: Coords tuple must consist of two ints')

        #Assign x, y values of coordinate
        self.x = coords[0]
        self.y = coords[1]
        
    def dir_coords():
        """
        Returns coordinates in 4 directions
        """
        return [Coordinate(d) for d in Coordinate.directions]
    
    def all_dir_coords():
        """
        Returns coordinates in 8 directions
        """
        return [Coordinate(d) for d in Coordinate.all_directions]
    
    def _add(self, other):        
        """
        Given a tuple of a pair of integers, returns its addition to instance's coordinates
        """
        return (self.x + other[0], self.y + other[1])
    
    def __add__(self, other):
        """
        Passes through to _add fn
        """
        return self._add(other)
        
    
    def __radd__(self, other):
        """
        Passes through to _add fn
        """
        return self._add(other)
    
    def _sub(self, other):
        """
        Given other as a tuple of integers, returns the distance between other and instance
        """
        return ((other[0] - self.x)**2 + (other[1] - self.y)**2)**(1/2)
    
    def __sub__(self, other):
        """
        Passes through to _sub fn
        """
        return self._sub(other)
    
    def __rsub__(self, other):
        """
        Passes through to _sub fn
        """
        return self._sub(other)
        