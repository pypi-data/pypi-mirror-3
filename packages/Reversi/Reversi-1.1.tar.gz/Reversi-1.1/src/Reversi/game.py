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


from board import *
from gameControl import *
import random, ui



class Game(object):
    """Encapsulates a game. A game has two players (one human, one computer),
    and a board. The players take turns to make a move.
    The game continues until one of the players wins, or a draw is declared."""


    def __init__(self, players, mode):
        """Initialise the game, and decide who goes first."""

        # initialize the players
        self.players = players
        for player in self.players: player.beginGame()

        # set up the playing mode
        self.mode = mode

        # set up the board
        self.board = Board()

        #set up the board display
        if not self.mode.bench(): ui.displayBoard(self.board)

        # randomly assign who goes first (turn toggles during the game)
        self.turn = random.randint(0,1)


    def play(self):
        """The main loop of the game. Alternate turns between the 2 players
        until a termination condition arises."""
        passed = False    # flag for passes, set if the last move was passed
        while True:

            # decide which player's turn it is
            currentPlayer = self.players[self.turn]

            # flag the player to do something
            if not self.mode.bench(): ui.flagPlayersTurn(currentPlayer)

            try:

                # check there are valid moves remaining
                if not self.board.findAllValidMoves(currentPlayer.token):
                    pass # in this case we catch a GameControl exception anyway
                passed = False

                move = currentPlayer.selectMove(self.board)
            except GameControl as gameControl:
                # if the player requests hints, toggle hints, re-start the move
                if gameControl.instruction == GameControl.HINT:
                    currentPlayer.hints = not currentPlayer.hints
                    flag = _('OFF')
                    if currentPlayer.hints: flag = _('ON')
                    ui.displayMessage(str(_('Hints are %s for %s.') % \
                                          (flag, currentPlayer.name)))
                    continue

                # the player has requested to quit
                if gameControl.instruction == GameControl.QUIT:
                    ui.displayMessage(str(_('%s has quit.') % \
                                          (currentPlayer.name)))
                    break # this is an end-game option!

                # the player has no valid moves
                if gameControl.instruction == GameControl.PASS:
                    if not self.mode.bench():
                        ui.displayMessage(str(_('%s cannot move.') % \
                                              (currentPlayer.name)))
                    if passed: break # the game is over
                    else: passed = True

            if not passed: self.board.makeMove(currentPlayer.token, move)
            self.turn = (self.turn + 1) % 2 # alternate the players

        # print out the final board configuration and scores before exit
        if not self.mode.bench():
            ui.displayBoard(self.board)
            ui.updateGameScores(self.board.getScores())
            ui.displayMessage(_('Game over!'))

        return self.board.getScores()


