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
from toolbar import Toolbar
from statusBar import StatusBar
from gridWindow import GridWindow



class GameWindow(Frame):
    """Frame defining the game controls and space for the game grid."""


    def __init__(self, master=None):
        """Initialize the toolbar and reserve space for the game grid."""
        super().__init__(master)

        # initialize the game grid to nothing
        self.gameGrid = None

        # stick the frame to the parent window.
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)
        self.grid(column=0, row=0, sticky=(N,S,E,W))

        # define 3 rows, for the toolbar, the game grid, and the status bar
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # don't vertically resize the toolbar ...
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0) # ... or the status bar

        self.createWidgets()


    def createWidgets(self):
        """Make the toolbar & status bar and define space for the game grid."""
        # toolbar
        self.toolbar = Toolbar(self)
        self.toolbar.grid(column=0, row=0, sticky=(N,S,E,W))

        # container for game grid
        self.gameContainer = Frame(self)
        self.gameContainer.grid(column=0, row=1, sticky=(N,S,E,W))

        # status bar
        self.statusbar = StatusBar(self)
        self.statusbar.grid(column=0, row=2, sticky=(N,S,E,W))


    def startGame(self, cols=1, rows=1, mines=[]):
        """Initialize the game grid. Eventually we want to use this as a callout
        function, but for now we use it from the main program."""

        # destroy the old game if it exists
        if self.gameGrid:
            self.gameGrid.destroy()

        # do this before the list gets used
        nMines = mines.count(True)

        self.gameGrid = GridWindow(self.gameContainer,
                                   cols=cols,
                                   rows=rows,
                                   mines=mines)

        self.statusbar.reset(cols=cols, rows=rows, nMines=nMines)
        self.gameGrid.start()


