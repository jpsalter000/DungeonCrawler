# DungeonCrawler
Dungeon crawling mini-game built with TKinter

# Requirements

	* Python 3.X

# Description

Program consists of a simple tactical turn-based fighting game with three distinct stages.

Each stage features a procedurally generated board of one of three type configurations,
 and up to three distinct enemies that the player must defeat before completing the stage.
 Combat consists of aiming the player at an enemy and pressing F to attack enemy. Once an enemy's
 hitpoints value falls to 0 or lower, enemy is 'defeated'.
 Player completes stage by moving to the tile with a green Exit label made available when
 all enemies have been defeated.

 Game is over when either:
 	Player successfully completes 3 consecutive stages (Win condition)
 or
 	Player's hitpoints value falls to 0 or lower (Lose condition)


# Usage

Launch program with command 'python main.py' from root directory

On program launch, all user interaction is managed by key bindings.

Key bindings by context are as follows:

* Title Screen
** Space - Start New Game
* Player Turn
** Left Arrow - Move Player Character to left-hand tile if possible
** Right Arrow - Move Player Character to right-hand tile if possible
** Up Arrow - Move Player Character to upper tile if possible
** Down Arrow - Move Player Character to lower tile if possible
** F - Attack Enemy Character if facing one
** Enter - End turn
*Enemy Turn
**NO USER INTERACTION DURING ENEMY TURN
*Game Over Screen
** Space - Start New Game

# External Resources Used

*Visual assets created with Piskel (https://www.piskelapp.com/)