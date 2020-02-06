from typing import Optional
class Flag(object):
    def __init__(self, set: Optional[bool] = False):
        self._state = set

    def set(self):
        self._state = True

    def reset(self):
        self._state = False

    def get(self) -> bool:
        return self._state