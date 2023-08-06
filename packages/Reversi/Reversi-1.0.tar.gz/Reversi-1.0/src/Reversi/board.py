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


from mode import *
from reversiToken import *
from location import *
from gameControl import *



class Board(object):
    """The board manages a record of the currently completed moves in the game
    on a grid."""


    def __init__(self):
        """
Construct a new copy of the grid with blanks in all the locations except the
starting positions. The starting map should look like this:
  1 2 3 4 5 6 7 8
 +-+-+-+-+-+-+-+-+
1| | | | | | | | |
 +-+-+-+-+-+-+-+-+
2| | | | | | | | |
 +-+-+-+-+-+-+-+-+
3| | | | | | | | |
 +-+-+-+-+-+-+-+-+
4| | | |B|W| | | |
 +-+-+-+-+-+-+-+-+
5| | | |W|B| | | |
 +-+-+-+-+-+-+-+-+
6| | | | | | | | |
 +-+-+-+-+-+-+-+-+
7| | | | | | | | |
 +-+-+-+-+-+-+-+-+
8| | | | | | | | |
 +-+-+-+-+-+-+-+-+

NB The grid indices go from 0 to 7 but the displayed locations go from 1 to 8."""

        # make the grid
        grid = self.makeGrid()

        # populate the grid with the starting positions
        grid[3][3] = BLACK_TK.clone()
        grid[3][4] = WHITE_TK.clone()
        grid[4][3] = WHITE_TK.clone()
        grid[4][4] = BLACK_TK.clone()

        self.grid = grid


    def makeGrid(self):
        """Return blank grid."""
        grid = []
        for x in range(MAX_GRID):
            grid.append([UNPLAYED_TK.clone()] * MAX_GRID)
        return grid


    def __str__(self):
        """Create a printable representation of the board. This implementation
        adds the location indices to make life easier for the human players."""

        # the header lines
        HLINE = ' +-+-+-+-+-+-+-+-+\n'
        HNUM =  '  1 2 3 4 5 6 7 8\n'

        # the display string
        display = '\n'
        display += HNUM
        display += HLINE
        for y in range(MAX_GRID):
            display += str(y+1) + '|'
            for x in range(MAX_GRID):
                display += printTk[self.grid[x][y].tk] + '|'
            display += '\n'
            display += HLINE
        return display


    def clone(self):
        """Make a deep copy of the board and return it.
        We make a new board and assign a clone of this one's grid to it."""
        copy = []
        for x in self.grid:
            copyX = []
            for y in x:
                copyX.append(y.clone()) # clone the tokens at each grid position
            copy.append(copyX)

        clone = Board()
        clone.grid = copy
        return clone


    def isPositionFree(self, move):
        """Determine if the selected move is available."""
        return self.grid[move[0]][move[1]].isEmpty()


    def isValidMove(self, token, move):
        """Check that the move location represents a valid move on the board.
        To satisfy this, the move must result in flipping (reversing) at least
        one of the opponent's tokens. To test this, we do the move as a trial
        and keep track of the flips that can be done.
        Returns the list of tokens to be flipped if true, otherwise False."""

        # shorthand
        g = self.grid
        tk = token                  # the current player's token
        ot = tk.clone()             # the other player's token (the other token)
        ot.flip()
        tokensToFlip = []

        # work out which directions have flippable opponent's tokens.
        for vector in DIRECTIONS:
            loc = move + vector

            # check if we have found an adjacent other token
            if loc.isOnTheBoard() and g[loc[0]][loc[1]] == ot:

                # keep going in the same direction...
                loc += vector

                # ...unless we go off the edge of the board...
                if not loc.isOnTheBoard(): continue

                # ...until we find one of our own tokens, or a blank
                while g[loc[0]][loc[1]] == ot:
                    loc += vector

                    # if we go over the edge break the while and continue the if
                    if not loc.isOnTheBoard(): break
                if not loc.isOnTheBoard(): continue

                # have we found one of our own tokens? We can flip some ot's!
                if g[loc[0]][loc[1]] == tk:
                    # record the locations of the flippable ot's for later
                    while True:
                        loc -= vector
                        if loc == move: break
                        tokensToFlip.append(loc.copy())

        # the move is not valid if there are no flippable ot's
        if len(tokensToFlip) == 0: return False

        return tokensToFlip


    def giveHints(self, token):
        """Request hints from the board for valid move options."""
        hints = self.clone()

        # find the valid options, mark them and provide them in the clone.
        hints.markValidMoves(self.findAllValidMoves(token))
        return hints


    def markValidMoves(self, validMoves):
        """Mark the listed moves on the board."""
        for move in validMoves:
            self.grid[move[0]][move[1]].mark()


    def findAllValidMoves(self,token):
        """Do an exhaustive search of the board for valid moves. Returns the
        list of valid options. If none are found we throw a GameControl exception
        to announce having lost."""
        validMoves = []
        for x in range(MAX_GRID):
            for y in range(MAX_GRID):
                move = Location([x, y])

                # we are only interested in the empty squares
                if not self.isPositionFree(move): continue

                # check if this move is valid, add to the list if so
                if not self.isValidMove(token, move): continue
                validMoves.append(move)

        # if there are no valid moves for this player they have lost the game
        if len(validMoves) == 0: raise GameControl(GameControl.PASS)

        return validMoves


    def makeMove(self, token, moveInstructions):
        """Make the move on the board with the specified token."""
        # unpack the move instructions
        move = moveInstructions[0]
        tokensToBeFlipped = moveInstructions[1]

        # put the new token on the board
        self.grid[move[0]][move[1]] = token.clone()

        # flip the affected tokens of the opponent's
        for otherToken in tokensToBeFlipped:
            self.grid[otherToken[0]][otherToken[1]].flip()


    def getScores(self):
        """Evaluate the current scores of both players by counting their tokens."""
        score = {NBK: 0, NWH: 0}
        for x in self.grid:
            for y in x:
                key = str(y)
                if key in score: score[key] += 1
        return score

