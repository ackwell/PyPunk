Engine
======

.. module:: pypunk.core

.. class:: Engine(width, height[, frame_rate=60[, title="PyPunk"]])

   Main game class. Manages game loop.

   :param width:      The width of your game.
   :param height:     The height of your game.
   :param frame_rate: The game framerate, in frames per second.
   :param title:      The window caption for your game.

   .. attribute:: paused = True

      If the game should stop updating/rendering.

   .. method:: start()

      Starts the PyPunk loop. Should be called after setting PP.world so as
      to start running the game.

   .. method:: close([event = None])

      Signals the Engine to stop it's loop, and exit the game.
