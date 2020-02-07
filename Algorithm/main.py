# 暴力

import MineSweeperGame as MSG
from MineSweeperGame.flag import Flag
from MineSweeperGame.mapGen import BlockType, ClickResult as MoveResult
# from MineSweeperGame.mapGen import Block

from copy import deepcopy
from enum import IntEnum
from typing import List,Tuple, Generator, Optional

class RESULT(IntEnum):
    LOSE = 0
    WIN = 1
    CONTINUE_NOCHANGE = 3
    CONTINUE_CHANGED = 4

class VAL_RESULT(IntEnum):
    PASS = 0
    FAIL_CONT = 1
    FAIL_SKIP = 2

# class MoveResult(object):
#     def __init__(self, result:  RESULT):
#         self.result = result
#
#     def isLose(self):
#         return self.result == RESULT.LOSE
#
#     def isWin(self):
#         return self.result == RESULT.WIN
#
#     def isContinue_NoChange(self):
#         return self.result == RESULT.CONTINUE_NOCHANGE
#
#     def isContinue_Changed(self):
#         return self.result == RESULT.CONTINUE_CHANGED
class Debugger(object):
    def __init__(self, **kwargs):
        self.dict = kwargs
    def __getitem__(self, item):
        return self.dict[item]
    def __setitem__(self, key, value):
        self.dict[key] = value

