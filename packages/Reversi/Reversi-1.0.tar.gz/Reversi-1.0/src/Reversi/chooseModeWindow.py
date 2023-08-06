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



class ChooseMode(Toplevel):
    """Present a radiobutton so the user can select the mode of play."""

    def __init__(self, master=None, prompt=None, modes=None):
        super().__init__(master)
        self.transient(master)
        self.prompt = prompt
        self.modes = modes

        # layout on one col, and however many rows it takes...
        for c in range(1): self.columnconfigure(c, weight=1, pad=20)
        for r in range(1): self.rowconfigure(r, weight=1, pad=20)
        r = 0
        for k in self.modes.keys():
            r += 1
            self.rowconfigure(r, weight=1, pad=5)
        self.rowconfigure(r+1, weight=1, pad=20)

        self.createWidgets()


    def createWidgets(self):
        """Make the radio button choice screen."""
        # instructions/heading
        self.message = Label(self, text=self.prompt, font='helvetica 12 bold')
        self.message.grid(column=0, row=0, sticky=())

        # set up the choices on the radio buttons
        r = 0
        self.radioVar = StringVar(self)
        for k in self.modes.keys():
            r += 1
            Radiobutton(self, text=self.modes[k],
                        variable=self.radioVar, value=k)\
                        .grid(column=0, row=r, sticky=(W), padx=20)
        self.radioVar.set('n') # TODO: hardwire here - can we soften it?

        # hit OK when finished
        self.chosen = BooleanVar(self)
        self.chosen.set(False)
        self.okButton = Checkbutton(self, text='OK',
                                    style='NoIndicator.TCheckbutton',
                                    variable=self.chosen,
                                    onvalue=True, offvalue=False,
                                    command=self.ok
                                    )
        self.okButton.grid(column=0, row=r+1, sticky=(E))


    def ok(self):
        """return control to the main program."""
        self.destroy()

