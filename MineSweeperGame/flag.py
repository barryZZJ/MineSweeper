from typing import Optional
class Flag(object):
    def __init__(self, set: Optional[bool] = False):
        self._state = set

    def set(self, state=True):
        self._state = state

    def reset(self):
        self._state = False

    def get(self) -> bool:
        return self._state