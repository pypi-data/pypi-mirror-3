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


"""Command-line console implementation of the game UI."""

from gameControl import *
from location import *
from reversiToken import *


def startUI(title, welcomeMessage):
    """Initialize the UI (not needed). Display a welcome message."""
    print(title)
    print()
    print(welcomeMessage)
    print()


def getMode(prompt, modes):
    """The player chooses what mode to play in.
    Returns the mode selected."""
    print(prompt)
    return input('          ' + \
                 '\n          '.join((str('%s: %s' % (k, modes[k])) \
                                      for k in modes.keys())))


def getNumberOfGames(prompt):
    """Obtain the number of required games for a bench test."""
    # TODO: really need a sanity check that the user really has entered a number.
    return int(input(prompt))


def getPlayersName(prompt):
    """Obtain the player's name.
    Returns what the player types in."""
    return input(prompt)


def chooseToken(prompt):
    """The player makes a selection based on the prompt.
    Returns a string. The first letter identifies the choice."""
    return input(prompt)


def setupScoreboard(players, score, gamesPlayed, total, wins):
    """Initialise the scoreboard on the UI. Not required for console."""
    pass


def displayMessage(message):
    """Print a message for the player."""
    print(message)


def flagPlayersTurn(player):
    """Tell the player(s) whose turn it is."""
    print(player.name + _(', your turn!'))


def displayBoard(board):
    """Get the board to print its string representation."""
    print(board)


def chooseMove(player):
    """Interaction between the game and the (human) player. The player is
    required to select their next move. Alternatively they can abort the game,
    or toggle hints.
    Returns the selected location or raises a GameControl throwable to deal with
    hints or quit."""

    move = []
    while not move:
        moveInput = \
        input(_('%s, What is your next move? (x y) x,y = 1-8 quit or hint ')
                 % (player.name)).lower()

        # user hits <return> without typing anything
        if not moveInput: continue

        # user bail-outs are thrown as GameControl instructions.
        if not moveInput[0].isdigit():
            if moveInput.startswith('q'):
                raise GameControl(GameControl.QUIT)
            if moveInput.startswith('h'):
                raise GameControl(GameControl.HINT)
            print(_('Sorry, I do not understand "') + moveInput + _('"'))
            continue

        # make sure player has typed something sensible
        try:
            for i in moveInput.split(): move.append(int(i)-1)
            if len(move) != 2:
                print(_('Please type two numbers'))
                continue
            return Location(move)
        except TypeError:
            print(_('Move must have numeric coordinates'))
            continue


def playerPause():
    """Wait for the player to hit the <enter> key."""
    input(_('Press <enter> when ready'))


def updateGameScores(score):
    """After each move re-calculate and re-display the scores."""
    print(_('Scores:  ') + _(' vs. ').join(str('%s: %2r'
          % ((k, score[k]))) for k in score.keys()))


def updateGameResults(players, score, gamesPlayed, total, wins):
    """At the end of each game update the players' game statistics."""
    print(_('Results for %3r games:') % gamesPlayed)
    print(_('Averages:                       Scores:       Wins:'))
    for player in players:
        k = str(player.token)
        if total[k]: average = str('%2.2d' % (total[k]/gamesPlayed))
        else: average = '    '
        print('               %15s %4s: %4s        %2r (%2.1d%%)' % \
              (player.name, k, average, wins[k], (wins[k]/gamesPlayed*100.0)))


def getPlayAgain(prompt):
    """Ask the player if they want to play again.
    Return True if they want to play again."""
    return input(prompt).startswith('y')


def stopUI(finishMessage):
    """Just say goodbye."""
    print(finishMessage)

