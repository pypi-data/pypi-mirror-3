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


import ui


class Mode(object):
    """The mode of play. Valid modes are:
    (p)vp:            'hot-seat' human vs. human
    (n)ormal:         human vs. computer
    (c)omputer:       computer vs. computer (TV mode)
    (b)enchtest:      computer vs. computer (benchtest - no visuals)"""
    PVP = 'p'
    NORMAL = 'n'
    COMPUTER = 'c'
    BENCH = 'b'
    MODES = {NORMAL: _('Normal human vs. computer'),
             PVP: _('Person vs. person'),
             COMPUTER: _('Computer vs. computer TV mode'),
             BENCH: _('Bench-test (no UI)')}


    def __init__(self, mode=None):
        """Can define this mode during construction, or initiate a user dialog."""
        if not mode or mode not in Mode.MODES.keys(): mode = self.chooseMode()
        self.mode = mode
        self.debugMode = False # toggle for debugging mode


    def chooseMode(self):
        """Set up mode of play interactively."""
        modes = Mode.MODES      # shorthand
        mode = ''
        while mode not in modes.keys():
            mode = ui.getMode(_('Choose a mode:'), modes)
        return mode


    def normal(self):
        """Returns whether the mode is normal."""
        return self.mode == Mode.NORMAL

    def pvp(self):
        """Returns whether the mode is PVP."""
        return self.mode == Mode.PVP

    def computer(self):
        """Returns whether the mode is computer vs. computer."""
        return self.mode == Mode.COMPUTER

    def bench(self):
        """Returns whether the mode is bench-test."""
        return self.mode == Mode.BENCH

    def debug(self):
        """Returns whether the mode is debug."""
        return self.debugMode

    def __str__(self):
        return 'Mode is ' + self.mode + ': ' + self.MODES[self.mode] + \
            ' Debug: ' + str(self.debug())

