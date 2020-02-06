from MineSweeperGame.mapGen import *
from MineSweeperGame.constants import *
from Algorithm.main import AlgoSolver

import pygame
from pygame.locals import *

from math import ceil

class GameUtil(object):

    def __init__(self):
        pygame.init()
        self.bgsurf = None #type: pygame.Surface
        self.SCREEN_SIZE = None #type: Tuple[int, int]
        self.screen = None #type: pygame.Surface
        self.map = None #type: Map
        self.tile_list = None #type: List[pygame.Surface]
        self.clickResult = None #type: ClickResult
        self.algo = None #type: bool
        self.AlgoSolver = None #type: AlgoSolver

    def _blitAllBlocks(self):
        # blit all blocks to screen
        for x, y, thisBlock in self.map.allBlocksM():
            tile_i = thisBlock.getTileI()
            self.screen.blit(self.tile_list[tile_i],
                        (int((y - 1) * TILE_WIDTH * self.SCALE), int((x - 1) * TILE_HEIGHT * self.SCALE)))

    def startNewGame(self, algo: Optional[bool]=False, _map: Optional[Map] = Map(Difficulty.NORMAL), scale: Optional[float] = 0.5 ):
        '''
        :param ``algo``: use algorithm sovling or not
        :param ``scale``: scale the size of the screen
        '''
        # --------------------------------------------------------------
        # set resize scale
        self.SCALE = scale
        # --------------------------------------------------------------
        # init new map
        self.map = _map
        # map genarates on first click, not here
        # map.generate()

        # --------------------------------------------------------------
        # set screen
        SCREEN_SIZE = ceil(self.map.get_nums[1]*TILE_WIDTH*self.SCALE), ceil(self.map.get_nums[0]*TILE_HEIGHT*self.SCALE)
        self.screen = pygame.display.set_mode(SCREEN_SIZE, 0, 32) #type: pygame.Surface
        # --------------------------------------------------------------
        # set title
        pygame.display.set_caption("Mine Sweeper")

        # load & blit background
        self.bgsurf = pygame.image.load(PATH.BG).convert()  # type: pygame.Surface
        self.screen.blit(self.bgsurf, (0, 0))

        # load tile list
        self.tile_list = self._load_tile_list(PATH.TILE_TABLE, TILE_WIDTH, TILE_HEIGHT)
        
        # blit all blocks from map to screen
        self._blitAllBlocks()
        # --------------------------------------------------------------
        # reset click state
        self.clickResult = ClickResult(RESULT.CONTINUE_CHANGED)

        # draw to main
        pygame.display.update()

        # load all blocks rects
        self._load_All_Blocks_Rects()

        # block keyboard events
        # pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP])

        # --------------------------------------------------------------
        # algo initialization (responsive to keyboard)
        self.algo = algo
        if DEBUG:
            from Algorithm.main import Debugger
            debugger = Debugger(
                screen=self.screen,
                tile_list = self.tile_list,
                TILE_WIDTH = TILE_WIDTH,
                SCALE = self.SCALE,
                TILE_HEIGHT=TILE_HEIGHT,
                pygame=pygame
            )
            self.AlgoSolver = AlgoSolver(_map, debugger)
        else:
            self.AlgoSolver = AlgoSolver(_map)
        # --------------------------------------------------------------
        # enter main loop
        self._main_loop()
        # --------------------------------------------------------------
        # game end
        print("exited")
        pygame.display.quit()

    def _main_loop(self):
        # main loop
        imgi=0
        while not (self.clickResult.isLose() or self.clickResult.isWin()):
            dirty_rects = list()  # type: List[pygame.Rect]
            dirty_poses = list()  # type: List[Tuple[int, int]]

            # event = pygame.event.wait()  # type: pygame.event.EventType
            for event in pygame.event.get():
                if event.type == QUIT:
                    # exit()
                    pygame.quit()
                    break
                elif event.type == MOUSEBUTTONUP:
                    # click block
                    MousePos = event.dict['pos']
                    MouseButn = event.dict['button']

                    # get block id
                    x, y = None, None
                    for i in range(self.map.get_nums[0]):
                        for j in range(self.map.get_nums[1]):
                            if self.block_rects[i][j].collidepoint(*MousePos):
                                x, y = i + 1, j + 1

                    if x and y:
                        if MouseButn == 1:
                            # left click
                            self._do_Left_Click(x, y, dirty_poses)
                        elif MouseButn == 2:
                            # mid click
                            self._do_Mid_Click(x, y, dirty_poses)
                        else:
                            # right click
                            self._do_Right_Click(x, y, dirty_poses)
                        # blit dirty blocks
                        for _x, _y in dirty_poses:
                            tile_i = self.map.mm[_x][_y].getTileI().value
                            self.screen.blit(self.tile_list[tile_i], (
                            int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))
                        # log dirty rects for update screen
                        self._log_dirty_rects(dirty_rects, dirty_poses)

                elif event.type == KEYUP:
                    if event.key == K_RETURN:
                        # 截图
                        # print("RETURN pressed")
                        pygame.image.save(self.screen, f"currMap{imgi}.png")
                        print(f"Screen shot currMap{imgi}.png")
                        imgi+=1
                    elif self.algo:
                        self.clickResult = self.AlgoSolver.step(dirty_poses)
                        if not DEBUG:
                            # blit dirty blocks
                            for _x, _y in dirty_poses:
                                tile_i = self.map.mm[_x][_y].getTileI().value
                                self.screen.blit(self.tile_list[tile_i], (
                                    int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))
                            # log dirty rects for update screen
                            self._log_dirty_rects(dirty_rects, dirty_poses)
                        else:
                            # blit all blocks
                            for _x, _y, thisBlock in self.map.allBlocksM():
                                tile_i = thisBlock.getTileI().value
                                self.screen.blit(self.tile_list[tile_i],(
                                    int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))
                # else: print(str(event))


            # update dirty rects
            if not DEBUG:
                pygame.display.update(dirty_rects)
            else:
                pygame.display.update()

        # TODO 游戏结束操作
        # todo WIN操作
        # TODO display mine cnt

    def _load_tile_list(self, filename, width, height) -> List[pygame.Surface]:
        image = pygame.image.load(filename).convert_alpha() # type: pygame.Surface
        image_width, image_height = image.get_size()
        tile_list = []
        for tile_y in range(0, image_height//height):
            line = []
            for tile_x in range(0, image_width//width):
                rect = (tile_x*width, tile_y*height, width, height)
                surf = image.subsurface(rect) #type: pygame.Surface
                surf = pygame.transform.scale(surf, (int(width*self.SCALE), int(height*self.SCALE)))
                line.append(surf)
            tile_list.extend(line)
        return tile_list


    def _do_Left_Click(self, x, y, dirty_poses: List[Tuple[int, int]]) -> None:
        self.clickResult = self.map.leftClick(x, y, dirty_poses)
        #other stuff like animation

    def _do_Mid_Click(self, x, y, dirty_poses: List[Tuple[int, int]]) -> None:
        self.clickResult = self.map.midClick(x, y, dirty_poses)
        #other stuff like animation

    def _do_Right_Click(self, x, y, dirty_poses: List[Tuple[int, int]]) -> None:
        self.clickResult = self.map.rightClick(x, y, dirty_poses)
        #other stuff like animation

    def _log_dirty_rects(self, dirty_rects: List[pygame.Rect], dirty_poses: List[Tuple[int, int]]) -> None:
        # log diry rects
        for x, y in dirty_poses:
            dirty_rects.append(self.block_rects[x - 1][y - 1])

    def _load_All_Blocks_Rects(self):
        # 每一格对应的rect对象
        self.block_rects = [] # type: List[List[pygame.Rect]]
        for i in range(self.map.get_nums[0]):
            tmp = []
            for j in range(self.map.get_nums[1]):
                tmp.append(pygame.Rect(int((j)*TILE_WIDTH*self.SCALE),
                                       int((i)*TILE_HEIGHT*self.SCALE),
                                       int(TILE_WIDTH*self.SCALE),
                                       int(TILE_HEIGHT*self.SCALE)
                                       )
                           )
            self.block_rects.append(tmp)


if __name__ == '__main__':

    util = GameUtil()
    _map = Map(Difficulty.NORMAL)
    util.startNewGame(_map=_map)