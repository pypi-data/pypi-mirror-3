# Example of creating sprites in easypg using mix-in classes.
#
# Copyright (c) 2011 Nick Efford <nick.efford (at) gmail.com>
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

import pygame

from easypg.colours import GREY
from easypg.mixins import KeyControl
from easypg.mixins import LinearMotion
from easypg.mixins import MouseControl
from easypg.mixins import ReflectingBoundary
from easypg.mixins import SolidBoundary
from easypg.mixins import WrapAround
from easypg.sprites import SimpleSprite
from easypg.utils import Window
from easypg.utils import create_surface, read_arrow_keys


#class UserSprite(KeyControl, SolidBoundary, SimpleSprite):
#class UserSprite(KeyControl, WrapAround, SimpleSprite):
class UserSprite(MouseControl, SolidBoundary, SimpleSprite):

    def __init__(self, screen, image_filename):
        #KeyControl.__init__(self, speed=8)
        MouseControl.__init__(self, weight=0.4)
        SimpleSprite.__init__(self, screen, image_filename)


class ComputerSprite(LinearMotion, ReflectingBoundary, SimpleSprite):

    def __init__(self, screen, image_filename):
        LinearMotion.__init__(self, velocity=(5, 7))
        SimpleSprite.__init__(self, screen, image_filename)


class ExampleWindow(Window):

    def __init__(self, size, user_image, computer_image):
        super().__init__(size, title='Sprite Mix-ins Demo')
        user = UserSprite(self.screen, user_image)
        computer = ComputerSprite(self.screen, computer_image)
        self.group = pygame.sprite.Group(user, computer)

    def update(self):
        self.group.clear(self.screen, self.background)
        self.group.update()
        self.group.draw(self.screen)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 2:
        pygame.init()
        size = (640, 480)
        window = ExampleWindow(size, sys.argv[1], sys.argv[2])
        background = create_surface(size, GREY)
        window.display(background)
    else:
        print('Usage: python3 mixdemo.py <image1> <image2>', file=sys.stderr)
