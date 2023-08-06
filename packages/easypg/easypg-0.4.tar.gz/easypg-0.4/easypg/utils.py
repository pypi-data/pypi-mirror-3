# Copyright (c) 2007-2012 Nick Efford <nick.efford (at) gmail.com>
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.


"""Various utilities to simplify the use of Pygame."""


__author__  = 'Nick Efford'
__version__ = '0.4'


import pygame
from .colours import BLACK


def create_surface(size, colour=BLACK):
    """Returns a surface with the specified size (width and height,
       as a 2-tuple) and, optionally, colour (a 3-tuple)."""

    surface = pygame.Surface(size).convert()
    surface.fill(colour)

    return surface


def create_tiled_surface(size, filename):
    """Returns a surface with the specified size (width and height, as
       a 2-tuple), tiled using the image with the given filename."""

    surface = pygame.Surface(size).convert()
    tile = pygame.image.load(filename).convert()

    width, height = size
    tile_width, tile_height = tile.get_size()

    y = 0
    while y < height:
        x = 0
        while x < width:
            surface.blit(tile, (x, y))
            x += tile_width
        y += tile_height

    return surface


def get_controller(number=0, verbose=False):
    """Attempts to initialise a game controller, returning a Joystick
       object if this is successful, otherwise None."""

    try:
        controller = pygame.joystick.Joystick(number)
        controller.init()
        if verbose:
            print(controller.get_name(), 'found...')
    except:
        controller = None

    return controller


def read_arrow_keys():
    """Reads arrow key status and returns a displacement vector (a 2-tuple)
       indicating how x & y coordinates should change in response to key
       presses.  For example, if left and up arrow keys are pressed, (-1,-1)
       is returned."""

    dx, dy = 0, 0

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:  dx -= 1
    if keys[pygame.K_RIGHT]: dx += 1
    if keys[pygame.K_UP]:    dy -= 1
    if keys[pygame.K_DOWN]:  dy += 1

    return dx, dy


def quit_detected(event):
    """Indicates whether the given event is an attempt to quit, either by
       clicking the Close Window button or pressing the Esc key."""

    return event.type == pygame.QUIT or (
      event.type == pygame.KEYUP and event.key == pygame.K_ESCAPE)


class Window:
    """A basic window that displays a Pygame surface as a background.

       The background is painted once only, before the window enters its
       display loop.  If you want a dynamic background, or if you want
       to do animation on top of the background, you will need to create
       a subclass of Window and override its update method.  Depending
       on what you are trying to achieve, you may need to repaint the
       background within your overridden method, with this code:

         self.screen.blit(self.background, (0, 0))"""

    def __init__(self, size, title='Pygame Window'):
        """Creates a window with the given size (width and height, as
           a 2-tuple) and, optionally, the given title."""

        self.size = size
        self.screen = pygame.display.set_mode(self.size)
        pygame.display.set_caption(title)

    def display(self, background=None, max_fps=30):
        """Sets the background of the Pygame window to the given surface
           and displays it.  If no surface is provided, a default is
           created.  The maximum frame rate for display updates can be
           given as a second argument, if desired."""

        if background:
            self.background = background
        else:
            self.background = create_surface(self.size)

        self.max_fps = max_fps

        self.screen.blit(self.background, (0, 0))
        clock = pygame.time.Clock()
        active = True

        while active:
            for event in pygame.event.get():
                if quit_detected(event):
                    active = False
                    break
                else:
                    self.handle_event(event)

            clock.tick(self.max_fps)
            self.update()
            pygame.display.flip()

    def handle_event(self, event):
        """A stub that can be overridden by subclasses to handle events."""

    def update(self):
        """A stub that can be overridden by subclasses to update the
           display on a frame-by-frame basis, e.g. with moving sprites."""
