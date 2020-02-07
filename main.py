import MineSweeperGame as MSG
from MineSweeperGame.mapGen import Map, Difficulty

game = MSG.gameUtil.GameUtil() # generate pygame util
_map = Map(Difficulty.EASY,seed=5) # generate map
game.startNewGame(_map, enable_algo=True)