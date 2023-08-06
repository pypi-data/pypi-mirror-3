# Example of creating a multi-image Sprite in easypg.
#
# NOTE: you will need to run getsprites.py before trying this!
# (Otherwise you'll see an 'invalid image location' error)
#
# When the program is running, you can steer the sprite using the
# arrow keys and change its state using the space bar.
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
from easypg.sprites import Sprite
from easypg.utils import Window
from easypg.utils import create_surface, read_arrow_keys


class ExampleSprite(Sprite):

    images = {}

    def __init__(self, screen):
        super().__init__(screen, 'monster.zip', state='angry')

    def toggle_state(self):
        self.state = 'fear' if self.state == 'angry' else 'angry'
        self.sequence = self.images[self.state][self.direction]

    def move(self):
        dx, dy = read_arrow_keys()
        self.rect.centerx += 5*dx
        self.rect.centery += 5*dy

    def check_bounds(self):
        w, h = self.screen.get_size()
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right >= w:
            self.rect.right = w - 1
        if self.rect.top < 0:
            self.rect.top = 0
        elif self.rect.bottom >= h:
            self.rect.bottom = h - 1


class ExampleWindow(Window):

    def __init__(self, size):
        super().__init__(size, title='Sprite Example')
        self.sprite = ExampleSprite(self.screen)
        self.sprites = pygame.sprite.Group(self.sprite)

    def handle_event(self, event):
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            self.sprite.toggle_state()

    def update(self):
        self.sprites.clear(self.screen, self.background)
        self.sprites.update()
        self.sprites.draw(self.screen)


if __name__ == '__main__':
    pygame.init()
    size = (640, 480)
    window = ExampleWindow(size)
    background = create_surface(size, GREY)
    window.display(background)
