# Copyright (c) 2011-12 Nick Efford <nick.efford (at) gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


"""Mix-in classes to simplify creation of Pygame sprites."""


__author__  = 'Nick Efford'
__version__ = '0.5'


import pygame


class KeyControl:
    """Mix-in that implements keyboard control for a sprite.

       The keys that move the sprite and the speed of movement can be
       specified if required, but suitable defaults are used if not.
    """

    def __init__(self, keys=None, speed=5):
        """Creates a KeyControl object.

           The 'keys' argument is a tuple or list specifying the keys
           used to move the sprite left, right, up and down; by default,
           the arrow keys will be used.

           The 'speed' argument specifies the number of pixels moved
           per frame in the direction selected by the keys.
        """

        self.speed = speed
        if keys:
            self.keys = keys
        else:
            self.keys = (
              pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN
            )

    def move(self):
        """Moves a sprite in response to key presses."""

        dx = dy = 0
        pressed = pygame.key.get_pressed()

        if pressed[self.keys[0]]: dx -= 1
        if pressed[self.keys[1]]: dx += 1
        if pressed[self.keys[2]]: dy -= 1
        if pressed[self.keys[3]]: dy += 1

        self.rect.centerx += self.speed * dx
        self.rect.centery += self.speed * dy


class MouseControl:
    """Mix-in that implements mouse control for a sprite.

       The responsiveness of the sprite can be tuned if necessary.
    """

    def __init__(self, weight=1.0):
        """Creates a MouseControl object.

           The 'weight' argument dictates how closely the sprite will
           follow the mouse; values less than 1 (but greater than 0)
           introduce a 'lag' in the sprite's ability to follow movement
           of the mouse.
        """

        self.weight = weight

    def move(self):
        """Moves a sprite in response to mouse movement."""

        mx, my = pygame.mouse.get_pos()
        self.rect.centerx += int(self.weight*(mx - self.rect.centerx))
        self.rect.centery += int(self.weight*(my - self.rect.centery))


class LinearMotion:
    """Mix-in that implements simple linear motion for a sprite.

       Velocity must be specified, and is fixed.
    """

    def __init__(self, velocity):
        """Creates a LinearMotion object.

           Velocity must be specified as a two-tuple containing the
           distance moved per frame in the x and y directions.
        """

        self.vx, self.vy = velocity

    def move(self):
        """Moves a sprite in a straight line at constant velocity."""

        self.rect.centerx += self.vx
        self.rect.centery += self.vy


class SolidBoundary:
    """Mix-in that prevents a sprite from moving beyond the bounds
       of its associated display surface.
    """

    def check_bounds(self):
        """Checks whether a sprite is in bounds and adjusts its
           position accordingly if it is not.
        """

        w, h = self.screen.get_size()

        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right >= w:
            self.rect.right = w - 1

        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom >= h:
            self.rect.bottom = h - 1


class ReflectingBoundary:
    """Mix-in that reflects a moving, computer-controlled sprite back
       from the bounds of its associated display surface.
    """

    def check_bounds(self):
        """Checks whether a sprite is moving out of bounds and, if so,
           adjusts its velocity to move it away from any boundaries.
        """

        w, h = self.screen.get_size()

        if self.rect.left < 0 or self.rect.right >= w:
            self.vx = -self.vx

        if self.rect.top < 0 or self.rect.bottom >= h:
            self.vy = -self.vy


class WrapAround:
    """Mix-in that implements a toroidal geometry in which a sprite
       that moves off the left edge of the display surface reappears
       on the right and vice versa, similarly for top and bottom.
    """

    def check_bounds(self):
        """Checks whether a sprite is in bounds and adjusts its
           position accordingly if it is not.
        """

        w, h = self.screen.get_size()

        if self.rect.centerx < 0:
            self.rect.centerx = w - 1
        elif self.rect.centerx >= w:
            self.rect.centerx = 0

        if self.rect.centery < 0:
            self.rect.centery = h - 1
        elif self.rect.centery >= h:
            self.rect.centery = 0
