"""
The ``core`` module provides the base functionality of the
framework, such as World and Entity management, and the
main game loop.
"""

# Import the other core classes
from ._engine import Engine, Screen
from ._entity import Entity
from ._graphics import Graphic
from ._pp import PP
from ._sound import Sfx
from ._tweening import Tweener, Tween
from ._world import World

class PyPunkError(Exception): pass
