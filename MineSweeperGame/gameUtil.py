import time

from MineSweeperGame.mapGen import *
from MineSweeperGame.constants import *
from Algorithm.main import AlgoSolver

import pygame
from pygame.locals import *

from math import ceil
from itertools import count


class GameUtil(object):
    FONT_YAHEI = 'msyh'
    FONT_HEITI = 'simhei'

    def __init__(self):
        pygame.init()
        self.bgsurf = None #type: pygame.Surface
        self.SCREEN_SIZE = None #type: Tuple[int, int]
        self.screen = None #type: pygame.Surface
        self.map = None #type: Map
        self.tile_list = None #type: List[pygame.Surface]
        self.clickResult = None #type: ClickResult
        self.enable_algo = None #type: bool
        self.AlgoSolver = None #type: AlgoSolver

        self.fontObj = pygame.font.SysFont(self.FONT_HEITI, 25)
        self.fontbgObj = pygame.font.SysFont(self.FONT_HEITI, 26)

    def _blitAllBlocks(self):
        # blit all blocks to screen
        for x, y, thisBlock in self.map.allBlocksM():
            tile_i = thisBlock.getTileI()
            self.screen.blit(self.tile_list[tile_i],
                        (int((y - 1) * TILE_WIDTH * self.SCALE), int((x - 1) * TILE_HEIGHT * self.SCALE)))

    # def _blitText(self,fontObj: pygame.font.Font, text, dest: Tuple[int, int]) -> None:
    #     textSurf = fontObj.render(text, True, (0,0,0)) # Black
    #     self.screen.blit(textSurf, dest)

    def startNewGame(self, _map: Optional[Map] = Map(Difficulty.NORMAL), enable_algo: Optional[bool]=False, scale: Optional[float] = 0.5):
        """
        :param enable_algo: use algorithm sovling or not
        :param scale: scale the size of the screen
        """
        # --------------------------------------------------------------
        # set resize scale
        self.SCALE = scale
        # --------------------------------------------------------------
        # init new map
        self.map = _map
        # map genarates on first click, not here
        # map.generate()

        # 根据map长宽确定每一格对应的rect大小和位置
        self._load_All_Blocks_Rects()

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

        # --------------------------------------------------------------

        # # block keyboard events
        # pygame.event.set_blocked([pygame.KEYDOWN, pygame.KEYUP])

        # --------------------------------------------------------------
        # algo initialization (responsive to keyboard)
        self.enable_algo = enable_algo
        if enable_algo:
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
                self.AlgoSolver = AlgoSolver(self.map, debugger)
            else:
                self.AlgoSolver = AlgoSolver(self.map)
        # --------------------------------------------------------------
        # enter main loop
        self._main_loop()

        # exit
        pygame.quit()

    def _main_loop(self):
        # main loop
        imgi=0
        exitFlag = Flag()
        for rnd in count(1): # 无限循环直到按下esc
            while True:
                dirty_rects = list()  # type: List[pygame.Rect]
                dirty_poses = list()  # type: List[Tuple[int, int]]
                # event = pygame.event.wait()  # type: pygame.event.EventType
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    elif event.type == MOUSEBUTTONUP:
                        # click block
                        MousePos = event.dict['pos']
                        MouseButn = event.dict['button']

                        # get block id
                        x, y = None, None
                        for i in range(self.map.get_nums[0]):
                            for j in range(self.map.get_nums[1]):
                                if self.block_rects[i][j].collidepoint(*MousePos): # TODO 按键在缝里？
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
                            for x, y in dirty_poses:
                                dirty_rects.append(self.block_rects[x - 1][y - 1])

                    elif event.type == KEYUP:
                        if event.key == K_RETURN:
                            # 截图
                            # print("RETURN pressed")
                            pygame.image.save(self.screen, f"currMap{imgi}.png")
                            print(f"Screen shot currMap{imgi}.png")
                            imgi+=1
                        elif event.key == K_ESCAPE:
                            # esc 退出游戏
                            pygame.quit()
                            exitFlag.set()
                            break
                        elif self.enable_algo:
                            self.clickResult = self.AlgoSolver.step(dirty_poses)
                            if not DEBUG:
                                # blit dirty blocks
                                for _x, _y in dirty_poses:
                                    tile_i = self.map.mm[_x][_y].getTileI().value
                                    self.screen.blit(self.tile_list[tile_i], (
                                        int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))
                                # log dirty rects for update screen
                                for x, y in dirty_poses:
                                    dirty_rects.append(self.block_rects[x - 1][y - 1])
                            else:
                                # blit all blocks
                                for _x, _y, thisBlock in self.map.allBlocksM():
                                    tile_i = thisBlock.getTileI().value
                                    self.screen.blit(self.tile_list[tile_i],(
                                        int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))
                # print("out of event")

                # 退出游戏
                if exitFlag.get():
                    print("游戏已退出")
                    break

                # 本轮游戏结束
                if self.clickResult.isLose() or self.clickResult.isWin():
                    if self.clickResult.isLose():
                        textSurf = self.fontObj.render(f"第{rnd}轮失败！重新开始...", True, (
                        0, 0, 0), (255, 255, 255))  # type: pygame.Surface  # text, 抗锯齿, color = Black
                        # textbgSurf = self.fontbgObj.render(f"第{rnd}轮失败！重新开始...", True, (
                        # 255, 255, 255))  # type: pygame.Surface # 大一圈描边
                        print(f"第{rnd}轮失败！重新开始...")
                    else:
                        textSurf = self.fontObj.render(f"第{rnd}轮胜利！重新开始...", True, (
                        0, 0, 0), (255, 255, 255))  # type: pygame.Surface  # text, 抗锯齿, color = Black, bg= white
                        # textbgSurf = self.fontbgObj.render(f"第{rnd}轮胜利！重新开始...", True, (
                        #     255, 255, 255))  # type: pygame.Surface # 大一圈描边

                        # 把雷都变成粉色块并blit到screen，记录在dirty_rects中
                        self.blit_remains2pinks(dirty_rects)
                        print(f"第{rnd}轮胜利！重新开始...")

                    textRect = pygame.Rect(
                        (self.screen.get_width() - textSurf.get_width()) // 2,  # left
                        (self.screen.get_height() - textSurf.get_height()) // 2, # top
                        textSurf.get_width(),
                        textSurf.get_height()
                    )

                    self.screen.blit(textSurf, (textRect.left, textRect.top))  # 生成黑色文字在屏幕中间
                    # self.screen.blit(textbgSurf, ((self.screen.get_width() - textbgSurf.get_width()) // 2, (
                    #         self.screen.get_height() - textbgSurf.get_height()) // 2))  # 生成白色描边文字在屏幕中间

                    if not DEBUG:
                        dirty_rects.append(textRect)
                        pygame.display.update(dirty_rects) # 更新脏块（包括点开的地方和/或粉色块）和文字所在区域
                    else:
                        pygame.display.update()

                    time.sleep(2)
                    self.game_reset()
                    break

                else:
                    # update dirty rects
                    if not DEBUG:
                        pygame.display.update(dirty_rects)
                    else:
                        pygame.display.update()

            if exitFlag.get():
                break


        # TODO 格子之间留点缝隙
        # TODO display mine cnt

    def blit_remains2pinks(self, dirty_rects):
        """
        把雷都变成粉色块并blit到screen
        :param dirty_rects: 用于加入脏的rect
        """
        dirty_poses = []

        self.map.set_remains2pinks(dirty_poses)

        # blit dirty blocks
        for _x, _y in dirty_poses:
            tile_i = self.map.mm[_x][_y].getTileI().value
            self.screen.blit(self.tile_list[tile_i], (
                int((_y - 1) * TILE_WIDTH * self.SCALE), int((_x - 1) * TILE_HEIGHT * self.SCALE)))

        # log dirty rects for update screen
        for x, y in dirty_poses:
            dirty_rects.append(self.block_rects[x - 1][y - 1])


    def game_reset(self) -> None:
        """重置游戏"""
        # 重置mm和其他参数
        self.map.reset()

        # blit background pic
        self.screen.blit(self.bgsurf, (0, 0))

        # blit all blocks from map to screen
        self._blitAllBlocks()

        # reset click state
        self.clickResult = ClickResult(RESULT.CONTINUE_CHANGED)

        # draw to main
        pygame.display.update()

        # --------------------------------------------------------------
        # algo initialization (responsive to keyboard)
        if self.enable_algo:
            if DEBUG:
                from Algorithm.main import Debugger
                debugger = Debugger(
                    screen=self.screen,
                    tile_list=self.tile_list,
                    TILE_WIDTH=TILE_WIDTH,
                    SCALE=self.SCALE,
                    TILE_HEIGHT=TILE_HEIGHT,
                    pygame=pygame
                )
                self.AlgoSolver = AlgoSolver(self.map, debugger)
            else:
                self.AlgoSolver = AlgoSolver(self.map)

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
        #TODO other stuff like animation

    def _do_Mid_Click(self, x, y, dirty_poses: List[Tuple[int, int]]) -> None:
        self.clickResult = self.map.midClick(x, y, dirty_poses)
        #TODO other stuff like animation

    def _do_Right_Click(self, x, y, dirty_poses: List[Tuple[int, int]]) -> None:
        self.clickResult = self.map.rightClick(x, y, dirty_poses)
        #TODO other stuff like animation

    def _load_All_Blocks_Rects(self):
        """根据map长宽确定每一格对应的rect大小和位置"""
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