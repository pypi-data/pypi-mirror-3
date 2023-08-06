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

from boardTk import BoardTk
from scoreBoard import Scoreboard
from reversiToken import *



class GameWindow(Frame):
    """The top-level window for the game"""


    def __init__(self, master=None):
        super().__init__(master)
        self.grid(sticky=(N, S, E, W))

        # define 2 columns and 3 rows with equal weight (for now)
        for c in range(2): self.columnconfigure(c, weight=1)
        for r in range(3): self.rowconfigure(r, weight=1)

        self.createWidgets()


    def createWidgets(self):
        """Define the main components of the game window."""

        # the game board play area
        self.board = BoardTk(self)
        self.board.grid(column=0, row=0, rowspan=3, sticky=(N, S, E, W))

        # title for the scoreboards
        self.title = Label(self, text=_('Scores'), anchor='center',
                           font='helvetica 14 bold')
        self.title.grid(column=1, row=0, sticky=(N, S, E, W))

        # scoreboards for each player
        r = 0
        self.scoreboard = dict.fromkeys(playerTokens)
        for k in self.scoreboard.keys():
            playerScores = Scoreboard(self, k)
            r += 1
            playerScores.grid(column=1, row=r, sticky=(N, S, E, W))
            self.scoreboard[k] = playerScores


