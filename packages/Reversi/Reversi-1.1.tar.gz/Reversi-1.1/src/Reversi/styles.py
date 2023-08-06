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


def defineStyles(master=None):
    """Define some styles for the display of the grid button icons and
    checkbuttons."""
    style = Style(master)

    # styles for the grid and the scoreboard
    style.configure('Grid.TButton', background='dark green')
    style.configure('Normal.Scoreboard.TButton', background='#dfdfdf')
    style.configure('Selected.Scoreboard.TButton', background='red')

    # adapt the TCheckbutton layout to remove the indicator
    style.layout('NoIndicator.TCheckbutton',
                 [('Checkbutton.padding',
                  {'children':
                   [('Checkbutton.focus',
                     {'children':
                      [('Checkbutton.label', {'sticky': 'nswe'})],
                      'side': 'left', 'sticky': 'nsew'})],
                   'sticky': 'nswe'})])
    # use the TButton map as a template for the new TCheckbutton behaviour
    style.map('NoIndicator.TCheckbutton',
              {'relief': [('!disabled', 'pressed', 'sunken')]})
    # use the TButton configuration as a template for the appearance
    style.configure('NoIndicator.TCheckbutton',
                     padding='3 3',
                     width='-9',
                     shiftrelief=1,
                     relief='raised',
                     anchor='center')



