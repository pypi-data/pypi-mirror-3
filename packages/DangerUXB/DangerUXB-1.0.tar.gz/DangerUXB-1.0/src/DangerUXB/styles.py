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
from tkinter.ttk import *


# a dictionary of sized font styles in the range of interest.
fontStyle = {}
fontColour = {}

# dictionary mapping colours to numbers
colour = {
          0: 'black',
          1: 'blue',
          2: 'red',
          3: 'green',
          4: 'orange',
          5: 'magenta',
          6: 'yellow',
          7: 'cyan',
          8: 'black',
          }

# invoke this method to set up the styles in the dictionary
def setupStyles():
    """Define button styles to enable rescaling font sizes according to the
    button size. Additionally set up derived styles for configuring font
    colour."""
    for font in range(10, 51, 5):

        # styles based purely on font size
        styleName = str(font)+'.TButton'
#        fontName = ' '.join(['helvetica', str(font), 'bold'])
        fontName = ' '.join(['comic', str(font), 'bold'])
        fontStyle[font] = styleName
        Style().configure(styleName, font=fontName, background='white')

        # derive colour styles
        for i, col in colour.items():
            Style().configure('.'.join([str(i), styleName]),
                              foreground=col,
                              background='light grey')

    # other styles as required.

    # FIXME configuration combobox - this does not seem to work
    print('Combobox default font: '+Style().lookup('TCombobox', 'font'))
    Style().configure('Configuration.TCombobox', font='helvetica 25 bold')
    print('Combobox Config font: '
          +Style().lookup('Configuration.TCombobox', 'font'))



