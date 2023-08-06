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



class StatusBar(Frame):
    """Simple container for game statistics."""


    def __init__(self, master=None):
        """Define the packing behaviour and initialize the buttons."""
        super().__init__(master)
        self.master = master

        # define the gridding behaviour for the buttons
        self.rowconfigure(0, weight=1)
        for c in range(6): self.columnconfigure(c, weight=0)
        self.columnconfigure(2, weight=1) # this fills any space

        self.createWidgets()


    def createWidgets(self):
        """Instantiate the buttons to control the game and link their
        callouts."""

        # exposed count
        self.exposed = IntVar(self, 0)
        self.exposedLabel = Label(self, textvariable=self.exposed)
        self.exposedLabel.grid(row=0, column=0, sticky=(E,))
        self.exposedMax = StringVar(self, ' / ')
        self.exposedMaxLabel = Label(self, textvariable=self.exposedMax)
        self.exposedMaxLabel.grid(row=0, column=1, sticky=(W,))

        # some padding in col 2
        padFrame = Frame(self)
        padFrame.grid(row=0, column=2, sticky=(N,S,E,W))

        # flag count
        self.flags = IntVar(self, 0)
        self.flagsLabel = Label(self, textvariable=self.flags)
        self.flagsLabel.grid(row=0, column=3, sticky=(E,))
        self.flagsMax = StringVar(self, ' / ')
        self.flagsMaxLabel = Label(self, textvariable=self.flagsMax)
        self.flagsMaxLabel.grid(row=0, column=4, sticky=(W,))


    def reset(self, cols=0, rows=0, nMines=0):
        # reset the status displays
        self.exposed.set(0)
        self.exposedMax.set(' / '+str(cols*rows - nMines))
        self.flags.set(0)
        self.flagsMax.set(' / '+str(nMines))
