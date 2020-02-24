from typing import List, Tuple, Optional, Union, Generator
# from .constants import *
from MineSweeperGame.constants import *
from MineSweeperGame.flag import Flag

import random
from enum import IntEnum

class Difficulty(IntEnum):
    EASY = 1
    NORMAL = 2
    HARD = 3
    CUSTOM = 4

class BlockType(IntEnum):
    MINE = 9
    NUM_0 = 0
    NUM_1 = 1
    NUM_2 = 2
    NUM_3 = 3
    NUM_4 = 4
    NUM_5 = 5
    NUM_6 = 6
    NUM_7 = 7
    NUM_8 = 8
    FLAG = 10
    CLOSED = 11
    NEW_FLAG = 12 # for algorithm
    PINK = 13
    QUESTION = 14
    NA = 15 # map的第0行和第0列不应该被显示，设置为无效块

class Block(object):
    def __float__(self):
        return self._blocktype.__float__()

    def __int__(self):
        return self._blocktype

    def __init__(self, blocktype: Union[BlockType, int, None] = BlockType.NA, x=None, y=None):
        # self.x = x
        # self.y = y
        self._blocktype : BlockType
        if isinstance(blocktype, BlockType):
            # is BlockType
            self._blocktype = blocktype
        elif isinstance(blocktype, int):
            # is int
            assert (0<=blocktype<=8)
            self._blocktype = BlockType(blocktype)

    # def getPos(self) -> Tuple[int, int]:
    #     return self.x, self.y
    #
    # def getX(self) -> int:
    #     return self.x
    #
    # def getY(self) -> int:
    #     return self.y

    def isMine(self) -> bool:
        return self._blocktype == BlockType.MINE

    def notMine(self) -> bool:
        return self._blocktype != BlockType.NA and self._blocktype != BlockType.MINE

    def isEmpty(self) -> bool:
        return self._blocktype == BlockType.NUM_0

    def isFlag(self) -> bool:
        return self._blocktype == BlockType.FLAG

    def isClosed(self) -> bool:
        return self._blocktype == BlockType.CLOSED

    def isOpened(self) -> bool:
        return not (self._blocktype == BlockType.NA or self._blocktype == BlockType.CLOSED or self._blocktype == BlockType.FLAG or self._blocktype == BlockType.NEW_FLAG)

    def isNum(self, num: Optional[int] = None) -> bool:
        if num:
            return self._blocktype.value == num
        return 1<=self._blocktype.value<=8

    def setType(self, blocktype: Union[BlockType, int]) -> None:
        if isinstance(blocktype, BlockType):
            #is BlockType
            self._blocktype = blocktype
        elif isinstance(blocktype, int):
            #is int
            assert (0 <= blocktype <= 8)
            self._blocktype = BlockType(blocktype)

    def getType(self) -> BlockType:
        return self._blocktype

    def getNum(self) -> int:
        return self._blocktype.value

    def getTileI(self) -> TILE:
        if self.getType() == BlockType.CLOSED:
            return TILE.CLOSED
        if self.getType() == BlockType.FLAG:
            return TILE.FLAG
        if self.getType() == BlockType.MINE:
            return TILE.MINE
        if self.getType() == BlockType.NUM_0:
            return TILE.NUM_0
        if self.getType() == BlockType.NUM_1:
            return TILE.NUM_1
        if self.getType() == BlockType.NUM_2:
            return TILE.NUM_2
        if self.getType() == BlockType.NUM_3:
            return TILE.NUM_3
        if self.getType() == BlockType.NUM_4:
            return TILE.NUM_4
        if self.getType() == BlockType.NUM_5:
            return TILE.NUM_5
        if self.getType() == BlockType.NUM_6:
            return TILE.NUM_6
        if self.getType() == BlockType.NUM_7:
            return TILE.NUM_7
        if self.getType() == BlockType.NUM_8:
            return TILE.NUM_8
        if self.getType() == BlockType.PINK:
            return TILE.PINK
        if self.getType() == BlockType.NEW_FLAG:
            return TILE.QUESTION

class RESULT(IntEnum):
    LOSE = 0
    WIN = 1
    CONTINUE_NOCHANGE = 3
    CONTINUE_CHANGED = 4

