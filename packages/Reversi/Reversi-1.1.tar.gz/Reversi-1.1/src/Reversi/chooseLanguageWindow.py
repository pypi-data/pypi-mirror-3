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
import styles

#import gettext

# runtime selectable languages
from languages import languageIds, languages



class ChooseLanguage(Toplevel):
    """Present a radiobutton so the user can select a language."""

    def __init__(self, master=None, prompt=None):
        super().__init__(master)
        self.transient(master)
        self.prompt = prompt

        # layout on one col, and however many rows it takes...

        for c in range(1): self.columnconfigure(c, weight=1, pad=20)
        for r in range(1): self.rowconfigure(r, weight=1, pad=20)
        r = 0
        for k in languageIds.keys():
            r += 1
            self.rowconfigure(r, weight=1, pad=5)
        self.rowconfigure(r+1, weight=1, pad=20) # add a row for the OK button

        self.createWidgets()


    def createWidgets(self):
        """Make the radio button choice screen."""
        # instructions/heading
        self.message = Label(self, text=self.prompt, font='helvetica 12 bold')
        self.message.grid(column=0, row=0, sticky=())

        # set up the choices on the radio buttons
        r = 0
        self.radioVar = StringVar(self)
        for k in languageIds.keys():
            r += 1
            Radiobutton(self, text=languageIds[k],
                        variable=self.radioVar, value=k,
                        command = self.changeLanguage)\
                        .grid(column=0, row=r, sticky=(W), padx=20)
        self.radioVar.set('en_GB') # TODO: hardwire here - can we soften it?

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
        """Return control to the main program."""
        self.destroy()


    def changeLanguage(self):
        """Change the translation language to the one selected."""
        languages[self.radioVar.get()].install()



def quitGame():
    """Early definition here wipes the app if invoked. A gentler version is
    defined in the main UI."""
    rootWindow.destroy()
    sys.exit()

# start the main window and set up window-killing callback
rootWindow = Tk()
rootWindow.resizable(True, True)
rootWindow.protocol('WM_DELETE_WINDOW', quitGame)

# implement styles
styles.defineStyles(rootWindow)

# set up a default language in case none gets picked
#gettext.install(domain, localedir)

# language changer invocation
chooseLanguageWindow = ChooseLanguage(rootWindow, _('Language:'))
while not chooseLanguageWindow.chosen.get():
    chooseLanguageWindow.update()
rootWindow.destroy()

