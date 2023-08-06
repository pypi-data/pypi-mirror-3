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


"""Classes to simplify the use of sprites in Pygame."""


__author__ = 'Nick Efford'
__version__ = '0.5'


import collections
import io
import os
import re
import zipfile
import pygame


class SpriteError(Exception):
    pass


class SimpleSprite(pygame.sprite.Sprite):
    """A basic sprite represented by a single, static image.

       A display surface and the path to the image file must be
       supplied when creating a SimpleSprite.  The presence of an
       alpha channel can be indicated; otherwise, 'colour key'
       transparency will be assumed.  The colour key and an
       initial position can be specified if the defaults are
       not suitable.
    """

    def __init__(self, screen, image_path,
                 alpha=False, background=None, position=None):
        """Creates a SimpleSprite for the given Pygame display surface,
           using the image at the given location.

           If the image has full alpha transparency, this should be
           indicated by setting the 'alpha' argument to True; otherwise,
           it is assumed that the colour of the pixel in the top-left
           corner of the sprite image is a background colour that
           should be transparent when the sprite is rendered on screen.
           If some other specific colour represents the background, this
           can be provided as a 3-tuple using the 'background' argument.

           By default, the sprite will be positioned in the centre of the
           the display surface on which it is drawn. Other coordinates can
           be specified as a 2-tuple using the 'position' argument.
        """

        super().__init__()

        self.screen = screen

        if alpha:
            self.image = pygame.image.load(image_path).convert_alpha()
        else:
            # Load image and make background transparent

            self.image = pygame.image.load(image_path).convert()

            if not background:
                background = self.image.get_at((0, 0))
            self.image.set_colorkey(background)

        # Position the sprite

        self.rect = self.image.get_rect()
        if position:
            self.rect.center = position
        else:
            w, h = self.screen.get_size()
            self.rect.center = (w // 2, h // 2)

    def update(self):
        """Updates this sprite.

           The implementation provided here simply invokes the move
           and check_bounds methods.
        """

        self.move()
        self.check_bounds()

    def move(self):
        """Moves this sprite.

           The implementation provided here is a stub that can be
           overridden in subclasses.
        """

    def check_bounds(self):
        """Checks whether this sprite is within bounds and modifies
           sprite properties if necessary.

           The implementation provided here is a stub that can be
           overridden in subclasses.
        """


class Sprite(pygame.sprite.Sprite):
    """A sprite consisting of (potentially) multiple images.

       It is assumed that the sprite can be in different states.  For each
       state, there can be different sets of sprite images representing
       the eight compass directions, and for each direction there can be a
       stack of images representing an animation sequence.

       The images themselves can be in a single directory or Zip archive
       and the main part of the filename (excluding the extension) should
       have the following format:

           [<state>]_[<direction>]_<num>

       <state> is optional.  If present, it consists of a short string of
       ASCII alphabetic characters.

       <direction> is also optional.  If present, it must be one of the
       following strings: 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'

       <num> is two decimal digits.  An image numbered 00 is required,
       but images numbered 01...99 are optional.

       Images are loaded into a dictionary called 'images'.  Note that this
       dictionary is not defined here.  IT MUST BE DEFINED IN A SUBCLASS,
       ideally as a class variable so that the loaded images can be shared
       by all instances of that subclass.

       Keys of this dictionary are states, with '-' representing an
       undefined state; values are themselves dictionaries, each of which
       has compass directions as keys (with '-' representing an undefined
       direction) and a corresponding list of Pygame surfaces as the
       value associated with each key.  This list of Pygame surfaces is
       used as an animation sequence for a particular state/direction.
    """

    image_regexp = re.compile('([a-zA-Z]*)_([a-zA-Z]*)_(\d\d)')

    def __init__(self, screen, path,
                 alpha=False, background=None, position=None,
                 state='-', direction='-'):
        """Creates a Sprite object for the given Pygame display surface,
           using the images at the given location.

           The required 'path' argument is either a path to a directory
           or a path to a Zip archive, containing sprite images.

           If the images have full alpha transparency, this should be
           indicated by setting the 'alpha' argument to True; otherwise,
           it is assumed that the colour of the pixel in the top-left
           corner of each sprite image is a background colour that should
           be transparent when the sprite is rendered on screen.  If some
           other specific colour represents the background, this can be
           provided as a 3-tuple using the 'background' argument.

           By default, the sprite will be positioned in the centre of the
           the display surface on which it is drawn. Other coordinates can
           be specified as a 2-tuple using the 'position' argument.

           An initial state and direction can be specified if needed;
           they default to '-', meaning 'undefined'.
        """

        super().__init__()

        self.screen = screen
        self.alpha = alpha
        self.background = background
        self.state = state
        self.direction = direction

        if not hasattr(self, 'images'):
            raise SpriteError('no image store defined')
        elif not isinstance(self.images, dict):
            raise SpriteError('image store must be a dictionary')

        if os.path.isfile(path) and path.endswith('.zip'):
            self._load_from_zip(path)
        elif os.path.isdir(path):
            self._load_from_dir(path)
        else:
            raise SpriteError('invalid image location')

        self.frame = 0
        self.counter = self.anim_delay = 3
        self.sequence = self.images[self.state][self.direction]
        self.image = self.sequence[self.frame]

        self.rect = self.image.get_rect()
        if position:
            self.rect.center = position
        else:
            w, h = self.screen.get_size()
            self.rect.center = (w // 2, h // 2)

    def _load_from_dir(self, path):
        contents = sorted(os.listdir(path))
        for (state, direction, _), name in self._find_images(contents):
            image_path = os.path.join(path, name)
            if self.alpha:
                image = pygame.image.load(image_path).convert_alpha()
            else:
                image = pygame.image.load(image_path).convert()
                self._set_background(image)
            self.images[state][direction].append(image)

    def _load_from_zip(self, path):
        archive = zipfile.ZipFile(path)
        contents = sorted(archive.namelist())
        for (state, direction, _), name in self._find_images(contents):
            data = archive.open(name).read()
            source = io.BytesIO(data)
            if self.alpha:
                image = pygame.image.load(source).convert_alpha()
            else:
                image = pygame.image.load(source).convert()
                self._set_background(image)
            self.images[state][direction].append(image)

    def _find_images(self, names):
        found = collections.OrderedDict()

        for name in names:
            match = self.image_regexp.match(name)
            if match:
                # Valid image file, so record details in dictionary

                state = match.group(1) or '-'
                direction = match.group(2) or '-'
                num = match.group(3)
                found[(state, direction, num)] = name

                # Prepare image store to hold loaded images

                if state not in self.images:
                    self.images[state] = {}
                if direction not in self.images[state]:
                    self.images[state][direction] = []

        return found.items()

    def _set_background(self, image):
        if self.background:
            image.set_colorkey(self.background)
        else:
            colour = image.get_at((0, 0))
            image.set_colorkey(colour)

    def update(self):
        """Updates this sprite.

           The implementation provided here simply invokes the check_state,
           animate, move and check_bounds methods.
        """

        self.check_state()
        self.animate()
        self.move()
        self.check_bounds()

    def check_state(self):
        """Checks this sprite's state, changing it if necessary.

           The implementation provided here is a stub that can be
           overridden in subclasses.
        """

    def animate(self):
        """Animates this sprite by changing its image at regular intervals."""

        self.counter -= 1
        if self.counter == 0:
            self.counter = self.anim_delay
            self.frame += 1
            if self.frame >= len(self.sequence):
                self.frame = 0
            self.image = self.sequence[self.frame]

    def move(self):
        """Moves this sprite.

           The implementation provided here is a stub that can be
           overridden in subclasses.
        """

    def check_bounds(self):
        """Checks whether this sprite is within bounds and modifies
           sprite properties if necessary.

           The implementation provided here is a stub that can be
           overridden in subclasses.
        """


class Label(pygame.sprite.Sprite):
    """A sprite for a text label - e.g., a score or timer.

       A display surface, some initial text, a Font object, a colour
       (RGB 3-tuple) and a position (2-tuple) must be provided when
       creating a Label object.  An anchor point may optionally be
       specified (this is the point on the label boundary corresponding
       to the given position).

       To update a Label object, simply assign a string to its 'text'
       field; the assigned text will be rendered on the next update of
       the sprite.
    """

    def __init__(self, screen, text, font, colour, position, anchor='c'):
        """Creates a Label for the given Pygame display surface, using
           the string, font, colour and position provided.

           By default, the Label will be centered at the given position
           (anchor='c'), but other anchor points are possible:

               'tr' - top right
               'mr' - middle right
               'br' - bottom right
               'mb' - middle bottom
               'bl' - bottom left
               'ml' - middle left
               'tl' - top left
               'mt' - middle top
        """

        super().__init__()

        self.screen = screen
        self._text = text
        self.font = font
        self.colour = colour
        self.position = position
        self.anchor = anchor.lower()

        self._create_image()
        self.refresh = False

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, new_text):
        self._text = new_text
        self.refresh = True

    def _create_image(self):
        self.image = self.font.render(self.text, True, self.colour)
        self.rect = self.image.get_rect()

        if self.anchor == 'tr':
            self.rect.topright = self.position
        elif self.anchor == 'mr':
            self.rect.midright = self.position
        elif self.anchor == 'br':
            self.rect.bottomright = self.position
        elif self.anchor == 'mb':
            self.rect.midbottom = self.position
        elif self.anchor == 'bl':
            self.rect.bottomleft = self.position
        elif self.anchor == 'ml':
            self.rect.midleft = self.position
        elif self.anchor == 'tl':
            self.rect.topleft = self.position
        elif self.anchor == 'mt':
            self.rect.midtop = self.position
        else:
            # default to centre
            self.rect.center = self.position

        self.refresh = False

    def update(self):
        """Updates this Label, rendering its image again if the text
           has changed since it was last rendered.
        """

        if self.refresh:
            self._create_image()


class Integer(Label):
    """A specialisation of Label, better suited to integer scores, etc.

       This class adds a 'value' field, to which an integer can be assigned.
       The field can also be incremented & decremented using += & -=.
       The formatting used to convert the value into text can be specified
       when creating the label, or by assigning a format to the 'fmt' field.
    """

    def __init__(
      self, screen, value, font, colour, position, anchor='c', fmt='d'):
        """Creates an Integer for the given Pygame display surface,
           using the value, font, colour and position provided.

           As with Label, an optional anchor point can be specified.
           A format can also be specified if required, using standard
           Python format specifier syntax.
        """

        self._value = value
        self.fmt = fmt
        text = format(value, fmt)

        super().__init__(screen, text, font, colour, position, anchor)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value
        self.text = format(new_value, self.fmt)
