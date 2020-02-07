from enum import IntEnum
from os.path import dirname

DEBUG = False

# tile index of tile_list, start from 0
class TILE(IntEnum):
    CLOSED = 1
    FLAG = 2
    MINE = 4
    NUM_0 = 5
    NUM_1 = 6
    NUM_2 = 7
    NUM_3 = 8
    NUM_4 = 9
    NUM_5 = 10
    NUM_6 = 11
    NUM_7 = 12
    NUM_8 = 13
    CLOSED_HOLD = 14
    PINK = 16*3+12
    QUESTION = 3

TILE_WIDTH = 1344//16 # 84
TILE_HEIGHT = 420//5 # 84

class PATH:
    _curr = dirname(__file__) # current path of this file
    BG = _curr + './pics/Metal/minesweeper-metal-bg.jpg'
    TILE_TABLE = _curr + './pics/Metal/TileStates-classic-combined.png'
