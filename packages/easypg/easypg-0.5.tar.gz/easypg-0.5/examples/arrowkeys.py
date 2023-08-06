# Example of reading arrow keys using easypg.
#
# Try pressing the arrow keys individually or in combination while
# running this program; the resulting displacement vector will be
# displayed in the Pygame window.
#
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

import pygame

from easypg.colours import WHITE
from easypg.drawing import draw_text
from easypg.fonts import FONTS
from easypg.utils import Window, read_arrow_keys


class ExampleWindow(Window):

    def __init__(self):
        super().__init__((320, 240), 'Arrow Keys Example')
        FONTS.set_font(44, 'Mono')

    def update(self):
        dx, dy = read_arrow_keys()
        vector = '({:2d},{:2d})'.format(dx, dy)
        self.screen.blit(self.background, (0, 0))
        draw_text(self.screen, vector, WHITE, (70, 80))


if __name__ == '__main__':
    pygame.init()
    window = ExampleWindow()
    window.display()
