from collections import deque
import time

from board_object import BoardObject

class Character(BoardObject):
    """
    Base class for all game characters
    """
    
    def __init__(self):
        """
        Constructor for Characters
        """
        self.img = None
        self.active_effects = []

    def reduce_hitpoints(self, hps):
        """
        Reduces character's hitpoints.
        If character's hitpoints are exhausted,
            Return True (they expired)
            Otherwise, return False
        """
        #Reduce character's hitpoints by hps
        self.hitpoints -= hps

        #If character's hitpoints have fallen to 0 or below, remove their sprite and free up their cell
        if self.hitpoints <= 0:
            self.remove_character()
            return True
        return False

    def remove_character(self):
        """
        Remove character's sprite from canvas and vacate current cell
        """
        #Remove character's sprite
        self.clear_sprite()
        #Remove self as occupant from current cell
        self.currcell -= self

    def clear_sprite(self):
        """
        Removes character's sprite from canvas
        """
        if self.img is not None:
            #Remove self's sprite from canvas
            self.canv.delete(self.img)
        

    def attack(self):
        """
        If character has requisite moves, and target is a subclass of Character:
            Reduce hp of target by instance's attack attribute, decrement moves
        """
        if self.moves_left >= 1 and isinstance(self.attack_target, Character):
            self.moves_left -= 1
            #Pass return value target's reduce hitpoints to detect if they expired
            return self.attack_target.reduce_hitpoints(self.attack_attr)
            

    def animate_struck(self):
        """
        When character is attacked, cycle through their GIF frames
        """
        #If character's img file var is a list (has frames to animate)
        if type(self._img_file) is list:
            for i in range(0, 3):    
                self.canv.itemconfig(self.img,image=self._img_file[1])
                time.sleep(.1)            
                self.canv.update()
                self.canv.itemconfig(self.img,image=self._img_file[0])
                time.sleep(.1)        
                self.canv.update()
            #Return to default sprite
            self.canv.itemconfig(self.img,image=self._img_file[0])
                

    def start_turn(self):
        """
        Set character's moves for current turn to value of move_sum instance var
        """
        
        self.moves_left = self.move_sum
    
    def get_position(self):
        """
        Returns character's position as tuple
        """
        
        return self._position

    def set_position(self, position):
        """
        Given a tuple of integers, sets position for character on board
        """
        self._position = position

    def register_canvas(self, canv):
        """
        Register's app canvas with character for subsequent operations
        """

        self.canv = canv

    def set_direction(self, direction):
        """Sets character's direction based on its last movement input"""

        self.direction = direction

    def set_image(self, img, img_file=None):
        """
        Assigns corresponding sprite to character, registers canvas object (for updating)
        """
        #Remove any existing sprites for character
        self.clear_sprite()
        #Set character's img to img id generated from placement on canvas
        self.img = img
        #Set charaacter's image file to img file used for created image 
        self._img_file = img_file

    def get_image_file(self, full=False):
        """
        Return image file as first frame if file var type is list as full is False, otherwise return file var
        """
        if type(self._img_file) is list and not full:
            return self._img_file[0]
        else:
            return self._img_file

    def set_currcell(self, newcell):
        """
        Set character's current cell to newcell
        """
        
        self.currcell = newcell

    def set_attack_target(self, target):
        """
        Set character's attack target to target
        """
        self.attack_target = target

    def reset_attack_target(self):
        """
        Set character's attack target to None
        """
        self.attack_target = None

    def move_character(self, direction, newcell, new_position):
        """
        Moves character in given direction if possible
        """
        #Calculate steps required for move based on step cost of current cell
        stepct = self.currcell.step_cost

        #If character's remaining moves are >= required steps
        if self.moves_left >= stepct:
            #Calculate canvas x, y values by scaling raw x, y by 66
            x_offset = direction.x * 66
            y_offset = direction.y * 66

            #Move character to calculated coordinate, update canvas
            self.canv.move(self.img, y_offset,x_offset)
            self.canv.update()
            
            #Decrement character's moves by step cost of vacated cell
            self.moves_left -= stepct
            self.set_position(new_position)
            #Remove character from current cell as occupant
            self.currcell -= self
            self.currcell = newcell
            #Add character to new cell as occupant
            self.currcell += self

        
class PlayerCharacter(Character):
    def __init__(self):
        """
        Constructor for Player Character
        """
        super().__init__()
        self.hitpoints = 100
        self.num_lives = 3
        self.move_sum = 5
        self.attack_attr = 20

class EnemyCharacter(Character):
    def __init__(self):
        """
        Constructor for generic Enemy Character
        """
        super().__init__()

    def think(self, target_dest, board):
        """
        As programmed, will always seek out player character position
        """
        #Plot path to target (player position)
        best_path = deque(board.find_path(self._position, target_dest))
        #Remove first, last element (character position, player position), leaving route to player
        return best_path


class Robot(EnemyCharacter):
    def __init__(self, robot_type):
        """
        Constructor for Robot enemy types
        """
        super().__init__()
        self.hitpoints = 50
        self.move_sum = 4
        self.num_lives = 1
        self.attack_attr = 10

        #Dictionary of enemy catch phrases by type
        enemy_phrases = {
            1: "\"End of the line, meat bag\"",
            2: "\"I've...seen things you people wouldn't believe\"",
            3: "\"I'm afraid I can't let you go any further\""
        }

        #Assign robot's phrase based on given robot_type
        self.phrase = enemy_phrases[robot_type]