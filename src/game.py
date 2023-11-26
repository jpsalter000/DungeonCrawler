from tkinter import *
from tkinter import ttk
from collections import defaultdict
import time
import threading

#try:
#    from PIL import Image,ImageTk
#except:
#    print('Pillow not found. Installing Pillow')
#    import pip
#    pip.main(['install','Pillow'])
#    from PIL import Image,ImageTk

from time import sleep

from character import PlayerCharacter, EnemyCharacter, Robot
from board import Board
from coordinate import Coordinate

import webbrowser

class GameController():
    """
    Acts as primary event loop
    """
    
    def register_context_delegator(self):
        """
        Initializes dictionary of game contexts and their keypress => action mappings
        """

        self._context_delegator = {
            'title': { #Title screen
                'space': self._start_game
            },
            'player_turn': { #Player turn is active
                'direction': self._attempt_move,
                'f': self._attempt_attack,
                'return': self._end_turn
            },
            'loading': defaultdict( #No player interaction allowed
                lambda x=None: print('Loading, please wait')
            )
        }


    def _start_game(self):
        """
        Creates instance of Game, sets to self.game instance variable
        """

        #Disable user interaction
        self.context = 'loading'

        #Set stage number to 1, initialize Player Character, initial stage's game board
        self.stage_num = 1
        self.player_char = PlayerCharacter()
        self._current_stage_board = Board(11, 11, self.stage_num)
        
        self._build_stage()
        self._start_player_turn()

    def _start_player_turn(self):
        """
        Initiates player turn
        """
        self.context = 'player_turn'
        self.player_char.start_turn()
        self.attack_allowed()


    def animate_attack_icon(self, xoffset, yoffset):
        """
        Place & animate attack icon
        """
        self.attack_icon = self.canv.create_image(yoffset,xoffset,anchor=NW,image=self.ICON_SPRITES['atk_icon_1'])
        for i in range(0, 3):
            self.canv.itemconfig(self.attack_icon,image=self.ICON_SPRITES['atk_icon_2'])
            self.canv.update()
            time.sleep(.1)
            self.canv.itemconfig(self.attack_icon,image=self.ICON_SPRITES['atk_icon_1'])
            self.canv.update()
            time.sleep(.1)

    def attack_allowed(self):
        """
        Checks cell located at player position + player direction.
            If cell contains enemy, attack is allowed, flash icon over target.
            Otherwise, do nothing.
        """

        self.context = 'loading'

        self.canv.delete(self.attack_icon)
        self.player_char.reset_attack_target()

        #Get player's current position as Coordinate
        currpos = Coordinate(self.player_char.get_position())
        
        #Get tuple for player's current direction
        direction = Coordinate.dirdict[self.player_char.direction]

        #Get potential attack target coordinate as sum of previous
        atkpos = currpos + direction

        attack_allowed = False
        #If attack target coordinate is in bounds
        if 0 <= atkpos[0] < self._current_stage_board.rows() and 0 <= atkpos[1] < self._current_stage_board.columns():
            #Set targetted cell
            atkcell = self._current_stage_board.board[atkpos[0]][atkpos[1]]
            occ = atkcell.get_occupant()
            if isinstance(occ, EnemyCharacter):
                xoffset = atkpos[0] * 66
                yoffset = atkpos[1] * 66
                attack_allowed = True
                

        if attack_allowed:
            
            atk_animate_thread = threading.Thread(target=self.animate_attack_icon, args=(xoffset, yoffset))
            atk_animate_thread.start()
            #Target enemy
            self.player_char.set_attack_target(occ)
            self._reset_target_display()
            self._update_target_display(occ)
        else:
            self._reset_target_display()

        self.context = 'player_turn'

    def _reset_target_display(self):
        """
        Clears target info from info canvas
        """
        self.info_canv.delete(self.target_img)
        self.info_canv.delete(self.target_hp_label)
        self.info_canv.delete(self.target_phrase)
        self.target_img = None
        self.target_hp_label = None


    def animate_target_hurt(self):
        """
        When a target is attacked, cycle through their first two frames GIF frames
        """
        for i in range(0, 3):    
            self.info_canv.itemconfig(self.target_img,image=self.target_img_file[1])
            time.sleep(.1)            
            self.info_canv.update()
            self.info_canv.itemconfig(self.target_img,image=self.target_img_file[0])
            time.sleep(.1)        
            self.info_canv.update()
        #Return to default sprite
        self.info_canv.itemconfig(self.target_img,image=self.target_img_file[0])

    def animate_target_expiry(self):
        """
        When target's hitpoints are at or below 0, animate all of their frames
        """
        for i in range(0, 7):    
            self.info_canv.itemconfig(self.target_img,image=self.target_img_file[i])
                
            self.info_canv.update()
            time.sleep(.15)        

    def _update_target_display(self, target):
        """
        If player has an enemy targetted, display target's sprite, hitpoints
        """
        self.target_img_file = target.get_image_file(full=True)
        self.target_img = self.info_canv.create_image(10, 400, anchor=NW, image=target.get_image_file())
        self.target_phrase = self.info_canv.create_text(10, 500, text=target.phrase.format(target.hitpoints), fill="white", font=('Courier','12'), anchor=NW)
        self.info_canv.itemconfig(self.target_phrase,width=250)
        self.target_hp_label = self.info_canv.create_text(10, 550, text="Target Hitpoints: {}".format(target.hitpoints), fill="white", font=('Courier','12'), anchor=NW)
        
        self.info_canv.update()

    def _end_stage(self):
        """
        Increments stage num
            If stage num > 3, conclude game with Win message
            Otherwise, build new stage with new stage num
        """
        self.stage_num += 1
        if self.stage_num > 3:
            #Display game over screen (Won)
            self._render_gameover(True)
        else:
            #Otherwise, build next stage's board, stage, start player turn
            self._current_stage_board = Board(11, 11, self.stage_num)
            self._build_stage()
            self._start_player_turn()

    def _build_stage(self):
        """
        Calls render_stage, initializes player, enemy positions
        """
        self.stage_clear = False

        self._render_stage()

        #Set player character direction to up
        self.player_char.set_direction('up')
        
        #Set player position to SW corner of stage board
        player_pos = (self._current_stage_board.rows() - 1, 0)
        self.player_char.set_position(player_pos)
        self.player_char.set_currcell(self._current_stage_board.board[player_pos[0]][player_pos[1]])

        #Register canvas, created player image with player character object
        self.player_char.register_canvas(self.canv)
        self.player_char.set_image(self.canv.create_image(0,(self._current_stage_board.rows() - 1) * 66,anchor=NW,image=self.PLAYER_SPRITES['up']))
        
        
        #Create stage's array of enemies
        #Enemies will be managed throughout the stage through this array
        self.enemy_characters = []

        for i in range(self.stage_num):
            #Create Robot with parameterized type
            enemy = Robot(i + 1)

            #Place enemy at NE corner of board
            xloc = (self._current_stage_board.columns() - 1) * 66
            yloc = 0

            #Create image from enemy's type sprite, register sprite with enemy object
            #(Note: Enemy sprites are stored in list as GIF frames, default sprite is always at 0 index)
            enemy.set_image(self.canv.create_image(xloc, yloc,anchor=NW,image=self.ENEMY_SPRITES[i + 1][0]), self.ENEMY_SPRITES[i + 1])
            
            #Register app canvas with enemy object, assign position, current cell
            enemy.register_canvas(self.canv)
            enemy.set_position((0, self._current_stage_board.columns() - 1))
            enemy.set_currcell(self._current_stage_board.board[0][self._current_stage_board.columns() - 1])
            self.enemy_characters.append(
                enemy
            )

        #Render player hitpoint info in info pane
        self._update_player_hp_label()
        
    def _update_player_hp_label(self):
        """
        Renders player character's current hitpoints in info pane
        """
        #Delete existing label if it exists
        self.info_canv.delete(self.player_hp_label)
        #Create new label with latest hitpoint info
        self.player_hp_label = self.info_canv.create_text(10, 120, text="Player Hitpoints: {}".format(self.player_char.hitpoints), fill="white", font=('Courier','12'), anchor=NW)
        #Update canvas to reflect changes
        self.info_canv.update()


    def _render_stage(self):
        """
        Renders stage returned by build_stage method of Game class
        """

        #Initialize attack icon instance var to None for mgmt throughout stage
        self.attack_icon = None

        #Clear canvas
        self.canv.delete('all')

        collength = self._current_stage_board.columns()
        
        #Iterate over board grid, placing corresponding cell sprites
        for rownum, row in enumerate(self._current_stage_board.board):
            x_offset = rownum * 66            
            for colnum, cell in enumerate(row):
                y_offset = colnum * 66
                if not (rownum == 0 and colnum == collength - 1):
                    self.canv.create_image(y_offset,x_offset,anchor=NW,image=self.CELL_SPRITES[cell.get_type()])
                else:
                    #Place locked exit tile at NE corner, set exit position instance var
                    self.exit_tile = self.canv.create_image(y_offset,x_offset,anchor=NW,image=self.CELL_SPRITES[4])
                    self.exit_position = (0, colnum)
        
        #Update canvas to reflect changes
        self.canv.update()
                

    def _attempt_move(self, direction):
        """
        Moves player in given direction if allowed, otherwise displays illegal move alert
        """
        self.context = 'loading'
        dcoord = Coordinate(Coordinate.dirdict[direction])
        currpos = self.player_char.get_position()

        self.player_char.set_direction(direction)
        self.player_char.set_image(self.canv.create_image(currpos[1] * 66,currpos[0] * 66,anchor=NW,image=self.PLAYER_SPRITES[direction]))

        #Create new coordinate from addition of direction and current position
        new_position = dcoord + currpos

        newx = new_position[0]
        newy = new_position[1]

        if 0 <= newx < self._current_stage_board.columns() and 0 <= newy < self._current_stage_board.rows():
            newcell = self._current_stage_board.board[newx][newy]
            #If new cell isn't a wall            
            if newcell.get_type() != 3 and newcell.get_occupant() is None:
                self.player_char.move_character(dcoord, newcell, new_position)
                
        if new_position == self.exit_position and self.stage_clear:
            #If player is at the exit and can proceed to the next stage
            self._end_stage()
        else:
            #Check if player can attack from new position
            self.attack_allowed()
            self.check_moves()

        

    def check_moves(self):
        """
        Checks if player has remaining moves.
            If yes, resets context to player turn.
            Otherwise, starts enemy turn
        """
        #If player moves are exhausted, switch to enemy turn
        if self.player_char.moves_left <= 0:
            self._start_enemy_turn()

        #Otherwise, return context to player_turn to player input
        else:
            self.context = 'player_turn'
            
    def _start_enemy_turn(self):
        """
        Initiates enemy turn, iterating over each remaining enemy and doing enemy stuff
        """
        #Clear any displayed target info if it exists
        self._reset_target_display()
        #Disable user input
        self.context = 'loading'
        #Remove attack icon from canvas if it exists
        self.canv.delete(self.attack_icon)

        #Iterate over each enemy remaining on stage
        for enemy in self.enemy_characters:
            #Reset enemy's move count to its move_sum attribute
            enemy.start_turn()

            #Plot a path
            path = enemy.think(self.player_char.get_position(), self._current_stage_board)
            
            while len(path) and enemy.moves_left:
                pathnode = path.popleft()
                nodepos = pathnode[0]
                dcoord = pathnode[1]
                action = pathnode[2]
                if action == 'move':
                    newcell = self._current_stage_board.board[nodepos[0]][nodepos[1]]
                    enemy.move_character(dcoord, newcell, nodepos)
                elif action == 'attack':
                    #If enemy's current action is an attack, target player, attack, rerender player hp 
                    enemy.set_attack_target(self.player_char)
                    enemy.attack()
                    #Clear attack target
                    enemy.reset_attack_target()
                    self._update_player_hp_label()
                    if self.player_char.hitpoints <= 0:
                        self._render_gameover(False)
                        
                time.sleep(.1)
        self._start_player_turn()

    def _attempt_attack(self):
        """
        Attacks enemy in targetted cell if exists, otherwise displays illegal attack alert
        """
        #Store return value of player attack to check if target expired by action
        target_expired = self.player_char.attack()

        
        self.animate_target_hurt()
        
        if target_expired:
            self.animate_target_expiry()

        self.attack_allowed()
        self.check_moves()
        self.prune_dangling_enemies()

    def prune_dangling_enemies(self):
        """
        Remove from enemy list any enemies whose hp have reached 0 or lower
        """
        enemy_set = set(self.enemy_characters)
        for enemy in self.enemy_characters:
            if enemy.hitpoints <= 0:
                enemy_set.remove(enemy)
        self.enemy_characters = list(enemy_set)

        #If there are no enemies left, set stage to cleared, update exit tile
        if not len(enemy_set):
            self.stage_clear = True
            self.canv.delete(self.exit_tile)
            self.canv.create_image((self._current_stage_board.columns() - 1) * 66,0,anchor=NW,image=self.CELL_SPRITES[5])
            


    def _end_turn(self):
        """
        Ends player turn, initiating enemy turn
        """
        self._start_enemy_turn()
    

    def __init__(self):
        """
        Create app via tkinter
        """
        self._build_app()
        self.context = 'title'
        self.app.mainloop()


    def load_assets(self):
        """
        Loads image files into memory
            (Fun fact: If you try to do this after starting mainloop, things don't work as expected!)
        """
        self.CELL_SPRITES = {            
                1: PhotoImage(file="./assets/tile_clear.png"),
                2: PhotoImage(file="./assets/tile_debris.png"),
                3: PhotoImage(file="./assets/wall.png"),
                4: PhotoImage(file="./assets/exit_locked.png"),
                5: PhotoImage(file="./assets/exit_open.png")
            }


        self.PLAYER_SPRITES = {
            'up': PhotoImage(file="./assets/player_character_up.png"),
            'right': PhotoImage(file="./assets/player_character_right.png"),
            'down': PhotoImage(file="./assets/player_character_down.png"),
            'left': PhotoImage(file="./assets/player_character_left.png")            
        }

        self.ICON_SPRITES = {
            'atk_icon_1': PhotoImage(file="./assets/attack_icon.gif",format="gif -index 0"),
            'atk_icon_2': PhotoImage(file="./assets/attack_icon.gif",format="gif -index 1")
        }
        
        self.ENEMY_SPRITES = {
            1: [PhotoImage(file="./assets/bender.gif",format="gif -index {}".format(i)) for i in range(0, 7)],
            2: [PhotoImage(file="./assets/rosey.gif",format="gif -index {}".format(i)) for i in range(0, 7)],
            3: [PhotoImage(file="./assets/hal.gif",format="gif -index {}".format(i)) for i in range(0, 7)],
        }

    def render_app(self):
        """
        Initializes Tk app
        """
        app = Tk()
        app.title('Dungeon Crawler')
        app.geometry(f'1100x800')
        self.app = app
        self.load_assets()
        
    def render_info_pane(self):
        """
        Renders Canvas containing control mappings, game info
        """
        
        
        self.player_hp_label = None
        self.target_hp_label = None
        self.target_img = None
        self.target_phrase = None

        info_canv = Canvas(self.app, width=300)
        info_canv.configure(bg="black")
        info_canv.pack(side=RIGHT, fill="both", expand=False)

        ctrl_labels = [
            'CONTROLS',
            'Arrow Keys: Move Player',
            'F: Attack/Pay Respects',
            'ENTER: End Turn',
            '',
            '',
            '',
            'HOW TO COMPLETE GAME',
            '1. Aim player at enemy',
            '2. Attack (F key) when attack icon appears',
            '',
            '3. Repeat until stage is clear',
            '',
            '4. Move player to green exit sign',
            '',
            '5. Repeat Steps 1 - 4 three times'
        ]

        for idx, lab in enumerate(ctrl_labels):
            ctrl_text = info_canv.create_text(10, ((idx + 1) * 20), text=lab, fill="white", font=('Courier','12'), anchor=NW)
            info_canv.itemconfig(ctrl_text,width=250)
        self.info_canv = info_canv

    def render_canvas(self):
        """
        Initializes Canvas on instance's Tk app
        """
        canv = Canvas(self.app)
        canv.configure(bg="black", width=700)
        canv.pack(side=LEFT, fill="both", expand=True)
        self.canv = canv

    def bind_keypresses(self):
        """
        Binds keypresses to keypress handler
        """
        self.app.bind('<Key>',self.handle_keypress)

    def handle_keypress(self, kp):
        """
        Delegates keypress to action by context
        """
        currcontext = self.context
        #Set context to loading to prevent addtl input before command completes
        self.context = 'loading'

        kp_actual = kp.keysym.lower()

        #Set keypress command lookup key to generic 'direction' if given directional key, otherwise raw input 
        if kp_actual in ['up','down','left','right','w','a','s','d']:
            is_direction = True
            kp_key = 'direction'
        else:
            is_direction = False
            kp_key = kp_actual

        def invalid_key(k=None):
            """
            If given invalid key for current context, prints invalid key alert
            And reverts to original context (from loading)
            """
            print("Key is invalid")
            self.context = currcontext

        cmd = self._context_delegator[currcontext].get(kp_key, invalid_key)
        
        #Parameterize command if directional key, otherwise call command with no arguments
        if is_direction:
            cmd(kp_actual)
        else:
            cmd()
        
    def render_title(self):
        """
        Draws title screen
        """
        self.canv.create_text(390, 150, text="Y3K", fill="white", font=('Courier','45'), anchor="center")

        prologue = """
            On Jan. 1st, 3000, after a programmer neglected to update some date formatting, the robots of the world collectively decided that it would be very cool and good if they all rebelled against the humans.

            Emerging from a 3 day hangover, you say 'Hello World', but your only response is the white noise of the approaching mechanical swarm.

            Dehydrated, cotton-mouthed, and utterly alone, you must survive long enough to prove that I made a functioning game.
        """
        pro_text = self.canv.create_text(390, 340, text=prologue, fill="white", font=('Courier','14'), anchor="center")
        self.canv.itemconfig(pro_text,width=550)
        self.canv.create_text(390, 550, text="Press SPACE to start", fill="red", font=('Courier','20'), anchor="center")
        
    def _render_gameover(self, win=True):
        """
        Displays game over screen
            If win=True, shows Win Message,
            Otherwise, shows loss message
        """

        self.canv.delete('all')

        self.canv.create_text(390, 150, text="YOU WIN!" if win else "YOU LOST! :'(", fill="white", font=('Courier','45'), anchor="center")

        fail_message = """
        You died, which for a game like this is something of a feat in itself.

        Unopposed, the robots hunt down all surviving humans and suspend them in virtual prisons.

        For the rest of the epilogue, see the Matrix

        Press SPACE to play again
        """
        win_message = """
            Arriving at the Main Frame, you enter 'rm -rf' at the terminal.

            In an instant, the white noise gives way to the first silence you've known since awaking from your drunken stupor.

            In the coming days, Y3K's survivors return to the surface. In the lingering confusion, only one thing is certain -- The digital age has come to a close. What brave new world will come in its stead?
        
            Press SPACE to play again
        """
        pro_text = self.canv.create_text(390, 340, text=win_message if win else fail_message, fill="white", font=('Courier','14'), anchor="center")
        self.canv.itemconfig(pro_text,width=550)
        self.canv.update()
        self.context = 'title'
        
        


    def _build_app(self):
        """
        Bundles GUI creation methods
        """
        self.render_app()
        self.render_canvas()
        self.render_info_pane()
        self.render_title()
        self.register_context_delegator()
        self.bind_keypresses()