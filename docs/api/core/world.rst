World
=====

.. currentmodule:: pypunk.core

.. class:: World

   Updated by Engine, main game container that holds all currently
   active Entities.

   Useful for organization, eg. "Menu", "Level1", etc.

   .. todo::

      Usage example, etc.

   .. note::

      Make sure to call ``super().__init__()`` if overriding to ensure
      World instance is set up correctly.

   .. attribute:: visible = True

      If False, the World will not be rendered.

   .. attribute:: self.camera = Point()

      Point used to modify location entities are drawn at.

   .. method:: begin()

      Override this; called when the World is changed, and is set to
      the currently active world.

   .. method:: end()

      Override this; called when the World is changed, and the active
      world is no longer this.

   .. method::
      update()
      render()

      Executed by the game loop, updates/renders all contained Entities.

      .. note::

         If you override these to give your World update/render code,
         remeber to call ``super().update()`` or your Entities will not
         be updated/rendered.

   .. attribute::
      mouse_x
      mouse_y

      Read only. X/Y position of the mouse in the World.

   .. method::
      add(e)
      remove(e)

      Adds/removes Entity ``e`` to/from the World at the end of the frame.
      Returns the added/removed Entity.

   .. method::
      add_list(entity[, entity [...]])
      remove_list(entity[, entity [...]])

      Adds/removes passed Entities to/from the World at the end of the frame.
      If the first argument is a ``list``, it will be used instead.

   .. method:: remove_all()

      Removes all Entities from the World at the end of the frame.

   .. add_graphic(graphic[, layer=0[, x=0[, y=0]]])

      Adds an Entity to the World with the specified Graphic object.

      :param Graphic graphic: The Graphic object to assign to the Entity.
      :param int x:     X position of the Entity.
      :param int y:     Y position of the Entity.
      :param int layer: Layer of the Entity.
      :return: The added Entity object.

   .. todo::

      Mask handling.

   .. method::
      bring_to_front(e)
      send_to_back(e)

      Brings/sends the Entity ``e`` to the front/back of it's containing
      layer. Returns ``True`` if successful.

   .. method::
      bring_forward(e)
      send_backward(e)

      Brings/sends the Entity ``e`` once position towards the front/back of
      it's containing layer. Returns ``True`` if successful.

   .. method::
      is_at_front(e)
      is_at_back(e)

      Returns whether the Entity ``e`` is at the front/back of it's layer.

   .. todo::

      Collide Functions.

   .. attribute:: count

      Read only. Number of Entities that are in the World.

   .. method:: type_count(t)

      Returns the number of Entities of the type ``t`` that are in the World.

   .. method:: class_count(c)

      Returns the number of Entities of the class ``c`` that are in the World.

   .. method:: layer_count(l)

      Returns the number of Entities on the layer ``l``.

   .. attribute:: first

      Read only. The first Entity in the World update order.

   .. attribute:: layers

      Read only. Number of Entity layers the World has.

   .. method:: type_first(t)

      The first Entity of type ``t``.

   .. method:: class_first(c)

      The first Entity of class ``c``.

   .. method::
      layer_first(l)
      layer_last(l)

      The first/last Entity on layer ``l``.

   .. attribute::
      farthest
      nearest

      Read only. The Entity that will be rendered first/last by the World.

   .. attribute::
      layer_farthest
      layer_nearest

      Read only. The Entity that will be rendered first/last by the World.

   .. attribute:: unique_types

      Read only. The number of different types that have been added to the World.

   .. method:: get_type(t, into)

      Adds all Entities of type ``t`` to provided list ``into``.

   .. method:: get_class(c, into)

      Adds all Entities of class ``c`` to provided list ``into``.

   .. method:: get_layer(l, into)

      Adds all Entities on layer ``l`` to provided list ``into``.

   .. method:: get_all(into)

      Adds all Entities in World to provided list ``into``.
