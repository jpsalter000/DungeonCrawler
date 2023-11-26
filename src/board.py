import math
from collections import defaultdict
from random import sample, shuffle
from copy import deepcopy

from coordinate import Coordinate
from cell import Cell


class Board():
    """
    Manages board generation, pathfinding
    """
    
    stage_types = {
        1: {'name': 'Warehouse',
            'cell_types': {
                1: 10,
                2: 2,
                3: 1,
                4: 1
                }
            },
        2: {'name': 'Datacenter',
            'cell_types': {
                1: 10,
                2: 2,
                3: 14,
                4: 2
            
            }
            },
        3: {'name': 'Ruins',
            'cell_types': {
                1: 2,
                2: 10,
                3: 3,
                4: 3
            }
            }
    }
    
    def init_grid(row_ct, col_ct, default_element=lambda: None):
        """
        Static function for grid intialization with 
            optional default element as callable
        Returns list of lists of dimension (row_ct, col_ct) where inner list element is given element
        """
        return [[default_element() for r in range(0, col_ct)] for c in range(0, row_ct)]
    
    def dupe_board_struct(self, default_element):
        """
        Returns duplicate of instance's board structure with 
            optional default element as callable
        """
        return Board.init_grid(self._rows, self._columns, default_element)
    
    def __init__(self, row_ct, col_ct, stage_type=1):
        """
        Creates game board with dimensions (row_ct, col_ct),
            initializes player and enemy character positions
            at bottom left and top right corners of game board, respectively
        """
        
        #Validate row, col ct params
        if type(row_ct) != int or type(col_ct) != int:
            raise TypeError('row and column values must be of type integer')
        if row_ct < 2 or col_ct < 2:
            raise AssertionError('board must be 2x2 or larger')
        
        #Create board grid, assign row, col instance variables
        self.board = Board.init_grid(row_ct, col_ct,Cell)
        self._columns = col_ct
        self._rows = row_ct
        
        self.positions = {
            0: [0,0],
            1: [row_ct-1, col_ct-1]
        }

        #Apply stage type config
        self.stage_type = Board.stage_types[stage_type]
        self.generate_board()       
        
    
    def wall_generator(poss_coords, wall_ct):
        """
        Helper function for placement of noncontinguous wall clusters
        """
        max_cluster_size = 6       
        
        #Create dict of coords with initial visited/placed values set to False
        coord_dict = defaultdict(lambda: None)
        coord_dict.update({coord: {'can_place': True, 'placed': False} for coord in poss_coords})
        
        while wall_ct >= 0 and len(poss_coords) >= 0:
            #Select an eligible cluster seed coordinate at random
            curr_coord = sample(list(poss_coords),1)[0]
            
            curr_cluster_size = 0
            reached_dead_end = False
            
            placed_coords = []
            while wall_ct >= 0 and curr_cluster_size <= 6 and reached_dead_end == False:
                #While the current cluster has not exceeded max cluster size and curr coord has eligible neighnors
                
                #Presume a dead end has been reached until negated by some wall placement in loop below
                reached_dead_end = True
                
                #Randomize order of searched directions
                shuffled_directions = Coordinate.dir_coords().copy()
                shuffle(shuffled_directions)
                for d in shuffled_directions:
                    #In each direction, search the possible coordinate and fetch its state if it exists
                    new_coord = d + curr_coord
                    coord_state = coord_dict[new_coord]
                    if coord_state is not None and not coord_state['placed'] and coord_state['can_place']:
                        #If the generated coordinate is in bounds and has not been filled or restricted, place wall
                        coord_state['placed'] = True
                        curr_cluster_size += 1
                        reached_dead_end = False
                        placed_coords.append(new_coord)
                        #Assign this coordinate to curr coord, skip to directional search for new curr coord
                        curr_coord = new_coord
                        wall_ct -= 1
                        break
            #Current wall cluster has completed (either by reaching max wall ct or reaching dead end)
            #   protect adjacent cells from placement to guarantee traversable stage
            #First, populate set of all coords adjacent to placed coords
            protected_coords = set()
            for coord in placed_coords:
                for d in Coordinate.all_dir_coords():
                    adjac_coord = d + curr_coord #(curr_coord[0] + d[0], curr_coord[1] + d[1])
                    protected_coords.add(adjac_coord)
            #Then, set can_place val of each coord to False if it exists
            for coord in protected_coords:
                if coord_dict[coord] is not None:
                    coord_dict[coord]['can_place'] = False
                    
            #Finally, remove protected coords from possible coords for placement of next cluster
            poss_coords -= protected_coords
            
        placed_coords = set([coord for coord, state in coord_dict.items() if state and state['placed'] == True]) 
        #Once all clusters have been placed, return list of all coordinates with placed=True (has wall)
        return set([coord for coord, state in coord_dict.items() if state and state['placed'] == True])                   
                    
            
        
    def generate_board(self):
        """
        Procedurally generates board environment
        """
        
        #Populate set of type assignment, wall placement coordinates
        available_coords = set()
        potential_wall_coords = set()
        for r in range(0, self._rows):
            for c in range(0, self._columns):
                available_coords.add((r, c))
                #Skip edge coordinates for wall placement
                if 0 not in [r,c] and c != self._columns - 1 and r != self._rows - 1:
                    potential_wall_coords.add((r,c))
                        
        #Fetch share of each cell type for board instance's stage type
        type_shares = self.stage_type['cell_types']
        
        #Calculate ct of cell type by its relative frequency
        stage_weight_denom = sum(type_shares.values())
        calc_freq = lambda x, y: int((x/stage_weight_denom) * len(y))
        
        #Calculate ct of debris, wall cell types
        wall_ct = calc_freq(type_shares[3], potential_wall_coords)
        
        #Generate coordinates for Wall assignment
        wall_coords = Board.wall_generator(potential_wall_coords, wall_ct)
        for coord in wall_coords:
            self.board[coord[0]][coord[1]].set_type(3) #Set type to 3 for Wall
        
        #Subtract coords of walls from candidate coordinates
        available_coords -= wall_coords
        
        #Caculate count of Debris type cells by relative share over total available coords
        debris_ct = calc_freq(type_shares[2], available_coords)
        
        #Randomly select N=debris_ct of remaining coords for Debris assignment
        debris_coords = sample(list(available_coords), debris_ct)
        for coord in debris_coords:
            self.board[coord[0]][coord[1]].set_type(2) #Set type to 2 for Debris           
        
        #Randomly select N=item_ct of available coords for Item placement
        #item_coords = random.sample( available_coords, item_ct)
        #for coord, item in it.zip(item_coords, Item.random_item_generator(item_ct)):
        #    self.board[coord[0]][coord[1]].place_item(item)
        
    def columns(self):
        """
        Getter for number of columns
        """
        return self._columns
    
    def rows(self):
        """
        Getter for number of rows
        """
        return self._rows    
    
    def render_board(self):
        """
        Renders board for printing to stdout
        """
        display = ""
        for ridx, row in enumerate(self.board):
            for cidx, cell in enumerate(row):
                #Append cell's text representation to out string
                display += str(cell)
            display += "\n"
        return display
        
            
    def step_allowed(self, cell_coord):
        """
        Checks if cell is in bounds and clear of any obstructions
        """
        
        row = cell_coord[0]
        col = cell_coord[1]        
        
        if not (0 <= row < self.rows()) or not (0 <= col < self.columns()):
            #If coords exceed board boundaries return False
            return False
        else:
            #Cell exists; check that cell is clear and cell is not wall type (type=3), return False if occupied
            cell = self.board[row][col]
            if cell.get_occupant() is not None or cell.get_type() == 3:
                return False            
        
        #Cell exists and is clear, so return True 
        return True            
        
    def find_path(self, src, dest):
        """
        Initiates recursive pathfinding from src to dest (as tuples of x,y coords), 
            returns path with minimum step ct
        """
        def step_cell(cell_coord, step_ct):
            """
            Updates cell with new step ct if applicable,
                recursively steps to neighboring cells
            """
            nonlocal self
            nonlocal dest
            nonlocal minsteps
            nonlocal minroute
            
            #Store current coordinate as point in current candidate route
            curr_route.append(cell_coord)            
            
            #Store x, y coords of current cell, 
            curr_x = cell_coord[0]
            curr_y = cell_coord[1]
            
            if self.step_grid[curr_x][curr_y] <= step_ct:
                #If minimum step ct recorded for coord is less than current step, 
                #    cell's inclusion would make path redundant with equal or better known path so abort
                return
            else:
                self.step_grid[curr_x][curr_y] = step_ct
            
            
            #Calc x, y diff to destination
            x_diff = dx - curr_x
            y_diff = dy - curr_y
            
            if x_diff + y_diff + step_ct >= minsteps:
                #If number of steps left in ideal route (no obstructions) plus curr steps >= best recorded steps, 
                #    cannot improve over best route, so abort
                return
            
            #Calculate distance of current cell to destination
            curr_dist = ((x_diff)**2 + (y_diff)**2)**(1/2)
            
            #Prioritize guess at best direction via
            #Iteration over enum of directions, sorted by min dist of: (current coord + direction) - destination
            for new_coord in sorted([Coordinate(cell_coord + d) for d in Coordinate.dir_coords()], key=lambda p: p - dest ):
                #For coordinate produced from current coordinate + direction
                new_coord = (new_coord.x, new_coord.y)
                if self.step_allowed(new_coord):
                    #If cell can be stepped to (is in bounds and not obstructed), step to it
                    #Increment step +1 if moving from clear ground, otherwise confer +2 movement penalty
                    step_cell(new_coord, step_ct + (1 if self.board[curr_x][curr_y].get_type() == 1 else 2))
                    #Remove stepped cell's coord (added in call to step_cell) from current route
                    #    to reset path for next element or calling function
                    curr_route.pop(-1)
                elif new_coord == dest:
                    #Destination reached, record step count to minsteps (is current path to beat)
                    #Set current route to minroute (path to follow)
                    curr_route.append(new_coord)
                    minsteps = step_ct
                    minroute = deepcopy(curr_route)
            return
        
        #Initialize minimum steps calculated to infinity for use in inner fn
        #(guarantee >= 1 path always considered)
        minsteps = math.inf
        
        #Initalize minroute, currroute to None, [] respectively for use in inner fn
        minroute, curr_route = [], []
        
        #Store x, y values of destination coordinate
        dx = dest[0]
        dy = dest[1]
        
        #Initialize mock of board with step counts = infinity 
        #(to guarantee any unvisited cell is considered if within range of minimum path candidates)
        self.step_grid = self.dupe_board_struct(lambda: math.inf)
        
        #Root of recursive stepper
        step_cell((src[0],src[1]), 1)


        path = []
        for idx in range(0, len(minroute) - 1):
            #If next coord in path is the destination, assign attack, otherwise, move
            curr_coord = minroute[idx]
            next_coord = minroute[idx + 1]
            if next_coord == dest:
                action = 'attack'
            else:
                action = 'move'
            path.append((next_coord, Coordinate((next_coord[0] - curr_coord[0], next_coord[1] - curr_coord[1] )), action))



        return path