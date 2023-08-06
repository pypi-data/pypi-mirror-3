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



class GameControl(Exception):
    """This is a customised throwable object to pass control of the game from
    the players to the main game loop with some form of instruction on what to do
    next."""
    # Valid values for instruction:
    HINT = 'hint'
    QUIT = 'quit'
    PASS = 'pass'


    def __init__(self, instruction):
        """Add an attribute that can contain some information."""
        self.instruction = instruction
        Exception.__init__(self)

