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


"""the idea of this module is to act as an abstraction layer between the game
and the ui implementation(s)"""

# the ui implementations. Only 1 should be used at a time
#import ui_console as ui_impl
##import ui_pygame as ui_impl # not any more!
import ui_tkinter as ui_impl


def startUI(title, welcomeMessage):
    """Initialize the UI and display a welcome message."""
    ui_impl.startUI(title, welcomeMessage)


def getMode(prompt, modes):
    """The player chooses what mode to play in.
    Returns the mode selected."""
    return ui_impl.getMode(prompt, modes)


def getNumberOfGames(prompt):
    """Obtain the number of games required for a bench test.
    Returns the number."""
    return ui_impl.getNumberOfGames(prompt)


def getPlayersName(prompt):
    """Obtain the player's name.
    Returns what the player types in."""
    return ui_impl.getPlayersName(prompt)


def chooseToken(prompt):
    """The player chooses which token they want to use in the game.
    Returns a key identifying the token (token.tk)."""
    return ui_impl.chooseToken(prompt)


def setupScoreboard(players, score, gamesPlayed, total, wins):
    """Initialise the scoreboard on the UI."""
    ui_impl.setupScoreboard(players, score, gamesPlayed, total, wins)


def displayMessage(message):
    """Give a message to the player."""
    ui_impl.displayMessage(message)


def flagPlayersTurn(player):
    """Indicate to the player whose turn it is."""
    ui_impl.flagPlayersTurn(player)


def displayBoard(board):
    """Display the current state of play on the UI."""
    ui_impl.displayBoard(board)


def chooseMove(name):
    """Player selects a move.
    Returns the selected move, or may raise a GameControl throwable to deal
    with the player deciding to quit or requesting hints."""
    return ui_impl.chooseMove(name)


def playerPause():
    """Wait for the player to do something."""
    ui_impl.playerPause()


def updateGameScores(score):
    """After each move re-calculate and re-display the scores."""
    ui_impl.updateGameScores(score)


def updateGameResults(players, score, gamesPlayed, total, wins):
    """At the end of each game update the players' game statistics."""
    ui_impl.updateGameResults(players, score, gamesPlayed, total, wins)


def getPlayAgain(prompt):
    """Ask the player if they want to play again.
    Return True if they want to play again."""
    return ui_impl.getPlayAgain(prompt)



def stopUI(finishMessage):
    """Display a message and do any final housekeeping on the UI before shutting
    down."""
    ui_impl.stopUI(finishMessage)

