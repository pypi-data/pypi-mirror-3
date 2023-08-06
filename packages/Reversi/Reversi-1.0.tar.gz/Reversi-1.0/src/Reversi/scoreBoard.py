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

from reversiToken import *
from gridButton import *



class Scoreboard(Frame):
    """Panel to hold the scores for a player."""


    def __init__(self, master=None, key=NBK):
        super().__init__(master)
        self.grid(sticky=(N, S, E, W))
        self.configure(padding=20)
        self.key = key

        # set up a 3*6 grid
        for c in range(2): self.columnconfigure(c, weight=1)
        for r in range(7): self.rowconfigure(r, weight=1)

        # now populate the grid
        self.createWidgets()


    def createWidgets(self):
        """Define 6 data display objects for the player, showing:
        0) the player's token
        1) the player's name
        2) their current score
        3) the number of wins
        4) percentage wins
        5) average score"""

        # player's token goes at the top
        self.icon = GridButton(self, token=self.key,
                               style='Normal.Scoreboard.TButton')
        self.icon.grid(column=0, row=0, columnspan=2, sticky=())

        # player's name
        self.nameVal = StringVar(self)
        self.nameVal.set('Name')
        self.name = Label(self, textvariable=self.nameVal, anchor='center',
                          font='helvetica 12 bold')
        self.name.grid(column=0, row=1, columnspan=2, sticky=(E, W))

        # current score
        self.scoreLbl = Label(self, text=_('Score:'))
        self.scoreLbl.grid(column=0, row=2, sticky=(E, W))
        self.scoreVal = IntVar()
        self.score = Label(self, textvariable=self.scoreVal, justify='right')
        self.score.grid(column=1, row=2, sticky=(E))

        # number of wins
        self.winsLbl = Label(self, text=_('Wins:'))
        self.winsLbl.grid(column=0, row=3, sticky=(E, W))
        self.winsVal = IntVar()
        self.wins = Label(self, textvariable=self.winsVal, justify='right')
        self.wins.grid(column=1, row=3, sticky=(E))

        # Percentage
        self.percentLbl = Label(self, text='%:')
        self.percentLbl.grid(column=0, row=4, sticky=(E, W))
        self.percentVal = IntVar()
        self.percent = Label(self, textvariable=self.percentVal,
                             justify='right')
        self.percent.grid(column=1, row=4, sticky=(E))

        # average score
        self.averageLbl = Label(self, text=_('Average:'))
        self.averageLbl.grid(column=0, row=5, sticky=(E, W))
        self.averageVal = IntVar()
        self.average = Label(self, textvariable=self.averageVal,
                             justify='right')
        self.average.grid(column=1, row=5, sticky=(E))

        # button to handle hints
        self.hints = BooleanVar(self)
        self.hints.set(False)
        self.hintsButton = Checkbutton(self, text=_('Hints'),
                                       style='NoIndicator.TCheckbutton',
                                       variable=self.hints,
                                       onvalue=True, offvalue=False)
        self.hintsButton.grid(column=1, row=6, sticky=(E))


