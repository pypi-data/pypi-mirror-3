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
from location import *

# the image file names - also used in the pygame interface
from graphics import *

# place-holders. We have to set up the images at run-time.
#blackImage = 'BWSmiley-75x75.gif'
#whiteImage = 'WBSmiley-75x75.gif'
#hintImage = 'star-75x75.gif'
#unplayedImage = 'unplayed-75x75.gif'
tokenImageChoices = {NBK: blackImageFile, NWH: whiteImageFile} # for player choice
tokenImage = {NBK: blackImageFile,
              NWH: whiteImageFile,
              NH: hintImageFile,
              NU: unplayedImageFile} # for board play



class TokenVar(StringVar):
    """Subclass of StringVar enables us to set the image and token attributes of
    the widget by game interaction (I hope)."""


    def __init__(self, master=None, value=NU, name=None):
        """Make sure we have references to the parent widget."""
        super().__init__(master, value, name)


    def set(self, token):
        """Extend the parent to set the image and token attributes in the
        parent."""
        super().set(token)
        self._master.setToken(token)



class GridButton(Button):
    """Visual representation of a Reversi board grid square. Contains all the
    information it needs to display itself and interact with the game when
    clicked."""


    def __init__(self, master=None,
                 token=NU, pos=TOP_LEFT, style='Grid.TButton'):
        """Do the class initialization and prepare the game-specific attributes."""
        super().__init__(master, text=str(token), style=style)
        self.master = master

        # this button's grid position and its current token.
#        self.token = token
        self.pos = pos

        # set up the image
#        self.setToken(token.tk)
        self.token = TokenVar(self, token)
        self['textvariable'] = self.token

        # set up the callout
        self['command'] = self.selected


    def setToken(self, key):
        """TokenVar callout to change the displayed image to match the token."""
#        self.token.tk = key
        file = tokenImage[key]
        image = PhotoImage(master= self.master, file=file)
        self.image = image
        self.configure(image=image)


    def selected(self):
        """This is the callout for when the grid location is chosen by a player.
        The location is presented to the parent board, where it can be inspected
        by the game loop."""
        self.master.chosen = self.pos

