# Downloader for sprite images needed by sprite.py

# The images come from the excellent Reiner's Tilesets site by Reiner
# "Tiles" Prokein; this program is provided instead of the actual images
# for licensing reasons (http://www.reinerstilesets.de/lizenz/)

import io
import os
import urllib.request
import zipfile

url = 'http://www.reinerstilesets.de/zips2d/T_doteaterghost.zip'

data = urllib.request.urlopen(url).read()
source = zipfile.ZipFile(io.BytesIO(data))

input_template = 'ghost red big bitmaps/{}{:04d}.bmp'
output_template = '{}__{:02d}.bmp'

with zipfile.ZipFile('monster.zip', 'w') as destination:
    for state in 'angry', 'fear', 'stoppedwalking':
        for num in range(16):
            input_name = input_template.format(state, num)
            output_name = output_template.format(state, num)
            with source.open(input_name) as input_file:
                data = input_file.read()
                destination.writestr(output_name, data)
