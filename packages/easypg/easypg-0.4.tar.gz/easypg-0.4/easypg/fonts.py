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


"""Tools for handling fonts in Pygame."""


__author__  = 'Nick Efford'
__version__ = '0.4'


import os, pygame


class FontManager:
    """A manager for Pygame fonts.
    
       It maintains a 'current font' and caches previously-loaded fonts.
    """

    DEFAULT_FONT_SIZE = 24

    def __init__(self):
        self.cache = {}
        self._current = None

    @property
    def current(self):
        if not self._current:
            self.set_font(self.DEFAULT_FONT_SIZE)
        return self._current

    def set_font(self, size, name=None, bold=False, italic=False):
        """Sets the current Pygame font.

           If 'name' is a filename, the font will be loaded from that file
           if necessary; otherwise, 'name' is assumed to be the name of
           a system font.  If no value is given for 'name', Pygame's default
           font will be loaded.

           Loaded fonts are cached, so switching back to a previously-used
           font is efficient.
        """

        b = 'b' if bold else ''
        i = 'i' if italic else ''
        key = '{}:{:d}{}{}'.format(name, size, b, i)

        if key in self.cache:
            self._current = self.cache[key]
        elif name == None or os.path.isfile(name):
            font = pygame.font.Font(name, size)
            if bold: font.set_bold(True)
            if italic: font.set_italic(True)
            self._current = self.cache[key] = font
        else:
            font = pygame.font.SysFont(name, size, bold, italic)
            self._current = self.cache[key] = font


FONTS = FontManager()   # global font manager
