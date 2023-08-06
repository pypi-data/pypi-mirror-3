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
from location import *
from reversiToken import *



class Strategy(object):
    """This is an abstract class that defines an interface for AI strategies to
    implement in subclasses."""

    def findBestMove(self, token, board, validMoves):
        """Find the best move for the current board, given the current player's
        token, the board, and a list of valid moves.
        Returns EITHER a couplet containing the best move, and the list of
        locations of the opponent's tokens that it will flip,
                OR False if no move is found."""
        return False


    def reset(self):
        """Reset any internal counters before starting a new game."""
        pass



class MaximizeScore(Strategy):
    """This is the fallback strategy if all other strategies fail to find a
    move. It should always be the last strategy implemented. """

    def findBestMove(self, token, board, validMoves):
        """Searches the list of valid moves for one that maximises the score for
        the player's next move.
        Returns a couplet containing the best move, and the list of associated
        flippable opponent's tokens.
        NB Unlike other strategy findBestMove() methods, this method ALWAYS
        returns a move, unless the list of valid moves is incorrectly configured
        or empty."""
        scoreHWM = 0
        for trialMove in validMoves:
            tokensToFlip = board.isValidMove(token, trialMove)

            # do the move on a cloned board and work out the score
            trialBoard = board.clone()
            trialBoard.makeMove(token, (trialMove, tokensToFlip))
            score = trialBoard.getScores()[str(token)]

            # keep the move if the score is a new high and reset the HWM
            if score > scoreHWM:
                scoreHWM = score
                bestMove = trialMove
                bestFlips = tokensToFlip

        return bestMove, bestFlips



class FindACorner(Strategy):
    """This strategy relies on the fact that the corners of the board can never
    be flipped. This makes the corners special."""


    def findBestMove(self, token, board, validMoves):
        """Finds a corner move and chooses it.
        Returns the corner move and the list of opponent's tokens it will flip,
                or False if no corner move is found."""
        for trialMove in validMoves:
            if trialMove.isCorner():
                return trialMove, board.isValidMove(token, trialMove)
        return False



class FindUnflippable(FindACorner):
    """This is a development of the 'find a corner' strategy. Finding a corner
    works because the token cannot be flipped. This strategy looks for corners
    and other positions where the player's token cannot be flipped.
    To simplify the calculation this strategy maintains a list of existing known
    stable locations for the player this strategy belongs to."""


    def __init__(self):
        """Initialize an internal list of locations for existing stable tokens."""
        self.stableTokenLocations = []


    def reset(self):
        """Reset the record of stable tokens at the start of each game."""
        self.__init__()


    def findBestMove(self, token, board, validMoves):
        """This strategy does the following and returns the first move it finds:
        1) Look for a corner move (using parent method).
        2) Look for any move next to at least 4 other unflippable tokens or
        positions off the board.
        (This uses and maintains an internal record of known stable tokens).
        Returns the move and the list of flippable opponent's tokens,
                or False if no move is found."""
#        if mode.debug(): self._dbgShowList('Starting')

        # 1) find a corner
        cornerFlips = FindACorner.findBestMove(self, token, board, validMoves)
        if cornerFlips:
            self.stableTokenLocations.append(cornerFlips[0])
#            if mode.debug(): print('Stable corner found: ', cornerFlips[0])

            # see what other tokens this move makes stable on a trial board
            testBoard = board.clone()
            testBoard.makeMove(token, cornerFlips)
            self._checkNeighbours(token, testBoard, cornerFlips[0])
#            if mode.debug(): self._dbgShowList('Corner')
            return cornerFlips

        # 2) find the first unflippable move in the list
        for move in validMoves:
            flips = board.isValidMove(token, move)

            # see what tokens this move makes stable on a trial board
            testBoard = board.clone()
            testBoard.makeMove(token, (move, flips))
            if self._isStablePosition(token, testBoard, move):
                self._checkNeighbours(token, testBoard, move)
#                if mode.debug(): self._dbgShowList('Unflippable')
                return move, flips

        # fallback if no move is found
        return False


    def _dbgShowList(self, title):
        """DBG: Debug print output of the current list of stable tokens."""
        print(title + ' list of stables: \n' + \
              '[' + ', '.join(str(x) for x in self.stableTokenLocations) + ']')


    def _checkNeighbours(self, token, board, stable):
        """When a location has been verified stable and accepted as a good move,
        some neighbouring tokens may become stable. We re-run the stability
        check, but this time on same-token neighbours.
        For each neighbour we find is stable, we recursively check their
        neighbours, too."""
        # check the neighbours
