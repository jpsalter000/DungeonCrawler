import math

class Cell():
    """
    Manages attributes and storage of objects within a given board coordinate
    """
        
    CELL_TYPES = {
        1: {
            'file_name': 'tile_clear',
            'step_cost': 1
        },
        2: {
            'file_name': 'tile_debris',
            'step_cost': 2
        },
        3: {
            'file_name': 'wall',
            'step_cost': math.inf
        }
    }

    def __init__(self, cell_type=1):
        """
        Create Cell instance with no occupant, parameterized type
        """
        self._occupant = None
        self._cell_type = cell_type
        self.step_cost = Cell.CELL_TYPES[cell_type]['step_cost']
    
    def __str__(self):
        """
        Renders cell as character for its type
        """
        return Cell.CELL_TYPES[self._cell_type]['text_sprite']
    
    def _set_occupant(self, occupant):
        """
        Assigns occupant if unoccupied
        """
        if occupant is None:
            self._occupant = None
        else:
            if self._occupant is not None:
                raise AssertionError('No vacancy: Attempted to assign BoardObject to occupied cell')
            else:
                self._occupant = occupant
        
    def get_occupant(self):
        """
        Getter for _occupant instance var
        """
        return self._occupant
    
    def set_type(self,cell_type):
        """
        Sets cell's type if valid
        """
        if cell_type not in Cell.CELL_TYPES:
            raise AssertionError('Invalid cell type: Assigned type must be one of type enum {1,2,3}')
        self._cell_type = cell_type
        
    def get_type(self):
        return self._cell_type
        
    def __add__(self, other):
        """
        Shortcut for call to _set_occupant
        """
        self._set_occupant(other)
        return self
        
    def __sub__(self, other):
        """
        If other currently occupies cell, set occupant to None
        """
        if self._occupant == other:
            self._set_occupant(None)
        return self
