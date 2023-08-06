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



class ChooseText(Toplevel):
    """Present a text entry field so the user can select the mode of play."""

    def __init__(self, master=None, prompt=None):
        super().__init__(master)
        self.transient(master)
        #self.grid(sticky=(N, S, E, W))

        self.prompt = prompt

        # layout on one row, and two cols
        for c in range(2): self.columnconfigure(c, weight=1, pad=20)
        for r in range(2): self.rowconfigure(r, weight=1, pad=20)

        self.createWidgets()


    def createWidgets(self):
        """Make the entry screen."""
        # instructions/heading
        self.message = Label(self, text=self.prompt, font='helvetica 12 bold')
        self.message.grid(column=0, row=0, columnspan=2, sticky=())

        # set up the entry field
        self.textVar = StringVar(self)
        self.textVar.set('')
        self.text = Entry(self, textvariable=self.textVar)
        self.text.grid(column=0, row=1, sticky=())

        # hit OK when finished
        self.chosen = BooleanVar(self)
        self.chosen.set(False)
        self.okButton = Checkbutton(self, text='OK',
                                    style='NoIndicator.TCheckbutton',
                                    variable=self.chosen,
                                    onvalue=True, offvalue=False,
                                    command=self.ok
                                    )
        self.okButton.grid(column=1, row=1, sticky=())


    def ok(self):
        """return control to the main program."""
        self.destroy()

