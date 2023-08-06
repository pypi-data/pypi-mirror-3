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
import random
from styles import fontStyle
from gridButton import GridButton


class GridWindow(Frame):
    """This class defines the layout of the grid buttons for the game."""

    def __init__(self, master=None, rows=1, cols=1, mines=[]):
        super().__init__(master)

        # ensure propagation of resize
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.grid(sticky=(N,S,E,W), padx=10, pady=10)

        # define the rows and columns
        self.rows = rows
        self.cols = cols

        # the randomised list of mines
        self.nmines = mines.count(True)
        self.mines = mines
        self.exploded = False # if a bomb has been hit
        self.gameOver = False # flag for game over - used for cleardown

        # tally of exposed minefield squares
        self.exposed = 0

        # the number of flags in use
        self.flags = 0

        # we need this to keep track of the buttons
        self.btnLookup = dict()

        # define the rows and cols with equal weight
        for c in range(self.cols): self.columnconfigure(c, weight=1)
        for r in range(self.rows): self.rowconfigure(r, weight=1)

        self.createWidgets()

        # bind to window resize events
        self.bind('<Configure>', self.resize)


    def createWidgets(self):
        """Make up the grid of buttons for the game."""
        for x in range(self.cols):
            for y in range(self.rows):

                # grid button
                button = GridButton(self, pos=(x, y), mined=self.mines.pop())
                button.grid(column=x, row=y, sticky=(), padx=1, pady=1)

                # add to the dictionary
                self.btnLookup[(x, y)] = button


    def start(self):
        """Prepare the grid before the player starts pressing buttons..."""
        # work out the neighbour bomb counts for this game
        for pos, button in self.btnLookup.items():
            button.updateNeighbourMines()


    def incrementExposedCount(self, increment):
        """Every time a button is exposed increment the count. When the count is
        big enough the game has been won."""

        # no count required during cleardown
        if self.gameOver: return

        self.exposed += increment
        self._root().gameWindow.statusbar.exposed.set(self.exposed)

        # test if we have won
        self.haveWeWonYet()


    def updateFlags(self, increment):
        """Increment or decrement the count of flags used when notified of
        a change. The Boolean increment argument determines whether we add or
        remove from the tally."""

        if increment: self.flags += 1
        else: self.flags -= 1
        self._root().gameWindow.statusbar.flags.set(self.flags)

        # test if we have won
        if not self.gameOver: self.haveWeWonYet()


    def haveWeWonYet(self):
        """Have we won yet?"""

        if self.exploded: self.endGame(False)

        elif not ((self.rows * self.cols) - (self.flags + self.exposed)):
            self.endGame(True)


    def endGame(self, success):
        """Finish the game."""

        self.gameOver = True # avoids recursion issues during cleardown

        if success:
            self._root().gameWindow.toolbar.setImage(
                self._root().gameWindow.toolbar.startButton,
                'Win')
        else:
            # clear down the grid
            for button in self.btnLookup.values():
                if button.exposed: continue
                elif button.flagged:
                    if button.mined: continue

                    # if the flag was bad remove it
                    else:
                        button.flagged = False
                        self.updateFlags(False)

                # press the button
                event = Event()
                event.widget = button
                button.leftMouse(event)

            self._root().gameWindow.toolbar.setImage(
                self._root().gameWindow.toolbar.startButton,
                'Lose')



    def giveHint(self):
        """Find an unplayed, unmined button near a played button and reveal it."""

        # get a randomised list of all the buttons
        buttons = list(self.btnLookup.values())
        random.shuffle(buttons)

        # find an unplayed, unmined button
        for button in buttons:
            if button.mined or button.exposed or button.flagged: continue

            # if this is not the start of the game check the button's neighbours
            if (self.flags + self.exposed):
                for neighbour in button.neighbourList:
                    if neighbour.exposed or neighbour.flagged:
                        button.expose(self)
                        return

            # at the start of the game no need to check neighbours
            else:
                # look for a button with no neighbour mines
                if not button.neighbourMines.get():
                    # make a dummy event and left-click the button
                    event = Event()
                    event.widget = button
                    button.leftMouse(event)
                    return


    def resize(self, event):
        """Method bound to the <Configure> event for resizing. Defines the
        resize behaviour. Window dimensions are re-calculated to make the
        buttons square, and the fonts used are scaled to match the button
        size."""

        # get geometry info from the root window.
        geometry = self._root().geometry()
        print('Start geometry is '+geometry)
        wm, hm, x, y = parseGeometry(geometry)

        # calculate the padding allowances - allow for toolbar & status bar
        padx = 20 + (self.cols - 1)*1
        barHeight = 20 + self._root().gameWindow.toolbar.imageSize
        pady = 20 + barHeight + (self.rows - 1)*1

        # get current dimensions, work out a sensible minimum
        buttonHeight = (hm - pady) // self.rows
        buttonWidth = (wm - padx) // self.cols
        buttonDimension = min([buttonHeight, buttonWidth])
        if buttonDimension < 20: buttonDimension = 20

        # resize the main window to the button dimensions
        wnew = (self.cols * buttonDimension) + padx
        hnew = (self.rows * buttonDimension) + pady
        geometry = '%dx%d+%d+%d' % (wnew, hnew, x, y)
        print('New   geometry is '+geometry)
        self._root().geometry(geometry)

        # choose a font height to match
        # note we assume optimal font height is 1/2 widget height.
        fontHeight = buttonDimension // 2
        print('Resizing to font '+str(fontHeight))

        # calculate the best font to use (use int rounding)
        bestStyle = fontStyle[10]               # use min size as the fallback
        if fontHeight < 10: pass                # the min size
        elif fontHeight >= 50:                  # the max size
            bestStyle = fontStyle[50]
        else:                                   # everything in between
            bestFitFont = (fontHeight // 5) * 5
            bestStyle = fontStyle[bestFitFont]

        # set the style on the buttons
        for button in self.btnLookup.values(): button.setStyle(bestStyle)


def parseGeometry(geometry):
    """Geometry parser.
    Returns the geometry as a (w, h, x, y) tuple."""

    # get w
    xsplit = geometry.split('x')
    w = int(xsplit[0])
    rest = xsplit[1]

    # get h, x, y
    plussplit = rest.split('+')
    h = int(plussplit[0])
    x = int(plussplit[1])
    y = int(plussplit[2])

    return w, h, x, y

