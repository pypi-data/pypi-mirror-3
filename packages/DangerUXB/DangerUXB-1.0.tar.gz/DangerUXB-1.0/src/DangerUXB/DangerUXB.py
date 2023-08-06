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
from gameWindow import GameWindow
from styles import setupStyles

gridX = 8
gridY = 8
nMines = 10

def quitGame():
    """Exit the current game."""
    rootWindow.destroy()
    sys.exit()

# some basics for the root window
rootWindow = Tk()
rootWindow.resizable(True, True)
rootWindow.title('Danger UXB')
rootWindow.protocol('WM_DELETE_WINDOW', quitGame)

# initialize the font styles
setupStyles()

# initialize the display
gameWindow = GameWindow(rootWindow)
rootWindow.gameWindow = gameWindow

# start the first game
gameWindow.toolbar.startButton.invoke()

# run the game
gameWindow.mainloop()
rootWindow.destroy()
