Entity
======

.. currentmodule:: pypunk.core

.. class:: Entity
   Main game Entity class, updated by World.

   :param x: X position to place the Entity.
   :param y: Y position to place the Entity.
   :param graphic: Graphic to assign to the Entity.
   :param mask:    Mask to assign to the Entity.
   
   .. note::

      Make sure to call ``super().__init__()`` if overriding to ensure
      World instance is set up correctly.

   .. attribute:: visible = True

      If the Entity should render.

   .. attribute:: collideable = True

      If the Entity should respond to collision checks.

   .. attribute::
      x
      y

      X/Y position of the Entity in the World

   .. attribute::
      width
      height

      Width/Height of the Entity's hitbox

   .. attribute::
      origin_x
      origin_y

      X/Y origin of the Entity's hitbox

   .. attribute:: render_target = None

      The Screen object to draw the entity onto. Leave
      as None to render to the primary window.

   .. method::
      added()
      removed()

      Override these, called when the Entity is added/removed to/from
      a world.

   .. method:: update()

      Override this, called every frame by the current World as part
      of the main game loop.

   .. method:: render()

      Renders the Entity's Graphic. If you override this to implement
      additional behaviour, remember to call ``super().render()`` to
      ensure the Entity is drawn.

   .. method:: collide(t, x, y)

      Checks for a collision between the Entity, positioned at
      ``(x, y)``, and an Entity of type ``t``. Returns the first Entity
      collided with, or ``None`` if there was no collision.

   .. method:: collide_types(types, x, y)

      Same as :py:meth:`collide`, but checks against a list of Entity
      types ``types``.

   .. method:: collide_with(e, x, y)

      Same as :py:meth:`collide`, but checks against a single Entity
      instance, ``e``.

   .. method:: collide_rect(x, y, r_x, r_y, r_width, r_height)

      Returns whether the Entity, positioned at ``(x, y)``, overlaps
      the specified rectangle at ``(r_x, r_y)`` with dimensions
      ``r_width x r_height``.

   .. method:: collide_point(x, y, p_x, p_y)

      Returns whether this Entity, positioned at ``(x, y)``, overlaps
      the specified position ``(p_x, p_y)``

   .. todo::

      * collide_into
      * collide_types_into
      * on_camera

   .. attribute:: world

      Read only. The World object this Entity has been added to.

   .. attribute::
      center_x
      center_y

      The center x/y position of the Entity's hitbox area.

   .. attribute::
      left
      right
      top
      bottom

      The left/right/top/bottom-most position of the Entity's hitbox.

   .. attribute:: layer

      The rendering layer of this entity. Higher layers are rendered first.

   .. attribute:: type

      The collision type, used for collision checks.

   .. todo::

      Mask support.

   .. attribute:: graphic

      Graphic object to render to the screen during the render loop.

   .. method:: add_graphic(g)

      Adds the Graphic ``g`` to the Entity via a Graphicslist

   .. method:: set_hitbox(width, height, origin_x, origin_y)

      Sets the Entity's hitbox properties.

   .. method:: set_hitbox_to(o)

      Sets the Entity's hitbox to math that of the provided object ``o``.

   .. method:: set_origin(x=0, y=0)

      Sets the origin of the Entity to ``(x, y)``.

   .. method:: center_origin()

      Sets the Entity's origin to ``(width/2, height/2)``.

   .. todo::

      * distance_from
      * distance_to_point
      * distance_to_rect
      * move_by
      * move_to
      * move_towards
      * move_collide_x
      * move_collide_y

   .. method::
      clamp_horizontal(left, right, padding=0)
      clamp_vertical(top, bottom, padding=0)

      Clamps the Entity's hitbox on the x/y axis, between ``(left, right)``
      /``(top, bottom)``, with optional additional ``padding``.