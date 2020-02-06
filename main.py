import MineSweeperGame as MSG
from MineSweeperGame.mapGen import Map, Difficulty

game = MSG.gameUtil.GameUtil()
_map = Map(Difficulty.HARD)
game.startNewGame(True, _map)