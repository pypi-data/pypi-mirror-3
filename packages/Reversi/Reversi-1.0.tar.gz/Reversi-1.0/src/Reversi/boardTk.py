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

from guiParameters import *
from reversiToken import *
#from board import Board
from location import *
from gridButton import *



class BoardTk(Frame):
    """The playing board holds an 8*8 grid of playing squares to hold the
    playing pieces and for the players to interact with."""


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid(sticky=(N, S, E, W))

        # this attribute is used to detect when a grid button has been clicked
        self.chosen = None

        # set up the 8*8 grid
        for c in range(MAX_GRID): self.columnconfigure(c, weight=1, minsize=75)
        for r in range(MAX_GRID): self.rowconfigure(r, weight=1, minsize=75)

        # now populate the grid
        self.createWidgets()


    def createWidgets(self):
        """Set up the playing board."""
        # use a board grid of tokens as a template data structure
        self.gridArray = self.makeGrid()
        grid = self.gridArray

        # the list of lists of grid locations with their piece of the display
        for x in range(MAX_GRID):
            for y in range(MAX_GRID):

                # initialize the array of ui widgets
                grid[x][y] = GridButton(self, pos=Location([x, y]))
                grid[x][y].grid(column=x, row=y, sticky=(N, S, E, W))


    def makeGrid(self):
        """Return an empty grid data structure."""
        grid = []
        for x in range(MAX_GRID):
            grid.append([None] * MAX_GRID)
        return grid

