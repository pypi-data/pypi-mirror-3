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


# constants for handling tokens
NBK = 'B'
NWH = 'W'
NH = 'H'
NU = 'U'
NDR = 'D'
tokenPlayNames = {NBK:_('Black'), NWH:_('White')} # for the players
tokenScoreNames = {NBK:_('Black'),
                   NWH:_('White'),
                   NDR:_('Drawn')} # for scoring
tokenNames = {NBK:_('Black'),
              NWH:_('White'),
              NH:_('Hint'),
              NU:_('Unplayed'),
              NDR:_('Drawn')}

# These constants are specific to console output
TB = '\u263b'
TW = '\u263a'
TH = '.'
TU = ' '
printTk = {NBK:TB, NWH:TW, NH:TH, NU:TU} # these are for console use



class Token(object):
    """Defines attributes of a player token."""


    def __init__(self, tk=NU):
        """Initialize the token's state. The default is 'unplayed'."""
        self.tk = tk


    def __str__(self):
        """Enable the token to print itself."""
        return self.tk


    def __eq__(self, other):
        """Token comparison."""
        return self.tk == other.tk


    def name(self):
        """Calculate the token's name from its state."""
        return tokenNames[self.tk]


    def play(self, token):
        """Player plays this token. The token may be another instance of Token,
        or just a letter."""
        if self.__class__ == token.__class__:
            self.tk = token.tk
        else: self.tk = token


    def flip(self):
        """Flip the token from one player to the other."""
        if self.tk == NBK: self.tk = NWH
        else: self.tk = NBK


    def mark(self):
        """Change the token to display itself as playable (hint mode)."""
        self.tk = NH


    def isEmpty(self):
        """Confirm if the token has not been played."""
        return self.tk == NU


    def clone(self):
        """Make a copy."""
        return Token(self.tk)


    def setTk(self, tk):
        """A setter to help disambiguate 'tk' when using tkinter."""
        self.tk = tk



# Constant token types for reference
BLACK_TK = Token(NBK)
WHITE_TK = Token(NWH)
DRAW_TK = Token(NDR)
UNPLAYED_TK = Token(NU)
HINT_TK = Token(NH)

playerTokens = {NBK:BLACK_TK, NWH:WHITE_TK}

