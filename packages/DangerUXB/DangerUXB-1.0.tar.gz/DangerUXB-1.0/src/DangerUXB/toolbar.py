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
import operator
from getImage import getImage

# game options (cols, rows, #mines)
gameOption = {
              '8*8-10': (8, 8, 10),
              '16*16-40': (16, 16, 40),
              '30*16-99': (30, 16, 99),
              }

# make a list of the option keys sorted by x-values
sortedList = sorted(gameOption.items(), key=operator.itemgetter(1))
optionList = []
for option in sortedList: optionList.append(option[0])
optionTuple = tuple(optionList)



class Toolbar(Frame):
    """Simple container for game control buttons."""


    def __init__(self, master=None):
        """Define the packing behaviour and initialize the buttons."""
        super().__init__(master)
        self.master = master

        # hardwire toolbar button size
        self.imageSize = 50

        # define the gridding behaviour for the buttons
        self.rowconfigure(0, weight=1)
        for c in range(7): self.columnconfigure(c, weight=0)
        self.columnconfigure(1, weight=1) # this fills any space
        self.columnconfigure(3, weight=1) # this fills any space
        self.columnconfigure(5, weight=1) # this fills any space

        self.createWidgets()


    def createWidgets(self):
        """Instantiate the buttons to control the game and link their
        callouts."""

        # some stretchy padding in cols 1, 3, 5
        for c in range(1, 6, 2):
            padFrame = Frame(self)
            padFrame.grid(row=0, column=c, sticky=(N,S,E,W))

        # start button also signals end game via changes in gif
        self.startButton = Button(self, text='Start', command=self.startGame)
        self.setImage(self.startButton, 'Start')
        self.startButton.grid(row=0, column=0, sticky=(W,))

        # hint button
        self.hintButton = Button(self, text='Hint', command=self.giveHint)
        self.setImage(self.hintButton, 'Hint')
        self.hintButton.grid(row=0, column=2, sticky=())

        # a combobox for setting the game configuration
        self.configBox = Combobox(self, style='Configuration.TCombobox')
        self.configBox['state'] = 'readonly'
        self.configBox['justify'] = 'right'
        self.configBox['width'] = 10
        self.configBox['values'] = optionTuple
        self.configBox.set(optionTuple[0])
        self.configBox.grid(row=0, column=4, sticky=(), padx=10)
        print('Style of combo is '+str(self.configBox.configure('style')[-1]))

        # quit button
        self.quitButton = Button(self, text='Quit', command=self._root().quit)
        self.setImage(self.quitButton, 'UXB')
        self.quitButton.grid(row=0, column=6, sticky=(E,))


    def startGame(self):
        """Get the chosen game parameters and then invoke the starter in the
        master."""
        # reset the start button image
        self.setImage(self.startButton, 'Start')

        # get the game configuration from the configBox
        self.gameOption = gameOption[self.configBox.get()]

        # get the current parameters
        cols, rows, nMines = self.gameOption

        # initialize the mines
        mines = [True] * nMines
        mines.extend([False] * (cols*rows - nMines))
        random.shuffle(mines)

        # invoke the game window
        self.master.startGame(cols=cols, rows=rows, mines=mines)


    def giveHint(self):
        """Give a hint to the player."""
        self.master.gameGrid.giveHint()


    def setImage(self, button, imageKey):
        """Set the image on a button using the keys. The image is stored
        locally to workaround the garbage collection bug."""
        button.image = getImage(self, self.imageSize, imageKey)
        button['image'] = button.image
