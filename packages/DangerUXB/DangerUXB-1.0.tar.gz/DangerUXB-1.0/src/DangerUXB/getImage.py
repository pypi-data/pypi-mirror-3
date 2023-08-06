# Copyright (C) 2012 Bob Bowles <bobjohnbowles@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from tkinter import *
import os

# link the tokens used in-game with actual files used
imageName = {'Empty': 'Empty.gif',              # \/ grid cell images \/
             1: '1.gif',
             2: '2.gif',
             3: '3.gif',
             4: '4.gif',
             5: '5.gif',
             6: '6.gif',
             7: '7.gif',
             8: '8.gif',
             'Flag': 'Flag.gif',
             'Explosion': 'Explosion.gif',      # /\ grid cell images /\
             'UXB': 'UXB.gif',                  # quit button
             'Win': 'VeryHappy.gif',            # \/ control button images \/
             'Lose': 'Confused.gif',
             'Start': 'Smile.gif',
             'Click': 'OMG.gif',
             'Hint': 'Unsure.gif',              # /\ control button images /\
             }

# define the sizes of image to use
size = {20: '20',
        30: '30',
        40: '40',
        50: '50',
        60: '60',
        70: '70',
        80: '80',
        90: '90',
        100: '100',
        150: '150',
        }

# initialize the image cache data structure
# NOTE having the cache also works round the garbage collection bug
imageCache = dict.fromkeys(size)
for dim in imageCache.keys():
    imageCache[dim] = dict.fromkeys(imageName)


def getImage(widget, dim, name):
    """Obtain an image from the file database using a size key and image key.
    Returns a PhotoImage."""

    if not imageCache[dim][name]:
        file = os.path.join('images', size[dim], imageName[name])
        imageCache[dim][name] = PhotoImage(file=file)

    return imageCache[dim][name]
