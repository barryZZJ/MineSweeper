from mapGen import *
from constants import *

import pygame
from pygame.locals import *

from math import ceil

pygame.init()

map = Map(Difficulty.NORMAL)
# map.generate()

TILE_WIDTH = 1344//16 # 84
TILE_HEIGHT = 420//5 # 84
RESIZE_SCALE = 0.5

# screen
SCREEN_SIZE = ceil(map.get_nums[0]*TILE_WIDTH*RESIZE_SCALE), ceil(map.get_nums[1]*TILE_HEIGHT*RESIZE_SCALE)
screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32) #type: pygame.Surface

# title
pygame.display.set_caption("Mine Sweeper")

# background
bgsurf = pygame.image.load(PATH.BG).convert() #type: pygame.Surface

def load_tile_list(filename, width, height) -> List[pygame.Surface]:
    image = pygame.image.load(filename).convert_alpha() # type: pygame.Surface
    image_width, image_height = image.get_size()
    tile_list = []
    for tile_y in range(0, image_height//height):
        line = []
        for tile_x in range(0, image_width//width):
            rect = (tile_x*width, tile_y*height, width, height)
            surf = image.subsurface(rect) #type: pygame.Surface
            surf = pygame.transform.scale(surf, (int(width*RESIZE_SCALE), int(height*RESIZE_SCALE)))
            line.append(surf)
        tile_list.extend(line)
    return tile_list

tile_list = load_tile_list(PATH.TILE_TABLE, TILE_WIDTH, TILE_HEIGHT)

def init():
    # draw background
    screen.blit(bgsurf, (0,0))

    # draw all blocks
    for x in range(1, map.get_nums[0]+1):
        for y in range(1, map.get_nums[1]+1):
            tile_i = map.mm[x][y].getTileI()
            screen.blit(tile_list[tile_i], (int((y-1)*TILE_WIDTH*RESIZE_SCALE), int((x-1)*TILE_HEIGHT*RESIZE_SCALE)))

    pygame.display.update()

def do_Left_Click(x, y, dirty_poses: List[Tuple[int, int]]) -> bool:

    game_over = map.leftClick(x, y, dirty_poses)

    #other stuff like animation
    return game_over

def do_Mid_Click(x, y, dirty_poses: List[Tuple[int, int]]) -> bool:
    game_over = map.midClick(x, y, dirty_poses)

    #other stuff like animation
    return game_over

def do_Right_Click(x, y, dirty_poses: List[Tuple[int, int]]) -> bool:
    map.rightClick(x, y, dirty_poses)

    #other stuff like animation
    return False

def log_dirty_rects(dirty_rects: List[pygame.Rect], dirty_poses: List[Tuple[int, int]]) -> None:
    # log diry rects
    for x, y in dirty_poses:
        dirty_rects.append(block_rects[x - 1][y - 1])


# block rects
block_rects = [] # type: List[List[pygame.Rect]]
for i in range(map.get_nums[0]):
    tmp = []
    for j in range(map.get_nums[1]):
        tmp.append(pygame.Rect(int((j)*TILE_WIDTH*RESIZE_SCALE),
                               int((i)*TILE_HEIGHT*RESIZE_SCALE),
                               int(TILE_WIDTH*RESIZE_SCALE),
                               int(TILE_HEIGHT*RESIZE_SCALE)
                               )
                   )
    block_rects.append(tmp)

#block keyboard events
pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP])

init() # draw BG img and all blocks
game_over = False
# main loop
while not game_over:
    dirty_rects = list() # type: List[pygame.Rect]
    dirty_poses = list() # type: List[Tuple[int, int]]

    event = pygame.event.wait() #type: pygame.event.EventType

    if event.type == QUIT:
        exit()
    elif event.type == MOUSEBUTTONUP:
        # click block
        MousePos = event.dict['pos']
        MouseButn = event.dict['button']

        # get block id
        x, y = None, None
        for i in range(map.get_nums[0]):
            for j in range(map.get_nums[1]):
                if block_rects[i][j].collidepoint(*MousePos):
                    x, y = i+1, j+1

        if x and y:
            if MouseButn == 1:
                # left click
                game_over = do_Left_Click(x, y, dirty_poses)
            elif MouseButn == 2:
                # mid click
                game_over = do_Mid_Click(x, y, dirty_poses)
            else:
                # right click
                game_over = do_Right_Click(x, y, dirty_poses)
            # blit dirty blocks
            for _x, _y in dirty_poses:
                tile_i = map.mm[_x][_y].getTileI()
                screen.blit(tile_list[tile_i], (int((_y-1)*TILE_WIDTH*RESIZE_SCALE), int((_x-1)*TILE_HEIGHT*RESIZE_SCALE)))
            # log dirty rects for update screen
            log_dirty_rects(dirty_rects, dirty_poses)

    # ------------------------------------------------
    # for x in range(1, map.get_nums[0]+1):
    #     for y in range(1, map.get_nums[1]+1):
    #         tile_i = map.mm[x][y].getTileI()
    #         screen.blit(tile_list[tile_i], (int((y-1)*TILE_WIDTH*RESIZE_SCALE), int((x-1)*TILE_HEIGHT*RESIZE_SCALE)))

    # ------------------------------------------------
    # draw updated blocks
    pygame.display.update(dirty_rects)

#TODO 游戏结束操作
#todo WIN操作
#TODO display mine cnt