class AlgoSolver(object):

    def __init__(self, _map: Optional[MSG.mapGen.Map]=None, debugger: Optional[Debugger]=None):
        self.debugger = debugger
        self._map = _map
        self._move_cnt = 0

    def solve(self, dirty_poses: Optional[List[Tuple[int, int]]]=None, _map: Optional[MSG.mapGen.Map]=None) -> MoveResult:
        # :keep moving until win/lose/noMoveLeft

        if _map:
            self._map = _map
        while 1:
            moveRes = self._move(dirty_poses)
            if not moveRes.isContinue_Changed():
                break
        return moveRes

    def step(self, dirty_poses: Optional[List[Tuple[int, int]]]=None, _map: Optional[MSG.mapGen.Map]=None) -> MoveResult:
        # :move once
        if _map:
            self._map = _map
        return self._move(dirty_poses)

    def _move(self, dirty_poses: Optional[List[Tuple[int, int]]]=None) -> MoveResult:
        self._move_cnt += 1
        # :easyMove first.
        moveRes = self._easyMove(dirty_poses)
        if moveRes.isContinue_NoChange():
            # :if no easyMove, make violent enumerate move.
            moveRes = self._violentEnumMove(dirty_poses)
            if moveRes.isContinue_NoChange():
                print(f'{self._move_cnt}. no move')
                # :if no violentMove, then no reasonable moves left.
                return MoveResult(RESULT.CONTINUE_NOCHANGE)
                # TODO ======================================
                # :if no violentMove, make best probability move.
                # return _bestProbableMove()
                # TODO ==========================================
            else:
                print(f"{self._move_cnt}. made violent enum move")
        else:
            print(f"{self._move_cnt}. made easy move")
        # :has made a move.
        return moveRes

    def _easyMove(self, dirty_poses: Optional[List[Tuple[int, int]]]) -> MoveResult:
        # 只走一步
        # seudo:
        # hasMoved = Flag()
        # for numBlock in numBlocks:
            # If neighbor flag <= num:
                # If neighbor closed + neighbor flag = num:
                    # rightClick neighbor closed blocks (set flags)
                    # hasMoved.set()
                    # [Optional: midClick flags neighboring num blocks]
                # Elif neighbor flag = num:
                    # midClick this block
                    # hasMoved.set()
                # Else:
                    # pass
            # Else:
                # raise tooManyFlagsError
        # return hasMoved.get()

        clickRes : MSG.mapGen.ClickResult

        for x, y, numBlock in self._map.allNumBlocksM():
            flag_cnt = closed_cnt = 0
            closed_neighbors = list() #type: List[Tuple[int, int]]

            # 获取numBlock邻居的closed数和flag数
            for nx, ny, neighbor in self._map.neighborBlocksM(x, y):
                if neighbor.isClosed():
                    closed_neighbors.append((nx, ny))
                    closed_cnt += 1
                elif neighbor.isFlag():
                    flag_cnt += 1

            if closed_cnt != 0:
                # 只考虑邻居有closed块的
                if flag_cnt <= numBlock.getNum():
                    if closed_cnt + flag_cnt == numBlock.getNum():
                        # can set flag
                        for closed_neighbor in closed_neighbors:
                            self._map.rightClick(*closed_neighbor, dirty_poses)
                        return MoveResult(RESULT.CONTINUE_CHANGED)
                    elif flag_cnt == numBlock.getNum():
                        # can quick open
                        clickRes = self._map.midClick(x, y, dirty_poses)
                        if clickRes.isWin(): return MoveResult(RESULT.WIN)
                        elif clickRes.isLose(): return MoveResult(RESULT.LOSE)
                        else: return MoveResult(RESULT.CONTINUE_CHANGED)
                else:
                    raise Exception("more flags than number!")
        return MoveResult(RESULT.CONTINUE_NOCHANGE)

    def _violentEnumMove(self, dirty_poses: Optional[List[Tuple[int, int]]]) -> MoveResult:
        # nextClosedBlocks = list of all closed blocks who is next to a numbered block
        # dfs traverse all nextClosedBlocks, find common mines and common empties in all enumeration
        # if mine: rightClick
        # if empty: leftClick
        # return hasMoved
        hasMoved = Flag()

        # reference in self._dfsAll
        curr_map = deepcopy(self._map.mm) #type: List[List[MSG.mapGen.Block]]

        nextClosedBlocks = list() #type: List[Tuple[int,int,MSG.mapGen.Block]]

        # -----------------------------------------------------
        # 一次只找局部相邻的一系列闭格子，减轻一次搜索的压力

        for nextClosedBlocks in self._bfsAllNextClosedBlocks(curr_map):
            # 如果当前连通图不可操作的就再看下一个连通图 (返回空列表时就结束）
            # -----------------------------------------------------
            # get all possible distributions and find common, then do clicks


            curr_perm = [BlockType.PINK for i in range(len(nextClosedBlocks))] # 初始化时所有将要被操作的格子全设置为PINK

            allPerms = list() #type: List[List[BlockType]]
            self.imgi = 0
            self._dfsAll(0, curr_map, curr_perm, nextClosedBlocks, allPerms)

            for x, y, targetType in self._findCommonBlocks(nextClosedBlocks, allPerms):
                hasMoved.set()
                if targetType == BlockType.NEW_FLAG:
                    # set flag
                    self._map.rightClick(x,y, dirty_poses)
                elif targetType == BlockType.PINK:
                    # open empty
                    clickRes = self._map.leftClick(x,y, dirty_poses)
                    if clickRes.isWin():
                        return MoveResult(RESULT.WIN)
                    elif clickRes.isLose():
                        return MoveResult(RESULT.LOSE)
            if hasMoved.get():
                return MoveResult(RESULT.CONTINUE_CHANGED)
            print("no move for this nextClosedBlocks")
        # 所有连通图都看完还时没有结果，说明没的做
        return MoveResult(RESULT.CONTINUE_NOCHANGE)

    def displayCurrMap(self, currMap: List[List[MSG.mapGen.Block]]): #For debug
        # debug: show dfs blocks
        for _x in range(1, self._map._NUM_X + 1):
            for _y in range(1, self._map._NUM_Y + 1):
                tile_i = currMap[_x][_y].getTileI().value
                self.debugger['screen'].blit(self.debugger['tile_list'][tile_i], (
                    int((_y - 1) * self.debugger['TILE_WIDTH'] * self.debugger['SCALE']), int((_x - 1) * self.debugger['TILE_HEIGHT'] * self.debugger['SCALE'])))
        self.debugger['pygame'].display.update()

    def screenShot(self, msg:Optional[str]=None): #For debug
        # debug: take current screen shot
        self.debugger['pygame'].image.save(self.debugger['screen'], f"currMap{self.imgi}_{msg}.png")
        print(f"Screen shot currMap{self.imgi}.png")
        self.imgi += 1

    def _bfsAllNextClosedBlocks(self, curr_map: List[List[MSG.mapGen.Block]]) -> Generator[List[Tuple[int, int, MSG.mapGen.Block]], None,None]:
        seen = [[False for j in range(len(curr_map[0]))] for i in range(len(curr_map))]
        foundOneClosed = Flag() # 在遍历所有块找到一个满足条件的后，就可以深搜并返回当前结果了
        nextClosedBlocks = list() #type: List[Tuple[int, int, MSG.mapGen.Block]]

        q = list() #type: List[Tuple[int,int,MSG.mapGen.Block]]

        # 先找到一个与数字相邻的closed块，添加到q中
        # TODO 有旗子格挡在中间怎么办
        for x, y, thisBlock in self._map.allBlocksM():
            # get all nextClosedBlocks
            if thisBlock.isClosed() and not seen[x][y]:
                for nx, ny, neighbor in self._map.neighborBlocksM(x, y):
                    if neighbor.isNum():
                        foundOneClosed.set()
                        q.append((x,y,thisBlock))
                        nextClosedBlocks.append((x,y,thisBlock))
                        curr_map[x][y].setType(BlockType.PINK)  # 初始化时所有将要被操作的格子全设置为PINK
                        break
            if foundOneClosed.get():
                # 深搜相邻的满足条件的块:
                # 所有相邻且在数字旁边的closed块加入nextClosedBlocks中
                while q:
                    x, y, thisBlock = q.pop()
                    nextClosedBlocks.append((x, y, thisBlock))
                    seen[x][y] = True
                    for nx, ny, neighbor in self._map.neighborBlocksM(x, y):
                        # neighbor: 当前块相邻的closed块
                        if neighbor.isClosed() and not seen[nx][ny]:
                            for nnx, nny, nneighbor in self._map.neighborBlocksM(nx, ny):
                                # nneighbor: 只有相邻closed块与num相邻时才加入nextClosedBlocks中
                                if nneighbor.isNum():
                                    q.append((nx,ny,neighbor))
                                    curr_map[nx][ny].setType(BlockType.PINK)  # 初始化时所有将要被操作的格子全设置为PINK
                                    break
                yield nextClosedBlocks
                nextClosedBlocks = list()
        #全部找完之后就没有再能搜的了


    def _dfsAll(self, block_i,
                currMap: List[List[MSG.mapGen.Block]],
                currPerm: List[MSG.mapGen.BlockType],
                nextClosedBlocks: List[Tuple[int,int,MSG.mapGen.Block]],
                resPerms: List[List[MSG.mapGen.BlockType]]):
        '''
        :param block_i: Index of curr dfs block in nextClosedBlocks
        :param currMap: 当前组合的地图，初始化时所有将要被操作的格子全设置为 PINK
        :param currPerm: 当前组合的旗/空分布，初始化全为 PINK
        :param resPerms: 记录所有可能的组合
        '''

        # dfs all mines and empties, from 0 mines to all mines,
        # each time set block_i be new_flag or empty, then validate
        # results list = 所有可行的旗/空分布，与nextClosedBlocks的每个元素对应

        # TODO 优化：根据当前数字一次直接赋相应个数的雷 x
        # tODO 优化：找到某一部分的赋值情况跟其他部分独立，那么每次深搜只在这一部分进行

        #TODO 改变搜索方法：从周围有闭块的数字块入手，edgeNumBlocks: List = 这些数字块，按顺序取第一个没seen过的，优先选工作区域小，再优先选可赋雷情况少的（直接选工作区域2~3，且待赋雷1~2个的，没有再考虑其他的（可以按顺序插到数组里，插入排序）），
            #TODO 令该块[1]与其周围闭块相邻的数字块(包含seen过的)为当前工作区域，把[1]周围闭块[设为seen]的所有赋雷情况找到，
            #TODO 并找到对应每一种情况下工作区域内其他数字块周围不在[seen]周围的闭块的赋雷可能情况（如果是赋一个雷的时候其他数字块有没[seen]过的空位但不能赋雷，那么这个位置一定没雷，直接点）
            #TODO（要涉及到工作区域以外的数字，只验证当前perm新插旗的块相邻的数字块），验证时如果新插旗块相邻的且非工作区域的数字块>=周围旗数 则作为一个perm，否则淘汰。
            #TODO 然后验证这些perm有没有共性块，如果有就点，如果没有，标记这些数字块为seen，下次取的时候不从seen过的块里取。

        if block_i < len(nextClosedBlocks):
            x,y,thisBlock = nextClosedBlocks[block_i]

            # set ith as new_flag, then search next permutation
            currMap[x][y].setType(BlockType.NEW_FLAG)
            currPerm[block_i] = BlockType.NEW_FLAG

            # 只有设置雷的时候才需要检查，设为空时一定不需要，一定是FAIL
            val_Res = self._validate(currMap)
            if val_Res == VAL_RESULT.PASS:
                if self.debugger:
                    self.displayCurrMap(currMap)
                    # self.screenShot(f"flag{block_i}_pass")
                resPerms.append(deepcopy(currPerm))
            elif val_Res == VAL_RESULT.FAIL_CONT:
                if self.debugger:
                    self.displayCurrMap(currMap)
                    # self.screenShot(f"flag{block_i}_FAIL_CONT")
                # check if this permutation is possible, if so, add to result
                self._dfsAll(block_i+1, currMap, currPerm, nextClosedBlocks, resPerms)
            #else: 如果当前旗子过多，以后有没有雷也无济于事，剪枝

            # set ith empty, then search next
            currMap[x][y].setType(BlockType.PINK)
            currPerm[block_i] = BlockType.PINK

            # 只有设置雷的时候才需要检查，设为空时一定不需要，一定是FAIL
            # val_Res = self._validate(currMap)
            self._dfsAll(block_i+1, currMap, currPerm, nextClosedBlocks, resPerms)

    def _validate(self, currMap: List[List[MSG.mapGen.Block]]) -> VAL_RESULT:
        # check if this distribution is correct
        # method:
        # For numBlock in allNumBlocks:
            # If sum(numBlock.surround_flags + numBlock.surround_new_flags) == num:
            # Return True
        FAIL_CONT_FLAG = Flag()#优先返回旗多时的剪枝，如果没有剪枝再返回是继续还是验证成功
        for x, y, numBlock in self._map.allNumBlocksM():
            o_flag_cnt = n_flag_cnt = 0
            o_opened_cnt = n_opened_cnt = 0
            for nx, ny, neighbor in self._map.neighborBlocksCustom(x, y, currMap):
                if neighbor.isFlag():
                    o_flag_cnt += 1
                elif neighbor.getType() == BlockType.NEW_FLAG:
                    n_flag_cnt += 1
                elif neighbor.isEmpty() or neighbor.isNum():
                    o_opened_cnt += 1
                elif neighbor.getType() == BlockType.PINK:
                    n_opened_cnt += 1
            # 如果周围没有新开旗子且没有PINK就跳过,
            # 只考虑周围有新旗子或有Pink的数字格。
            if n_flag_cnt or n_opened_cnt:
                if o_flag_cnt+n_flag_cnt > numBlock.getNum():
                    return VAL_RESULT.FAIL_SKIP  # 旗太多，不能再加旗了，剪枝
                elif o_flag_cnt+n_flag_cnt < numBlock.getNum():
                    FAIL_CONT_FLAG.set()
        # 优先返回旗多时的剪枝，如果没有剪枝再返回是继续还是验证成功
        if FAIL_CONT_FLAG.get():
            return VAL_RESULT.FAIL_CONT
        # 全都符合条件，验证成功
        return VAL_RESULT.PASS

    @staticmethod
    def _findCommonBlocks(nextClosedBlocks: List[Tuple[int,int,MSG.mapGen.Block]],
                          allPerms: List[List[MSG.mapGen.BlockType]]) -> Generator[Tuple[int,int,MSG.mapGen.BlockType],None,None]:
        #yield 相同的格子的 x, y, NEW_FLAG/NUM_0 among all distributions
        if not allPerms: return
        col_sames = [True for i in range(len(allPerms[0]))] #假设全部相同
        for i in range(len(allPerms)-1):
            for j in range(len(allPerms[0])):
                if col_sames[j] and allPerms[i][j] != allPerms[i+1][j]:
                    #第j列不同，去掉
                    col_sames[j] = False
        for col, isSame in enumerate(col_sames):
            if isSame:
                yield nextClosedBlocks[col][0], nextClosedBlocks[col][1], allPerms[0][col]

# if __name__ == '__main__':
#     game = MSG.gameUtil.GameUtil()
#     game.startNewGame()