#        if mode.debug(): print('Checking neighbours of ', stable)
        for direction in DIRECTIONS:
            neighbour = stable + direction

            # we ignore positions not on the board
            if not neighbour.isOnTheBoard():
#                if mode.debug():
#                    print('Neighbour of ', stable, ' is not on the board: ', \
#                          neighbour)
                continue

            # if the position is empty it is irrelevant
            elif board.isPositionFree(neighbour):
#                if mode.debug():
#                    print('Neighbour of ', stable, ' is empty: ', neighbour)
                continue

            # we may already have recorded it
            elif neighbour in self.stableTokenLocations:
#                if mode.debug():
#                    print('Neighbour of ', stable, ' already noted: ', \
#                          neighbour)
                continue

            # if it is a same token make sure it is stable...
            elif board.grid[neighbour[0]][neighbour[1]] == token:
                if self._isStablePosition(token, board, neighbour):
#                    if mode.debug():
#                        print('Neighbour of ', stable, \
#                              ' now identified stable: ', neighbour)
                    self._checkNeighbours(token, board, neighbour)
#                elif mode.debug():
#                    print('Neighbour of ', stable, ' NOT stable: ', neighbour)
#            elif mode.debug():
#                print('Neighbour of ', stable, ' is the opponents!: ', \
#                      neighbour)


    def _isStablePosition(self, token, board, location):
        """Check if the given location with the given token is stable.
        We define 'stable' as having a board edge or an existing stable token
        in at least 4 directions, or filled board locations in all 8 directions
        to the board edge.
        Returns True if the token can not be flipped in that location."""
        # check the 8 neighbours of the location - are they stable?
        stableDirs = []

        # only need do this if our list of known stables is non-empty
        if len(self.stableTokenLocations) != 0:
            for direction in DIRECTIONS:
                nbor = location + direction

                # is the neighbour off the board?
                if not nbor.isOnTheBoard(): stableDirs.append(direction)

                # is the neighbour vacant?
                elif board.isPositionFree(nbor): continue

                # is the neighbour one of ours?
                elif board.grid[nbor[0]][nbor[1]] != token: continue

                # is the neighbour already in our list of stable tokens?
                elif nbor in self.stableTokenLocations:
                    stableDirs.append(direction)

                # is the neighbour a to-be-identified stable?
                else:
                    # see if we find a stable anchor in this direction
                    nbor += direction
                    while nbor.isOnTheBoard() and \
                    board.grid[nbor[0]][nbor[1]] == token:
                        if nbor in self.stableTokenLocations:
                            stableDirs.append(direction)
                            break
                        else:
                            nbor += direction

        # we need to check contiguity of directions for n=4
        contiguousNeighbours = True
        if len(stableDirs) == 4:
            sumSepSq = 0.0                      # sum of squares of separations
            dirsToCheck = stableDirs[:]
            for dir1 in stableDirs:
                dirsToCheck.remove(dir1)
                for dir2 in dirsToCheck:
                    separation = dir2 - dir1
                    sumSepSq += separation.dot(separation) # numpy dot product

            # if sumSepSq is > 14 the directions are not contiguous on the board
            contiguousNeighbours = sumSepSq <= 14
#            if mode.debug():
#                print('Contiguity is ' + str(contiguousNeighbours) + \
#                      ' for ' + str(location))

        if contiguousNeighbours and len(stableDirs) >= 4:
#            if mode.debug(): print('Stable location found: ', location)

            # update the list of stables
            self.stableTokenLocations.append(location)
            return True

        # secondary check to see if all 8 directions are full
        else: # i.e. the last check failed
            for direction in DIRECTIONS:
                nbor = location + direction
                if not nbor.isOnTheBoard(): continue
                while not board.grid[nbor[0]][nbor[1]].isEmpty():
                    nbor += direction
                    if not nbor.isOnTheBoard(): break
                return False

        # we have failed to find a False condition so it must be stable
#        if mode.debug():
#            print('Secondary check found stable location: ', location)
        self.stableTokenLocations.append(location) # update the list
        return True