class ClickResult(object):
    def __init__(self, result: RESULT):
        self.result = result

    def isLose(self):
        return self.result == RESULT.LOSE

    def isWin(self):
        return self.result == RESULT.WIN

    def isContinue_NoChange(self):
        return self.result == RESULT.CONTINUE_NOCHANGE

    def isContinue_Changed(self):
        return self.result == RESULT.CONTINUE_CHANGED

class Map(object):

    @staticmethod
    def getMapInfo(difficulty: Difficulty) -> Tuple[int, int, int]:
        '''returns num_x, num_y, mines'''
        if difficulty == Difficulty.EASY:
            return 9, 9, 10
        elif difficulty == Difficulty.NORMAL:
            return 16, 16, 40
        elif difficulty == Difficulty.HARD:
            return 16, 30, 99
        elif difficulty == Difficulty.CUSTOM:
            while 1:
                try:
                    x = int(input("Map width (9~30): ")) # type: int
                    y = int(input("Map height (9~24): ")) # type: int
                    z = int(input("Mine count (10~667): ")) # type: int
                    assert (9 <= x <= 30)
                    assert (9 <= y <= 24)
                    assert (10 <= z <= 667)
                    break
                except AssertionError:
                    print("Input range error, try again")
            return x, y, z

    def __init__(self, difficulty: Optional[Difficulty] = Difficulty.NORMAL, seed:Optional[int]=None):
        '''生成后记得调用generate'''

        self._NUM_X, self._NUM_Y, self._MINE_cnt = Map.getMapInfo(difficulty)

        self._MAPr = None # type: List[List[Block]] # real map
        # -----------------------------------------------------
        # generate mask map
        self._MAPm: List[List[Block]]
        # self._MAPm = [[Block(i, j, BlockType.CLOSED) for j in range(self._NUM_Y + 1)] for i in range(self._NUM_X + 1)]
        self._MAPm = [[Block(BlockType.CLOSED) for j in range(self._NUM_Y + 1)] for i in range(self._NUM_X + 1)]
        # -----------------------------------------------------
        # record remaining closed blocks to determine wether game won
        self._closed_cnt = None # type: int # remaining closed blocks (include mines and flags)
        # -----------------------------------------------------
        # record remaining mine cnt for hint (todo)
        self._remain_mine_hint = self._MINE_cnt
        # -----------------------------------------------------
        # is First Generate flag,
        # to determine if first click in self.leftClick()
        self.firstGen = True
        # -----------------------------------------------------
        self.seed = seed


    @property
    def get_nums(self) -> Tuple[int, int]:
        return self._NUM_X, self._NUM_Y

    def is_in_map(self, x, y) -> bool:
        return 1<=x<=self._NUM_X and 1<=y<=self._NUM_Y

    def neighborBlocksM(self, x, y) -> Generator[Tuple[int, int, Block], None, None]:
        for nx in range(x-1, x+2):
            for ny in range(y-1, y+2):
                if self.is_in_map(nx, ny) and (nx, ny) != (x, y):
                    yield nx, ny, self._MAPm[nx][ny]

    @staticmethod
    def neighborBlocksCustom(x, y, _mm: List[List[Block]]) -> Generator[Tuple[int, int, Block], None, None]:
        NUM_X, NUM_Y = len(_mm)-1, len(_mm[0])-1

        for nx in range(x-1, x+2):
            for ny in range(y-1, y+2):
                if 1<=nx<=NUM_X and 1<=ny<=NUM_Y and (nx, ny) != (x,y):
                    yield nx, ny, _mm[nx][ny]

    def neighborBlocksR(self, x, y) -> Generator[Tuple[int, int, Block], None, None]:
        for nx in range(x-1, x+2):
            for ny in range(y-1, y+2):
                if self.is_in_map(nx, ny) and (nx, ny) != (x, y):
                    yield nx, ny, self._MAPr[nx][ny]

    def allBlocksM(self) -> Generator[Tuple[int, int, Block], None, None]:
        for x in range(1, self._NUM_X+1):
            for y in range(1, self._NUM_Y+1):
                yield x, y, self._MAPm[x][y]

    def allBlocksR(self) -> Generator[Tuple[int, int, Block], None, None]:
        for x in range(1, self._NUM_X+1):
            for y in range(1, self._NUM_Y+1):
                yield x, y, self._MAPr[x][y]

    def allNumBlocksM(self) -> Generator[Tuple[int, int, Block], None, None]:
        # l = list()
        for x in range(1, self._NUM_X+1):
            for y in range(1, self._NUM_Y+1):
                if self._MAPm[x][y].isNum():
                    yield x, y, self._MAPm[x][y]

    @staticmethod
    def isNeighbor(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> bool:
        # determine if two tuples are neighbors (around each other)
        return abs(pos1[0] - pos2[0]) <= 1 and abs(pos1[1] - pos2[1]) <= 1

    def reshape(self):
        # reshape size and mines
        self.firstGen = False
        while 1:
            try:
                self._NUM_X = int(input("Map width (9~30): "))  # type: int
                self._NUM_Y = int(input("Map height (9~24): "))  # type: int
                self._MINE_cnt = int(input("Mine count (10~667): "))  # type: int
                assert (9 <= self._NUM_X <= 30)
                assert (9 <= self._NUM_Y <= 24)
                assert (10 <= self._MINE_cnt <= 667)
                break
            except AssertionError:
                print("Input range error, try again")
        self._MAPr = None
        self._MAPm = None
        self._remain_mine_hint = self._MINE_cnt #type: int

    def reset(self):
        '''重置'''
        self._MAPr = None  # type: List[List[Block]] # real map
        # -----------------------------------------------------
        # regenerate mask map
        for row in self._MAPm:
            for block in row:
                block : Block
                block.setType(BlockType.CLOSED)
        # -----------------------------------------------------
        # record remaining closed blocks to determine wether game won
        self._closed_cnt = None  # type: int
        # -----------------------------------------------------
        # record remaining mine cnt for hint (todo)
        self._remain_mine_hint = self._MINE_cnt  # type: int
        # -----------------------------------------------------
        # is First Generate flag,
        # to determine if first click in self.leftClick()
        self.firstGen = True

    def generate(self, noMinePos: Optional[Tuple[int, int]] = (-1, -1)):
        # generate new map
        random.seed(self.seed)

        self.firstGen = False # to determine if first click in self.leftClick(), generate on first click
        self._closed_cnt = self._NUM_X * self._NUM_Y # to determine wether game won: closed_cnt == mine_cnt
        # -----------------------------------------------------
        # randomly put mines
        # 如果j或i是0，设为墙，其他设为NUM0
        self._MAPr = [[Block(BlockType.NA if j*i == 0 else BlockType.NUM_0) for j in range(self._NUM_Y+1)] for i in range(self._NUM_X+1)]

        # 太慢了
        # # 打乱(0~_NUM_X, 0~_NUM_Y)，取Mines个Tuple放雷，防止直接生成随机数导致重复
        # tmp = [(i, j) for i in range(self._NUM_X) for j in range(self._NUM_Y)]
        # random.shuffle(tmp)

        mines = 0
        while mines != self._MINE_cnt:
            x, y = random.randint(1,self._NUM_X), random.randint(1,self._NUM_Y)
            # 如果x，y之前没有被设置过雷，且不在noMinePos的Neighbor中，则设为雷
            if not self._MAPr[x][y].isMine() and not self.isNeighbor((x,y), noMinePos):
                self._MAPr[x][y].setType(BlockType.MINE)
                mines += 1
        # -----------------------------------------------------
        # If x,y is mine, its neighboring not mine blocks' numbers +1
        for x, y, thisBlock in self.allBlocksR():
            if thisBlock.isMine():
                for nx, ny, neighbor in self.neighborBlocksR(x, y):
                    if neighbor.notMine():
                        # num++
                        num = neighbor.getNum()
                        neighbor.setType(num + 1)

    def set_remains2pinks(self, dirty_poses):
        """获胜时使用，把所有没翻开的变成粉色块，返回dirty的pos"""
        for x, y, block in self.allBlocksM():
            if block.isClosed():
                block.setType(BlockType.PINK)
                dirty_poses.append((x, y))

    def rightClick(self, x, y, dirty_poses: Optional[List[Tuple[int, int]]] = None) -> ClickResult:
        # If Closed:
            # Set Flag
        # Elif Falg:
            # Remove Flag
        # Else:
            # Do nothing
        if self._MAPm[x][y].isClosed():
            # set Flag
            self._MAPm[x][y].setType(BlockType.FLAG)
            dirty_poses.append((x, y)) if dirty_poses is not None else None
            self._remain_mine_hint -= 1
            return ClickResult(RESULT.CONTINUE_CHANGED)

        elif self._MAPm[x][y].isFlag():
            # remove Flag
            self._MAPm[x][y].setType(BlockType.CLOSED)
            dirty_poses.append((x, y)) if dirty_poses is not None else None
            self._remain_mine_hint += 1
            return ClickResult(RESULT.CONTINUE_CHANGED)

        return ClickResult(RESULT.CONTINUE_NOCHANGE)

    def midClick(self, x, y, dirty_poses: Optional[List[Tuple[int, int]]] = None) -> ClickResult:
        # If Opened:
        # auto left click neighboring closed blocks if
        # flag = curr num
        # Else: do nothing
        if self._MAPm[x][y].isOpened():
            flag_cnt = 0
            closedNeighborPoses = list() #type: List[Tuple[int, int]]
            for nx, ny, neighbor in self.neighborBlocksM(x, y):
                # neighbor is flag:
                if neighbor.isFlag():
                    flag_cnt += 1
                elif neighbor.isClosed():
                    closedNeighborPoses.append((nx, ny))
            # if neighbor flag = this num
            if self._MAPm[x][y].getNum() == flag_cnt:
                # auto click Closed neighbors
                for nx, ny in closedNeighborPoses:
                    clickRes = self.leftClick(nx, ny, dirty_poses)
                    if clickRes.isLose():
                        return ClickResult(RESULT.LOSE)
                    elif clickRes.isWin():
                        return ClickResult(RESULT.WIN)

                return ClickResult(RESULT.CONTINUE_CHANGED)

        return ClickResult(RESULT.CONTINUE_NOCHANGE)

    def leftClick(self, x, y, dirty_poses: Optional[List[Tuple[int, int]]] = None) -> ClickResult:
        """
        If Closed: replace with real block.
            If opened to:
               mine, game over.
               empty, empty_cnt--, auto bfs.
            If closed_cnt == mine_cnt, game won.
        Else (Flag or Opened): do nothing
        """

        # init flag to record if map has changed
        hasChanged = Flag()

        # Generate Map on First Click
        if self.firstGen:
            self.generate((x, y))

        queue = list()
        queue.append((x,y))

        while queue:
            x, y = queue.pop()
            if self._MAPm[x][y].isClosed():
                # only closed block is clickable, and is dirty
                dirty_poses.append((x,y)) if dirty_poses is not None else None
                hasChanged.set()
                if self._openBlock(x, y): return ClickResult(RESULT.LOSE) # game over

                # remaining closed blocks =
                self._closed_cnt -= 1
                # print(f'closed={self._closed_cnt}')

                if self._MAPr[x][y].isEmpty():
                    # if is empty block,
                    # bfs open neighbors
                    for nx, ny, _ in self.neighborBlocksM(x, y):
                        queue.append((nx,ny))

        # if 没开的只剩雷, game win
        if self._closed_cnt == self._MINE_cnt:
            return ClickResult(RESULT.WIN)
        else:
            return ClickResult(RESULT.CONTINUE_CHANGED) if hasChanged.get() else ClickResult(RESULT.CONTINUE_NOCHANGE)

    def _openBlock(self, x, y) -> bool:
        '''
        :return: Is mine
        '''
        # open a closed tile

        self._MAPm[x][y].setType(self._MAPr[x][y].getType())
        return self._MAPr[x][y].getType() == BlockType.MINE

    @property
    def mr(self) -> List[List[Block]]:
        return self._MAPr
    @property
    def mm(self) -> List[List[Block]]:
        return self._MAPm
#
# if __name__ == '__main__':
#
#     map = Map(Difficulty.NORMAL)
#     map.generate()
#
#     exit()

