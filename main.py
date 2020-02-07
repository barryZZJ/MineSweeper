import MineSweeperGame as MSG
from MineSweeperGame.mapGen import Map, Difficulty

game = MSG.gameUtil.GameUtil() # generate pygame util
_map = Map(Difficulty.EASY) # generate map
game.startNewGame(True, _map)