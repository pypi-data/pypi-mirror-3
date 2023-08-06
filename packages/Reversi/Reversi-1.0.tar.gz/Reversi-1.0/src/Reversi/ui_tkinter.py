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


"""Tkinter implementation of the game GUI."""
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

from gameControl import *
from location import *
from reversiToken import *
from reversiConstants import *
from board import *
from player import *

from gameWindow import *
from chooseModeWindow import *
from chooseNumberWindow import *
from chooseTextWindow import *
from chooseTokenWindow import *
import styles



#==============================================================================
# UI Callbacks


# callback for the main window so we can kill it cleanly.
quit = False
def quitGame():
    """Exit the current game."""
    global quit
    quit = True


# TODO: this is a kludge to keep track of hints (really need access to players)
hintHistory = {NBK: False, NWH: False}


#==============================================================================
# UI INTERFACE IMPLEMENTATION


def startUI(title, welcomeMessage):
    """Initialize the UI. Display a welcome message."""
    global rootWindow, gameWindow

    # start the main window and set up window-killing callback
    rootWindow = Tk()
    rootWindow.resizable(True, True)
    rootWindow.protocol('WM_DELETE_WINDOW', quitGame)

    # implement styles
    styles.defineStyles(rootWindow)

    # put up a title
    rootWindow.title(title)

    # the main game window with the board and score panel
    gameWindow = GameWindow(rootWindow)
    rootWindow.update()

    # simple welcome message
    messagebox.showinfo(message=welcomeMessage)


def getMode(prompt, modes):
    """The player chooses what mode to play in.
    Returns the mode selected."""
    chooseModeWindow = ChooseMode(rootWindow, prompt, modes)

    mode = None
    while not chooseModeWindow.chosen.get():
        mode = chooseModeWindow.radioVar.get()
        chooseModeWindow.update()
    return mode


def getNumberOfGames(prompt):
    """Obtain the number of required games for a bench test."""
    chooseNumberWindow = ChooseNumber(rootWindow, prompt)
    numberOfGames = 0
    while not chooseNumberWindow.chosen.get():
        numberOfGames = chooseNumberWindow.numberVar.get()
        chooseNumberWindow.update()
    return numberOfGames


def getPlayersName(prompt):
    """Obtain the player's name.
    Returns what the player types in."""
    chooseTextWindow = ChooseText(rootWindow, prompt)
    name = ''
    while not chooseTextWindow.chosen.get():
        name = chooseTextWindow.textVar.get()
        chooseTextWindow.update()
    return name


def chooseToken(prompt):
    """The player makes a selection based on the prompt.
    Returns a string. The first letter identifies the choice."""
    chooseTokenWindow = ChooseToken(rootWindow, prompt)
    tokenID = ''
    while not tokenID:
        tokenID = chooseTokenWindow.tokenVar.get()
        chooseTokenWindow.update()
    return tokenID


def findPlayer(players, key):
    """Identify a player from their playing token.
    Returns the player with the matching token key."""
    for player in players:
        if player.token.tk == key: return player


def setupScoreboard(players, score, gamesPlayed, total, wins):
    """Initialise the scoreboard on the UI. Note all parameters are dictionaries
    indexed on token parameter."""
    for k in score.keys():
        scoreboard = gameWindow.scoreboard[k]

        # set up the players' names
        player = findPlayer(players, k)
        scoreboard.nameVal.set(player.name)

        # initialise the scores
        scoreboard.scoreVal.set(score[k])

        # set up wins
        scoreboard.winsVal.set(wins[k])

        # set up percentages
        percent = 0
        if gamesPlayed: percent = wins[k] * 100 // gamesPlayed
        scoreboard.percentVal.set(percent)

        # set up averages
        average = 0
        if gamesPlayed: average = total[k] // gamesPlayed
        scoreboard.averageVal.set(average)

        # remove the hints button for non-human players
        if isinstance(player, Computer): scoreboard.hintsButton.forget()

    gameWindow.update()


def displayMessage(message):
    """Print a message for the player."""
    gameWindow.update()
    messagebox.showinfo(message=message)
    gameWindow.update()


def flagPlayersTurn(player):
    """Tell the player(s) whose turn it is by changing the background of the
    icons on the scoreboard. Make sure the correct hint button is enabled."""
    gameWindow.update()
    turn = player.token.tk
    for k in gameWindow.scoreboard.keys():

        # set the icon to show which player's move is next
        icon = gameWindow.scoreboard[k].icon
        if k == turn: icon.configure(style='Selected.Scoreboard.TButton')
        else: icon.configure(style='Normal.Scoreboard.TButton')

        # enable/disable the hints button for human players if applicable
        if k == turn and isinstance(player, Human):
            gameWindow.scoreboard[k].hintsButton.configure(state='normal')
        else:
            gameWindow.scoreboard[k].hintsButton.configure(state='disabled')

    gameWindow.update()


def displayBoard(board):
    """Map the current state of the board onto the GUI."""
    gameWindow.update()
    for x in range(MAX_GRID):
        for y in range(MAX_GRID):
            token = board.grid[x][y]
            guiButton = gameWindow.board.gridArray[x][y]
            guiButton.token.set(token.tk)
    gameWindow.update()


def chooseMove(name):
    """Interaction between the game and the (human) player. The player is
    required to select their next move. Alternatively they can abort the game,
    or toggle hints.
    Returns the selected location or raises a GameControl throwable to deal with
    hints or quit."""
    move = None


    while move == None:
        gameWindow.update()

        # check to see if the window quit button was clicked
        global quit
        if quit:
            quit = False
            raise GameControl(GameControl.QUIT)

        # check the scoreboard to see if a hints button state has changed
        for k in gameWindow.scoreboard.keys():
            if gameWindow.scoreboard[k].hints.get() != hintHistory[k]:
                hintHistory[k] = gameWindow.scoreboard[k].hints.get()
                raise GameControl(GameControl.HINT)

        # check the gui grid to see if anything has been clicked
        move = gameWindow.board.chosen

    # clear the grid selection latch
    gameWindow.board.chosen = None
    gameWindow.update()

    return move


def playerPause():
    """Wait for the player to clear the messagebox."""
    gameWindow.update()
    messagebox.showinfo(message=_('Click <OK> when ready...'))
    gameWindow.update()


def updateGameScores(score):
    """After each move re-calculate and re-display the scores."""
    for k in score.keys():
        gameWindow.scoreboard[k].scoreVal.set(score[k])

    gameWindow.update()


def updateGameResults(players, score, gamesPlayed, total, wins):
    """At the end of each game update the players' game statistics."""
    for k in score.keys():
        scoreboard = gameWindow.scoreboard[k]

        # update wins
        scoreboard.winsVal.set(wins[k])

        # update percentages
        percent = 0
        if gamesPlayed: percent = wins[k] * 100 // gamesPlayed
        scoreboard.percentVal.set(percent)

        # update averages
        average = 0
        if gamesPlayed: average = total[k] // gamesPlayed
        scoreboard.averageVal.set(average)

    gameWindow.update()


def getPlayAgain(prompt):
    """Ask the player if they want to play again.
    Return True if they want to play again."""
    if messagebox.askyesno(message=prompt): return True
    else: return False


def stopUI(finishMessage):
    """Say goodbye and shut down the UI cleanly."""
    messagebox.showinfo(message=finishMessage)
    gameWindow.update()
    gameWindow.destroy()


