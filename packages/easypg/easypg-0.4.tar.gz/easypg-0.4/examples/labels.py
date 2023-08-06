# Example of using Label sprites in easypg.
#
# You can toggle the text label between two different strings by
# pressing and releasing the space bar.  You can increment or
# decrement the integer label by pressing the up or down arrow keys.
#
# Copyright (c) 2012 Nick Efford <nick.efford (at) gmail.com>
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

from easypg.colours import BLACK, RED, YELLOW
from easypg.sprites import Label, Integer
from easypg.utils import Window, create_surface


class ExampleWindow(Window):

    def __init__(self, size):
        super().__init__(size, title='Label & Integer Example')
        font = pygame.font.SysFont('Sans', 40)
        word_pos = (size[0]/2, size[1]/2)
        self.word = Label(self.screen, 'Yes', font, RED, word_pos)
        number_pos = (size[0] - 10, size[1] - 10)
        self.number = Integer(self.screen, 0, font, YELLOW,
          number_pos, anchor='br')
        self.sprites = pygame.sprite.Group(self.word, self.number)

    def handle_event(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            if self.word.text == 'Yes':
                self.word.text = 'No'
            else:
                self.word.text = 'Yes'

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.number.value += 1
        if keys[pygame.K_DOWN]:
            self.number.value -= 1

        self.sprites.clear(self.screen, self.background)
        self.sprites.update()
        self.sprites.draw(self.screen)


if __name__ == '__main__':
    pygame.init()
    size = (320, 240)
    window = ExampleWindow(size)
    background = create_surface(size, BLACK)
    window.display(background)
