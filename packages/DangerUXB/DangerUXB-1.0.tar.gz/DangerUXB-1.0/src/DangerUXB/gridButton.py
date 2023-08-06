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
from getImage import getImage


# grid direction vectors (8 points of the compass)
directions = []
for x in range(-1, 2):
    for y in range(-1, 2):
        # we skip the centre
        if not (x == y == 0): directions.append((x, y))



class GridButton(Button):
    """Visual representation of a minefield grid square. Contains all the
    information it needs to display itself and interact with the game."""


    def __init__(self, master=None, pos=None, mined=False):
        """Do the class initialization and prepare the game-specific
        attributes."""

        super().__init__(master)
        self.master = master

        # this button's grid position.
        self.pos = pos

        # is this button mined?
        self.mined = mined
        self.exploded = False

        # is this button flagged? - initialize to False
        self.flagged = False

        # initialize the mine count to zero
        self.neighbourMines = IntVar(self, 0)
        self['textvariable'] = self.neighbourMines
        self['width'] = 2 # width of the text field

        # initialize the neighbour flag count to zero
        self.neighbourFlags = 0

        # flag to emulate disabled when mines are exposed
        self.exposed = False

        # initialize the image to empty at 20 pixels
        self.imageSize = 20
        self.imageKey = 'Empty'
        self.setImage()
        self['compound'] = 'image'

        # initialize the font key to 10 pixels (half image size).
        self.fontKey = '.'.join([str(self.imageSize // 2), 'TButton'])

        # set up the event bindings
        self.bind('<ButtonRelease-1>', self.leftMouse)  # Left-Mouse
        self.bind('<ButtonRelease-3>', self.rightMouse) # Right-Mouse
        self.bind('<ButtonPress-1>',
                  lambda event, \
                         button=self._root().gameWindow.toolbar.startButton, \
                         key='Click':\
                         self._root().gameWindow.toolbar.setImage(button, key))


    def updateNeighbourMines(self):
        """Update the number of neighbouring mines after initialization. This
        only happens at the start of each game, but the cache of neighbours is
        used later."""

        mineCount = 0

        # initialize the list of neighbours
        self.neighbourList = []
        for dir in directions:
            x = self.pos[0]+dir[0]
            y = self.pos[1]+dir[1]
            if x < 0 or x >= self.master.cols or \
               y < 0 or y >= self.master.rows: continue
            neighbour = self.master.btnLookup[(x, y)]
            self.neighbourList.append(neighbour)

            # count the neighbours that are mined
            if neighbour.mined: mineCount += 1

        self.neighbourMines.set(mineCount)


    def updateNeighbourFlags(self, increment):
        """Increment or decrement the count of neighbour flags when notified of
        a change. The Boolean increment argument determines whether we add or
        remove from the tally."""

        if increment: self.neighbourFlags += 1
        else: self.neighbourFlags -= 1


    def setImage(self):
        """Set the image on the button using the key. """

        self['image'] = getImage(self, self.imageSize, self.imageKey)


    def setFont(self):
        """Set up the font to use for text. This also changes the background
        colour of the button. Different styles for different numbers of mines
        gives the numbers different foregrond colours."""

        # use a different background if the button has not been exposed
        if self.exposed:
            self['style'] = '.'.join([str(self.neighbourMines.get()),
                                      self.fontKey])
        else:
            self['style'] = self.fontKey


    def setStyle(self, fontKey):
        """Choose the style to use according to the font key passed, and set
        the image size to match."""

        self.fontKey = fontKey
        self.setFont()

        # configure the image to match the font size
        self.imageSize = int(fontKey.split('.')[0]) * 2
        self.setImage()


    def leftMouse(self, event):
        """Left-Mouse handler. We use this to clear the area."""

        # exclusions
        if self.exposed: return False
        if self.flagged: return False

        exposedNeighbours = 0

        # end game - we hit a mine - lose
        if self.mined:
            self.imageKey = 'Explosion' # lose
#            # TODO cleardown mode - not working - threading problem?
#            if self.master.exploded:
#                self.imageKey = 'UXB'

            self.setImage()
            self.exploded = True
            self.master.exploded = True

        else: # expose the button, display the number of neighbour mines
            self.expose(self)

            # propagate exposure to the neighbours if mines = flags
            if self.neighbourFlags == self.neighbourMines.get():
                for neighbour in self.neighbourList:

                    exposedNeighbours += neighbour.leftMouse(event)

            # reset the start button image
            self._root().gameWindow.toolbar.setImage(
                self._root().gameWindow.toolbar.startButton, 'Start')

        # update count of exposed buttons - potential win end game
        exposedNeighbours += 1 # add self to the count
        if event.widget == self:
            self.master.incrementExposedCount(exposedNeighbours)
        else: return exposedNeighbours


    def expose(self, widget):
        """Reveal the number of neighbour mines for this button."""

        # disable the button and change its colour once it has been clicked
        self.exposed = True
        self.setFont()

        if self.neighbourMines.get() == 0:
            self.imageKey = 'Empty'
            self.setImage()
        else:
            self['compound'] = 'text'

        # this is for when invoked by the game grid when giving hints
        if widget != self:
            self.master.incrementExposedCount(1)


    def rightMouse(self, event):
        """Right-Mouse handler. We use this to toggle mine flags."""

        if self.exposed: return

        if self.flagged:
            self.imageKey = 'Empty'
            self.setImage()
        else:
            self.imageKey = 'Flag'
            self.setImage()
        self.flagged = not self.flagged

        # notify neighbours and parent of the change
        self.master.updateFlags(self.flagged)
        for neighbour in self.neighbourList:
            neighbour.updateNeighbourFlags(self.flagged)
