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

from gridButton import *
from reversiToken import *



class ChooseToken(Toplevel):
    """Present a number entry field so the user can select the mode of play."""

    def __init__(self, master=None, prompt=None):
        super().__init__(master)
        self.transient(master)
        #self.grid(sticky=(N, S, E, W))
        self.prompt = prompt

        # layout on two rows, and two cols
        for c in range(2): self.columnconfigure(c, weight=1, pad=20)
        for r in range(1): self.rowconfigure(r, weight=1, pad=20)

        self.createWidgets()


    def createWidgets(self):
        """Make the entry screen."""
        # instructions/heading
        self.message = Label(self, text=self.prompt, font='helvetica 12 bold')
        self.message.grid(column=0, row=0, columnspan=2, sticky=())

        # set up the variable to contain the result
        self.tokenVar = StringVar(self)
        self.tokenVar.set('')

        # display the buttons for the two choices
        c = 0
        for k in playerTokens.keys():
            gridButton = GridButton(self, playerTokens[k].tk)
            gridButton.grid(column=c, row=1, sticky=())
            gridButton.configure(pad=20,
                                 style='Normal.Scoreboard.TButton',
                                 command=lambda arg1=gridButton:
                                 self.choose(arg1))
            c += 1


    def choose(self, gridButton):
        """make a selection and return control to the main program."""
        self.tokenVar.set(gridButton.token.get())
        self.destroy()

