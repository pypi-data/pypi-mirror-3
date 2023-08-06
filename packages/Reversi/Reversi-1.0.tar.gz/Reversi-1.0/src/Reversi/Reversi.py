#!/usr/bin/env python3
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


"""
An implementation of the popular Reversi board game, for use by one or two
players. Some simple AI is included to provide a computer opponent, and if you
are feeling lazy you can watch while two AI opponents slug it out.

The controls for the game are minimal, and hopefully self-explanatory, but here
is a list:

Preparation:
============
Language:   A selection box appears to enable the player to choose their preferred
            language. At time of writing the only options supported are English
            and Chinese, but if there is someone 'out there' interested in
            helping with other translations I will be happy to hear from them.
            If no language is selected the game will default to English.
Your name:  You can type anything you like here, it just helps to distinguish
            the players.
Mode:       Four modes are supported:
    n       Normal (human versus computer opponent).
    p       Person versus Person, in 'hot-seat' mode.
    c       Computer versus computer, what I like to call TV mode.
    b       Benchmarking mode, all graphics turned off. In this mode additional
            information is requested for the number of games to play.
            The default mode is 'Normal'.
Token:      The game asks the first player to choose a token, Black or White.

Game Play:
==========
Who starts is chosen at random.
Hints:      A hint mode is provided for each (human) player that can be toggled
            by either typing 'h' or clicking the appropriate button, depending
            on the UI you are using.
Quit:       Typing 'q', hitting 'Esc' and/or clicking the 'Close Window' icon
            (the details depend on the UI) causes the current game to be
            aborted.
Play Again: You can elect to play again as many times as you want. The more
            games you play, your game statistics will be accumulated and
            displayed on the scoreboard. However, at the time of writing, there
            is no mechanism for storing game stats between sessions.

Bob Bowles <bobjohnbowles@gmail.com>
"""


# initialize the language from a rudimentary UI BEFORE we do any imports
import gettext
import chooseLanguageWindow


from utils import *
from mode import *
from game import *
from player import *
from reversiToken import *
from reversiConstants import *
import ui



# main program and loop


ui.startUI(_('Reversi'), _('Welcome to Reversi!'))

# choose the game mode, set up mode variables
mode = Mode()
mode.debugMode = False   # set the debug flag
totalGames = None
if mode.bench():
    while not totalGames:
        number = ui.getNumberOfGames(_('Enter how many iterations: '))
        try: totalGames = int(number)
        except: continue

# set up the players - dummy 'ghost' player for draws
players = choosePlayers(mode)
draw = Player(DRAW_TK.name(), {NDR:DRAW_TK}, mode)
players.append(draw)

# accumulators for the final totals
gamesPlayed = 0
wins = {NBK: 0, NWH: 0, NDR: 0}
total = {NBK: 0, NWH: 0, NDR: False}

score = {NBK:0, NWH:0}
ui.setupScoreboard(players, score, gamesPlayed, total, wins)

while True:
    # reset the game
    game = Game(players, mode)
    score = game.play()

    # accumulate the totals
    gamesPlayed += 1
    for k in score.keys(): total[k] += score[k]

    # who won?
    if score[NBK] > score[NWH]: wins[NBK] += 1
    elif score[NWH] > score[NBK]: wins[NWH] += 1
    else: wins[NDR] += 1

    # display the scores
    if not mode.bench():
        ui.updateGameResults(players, score, gamesPlayed, total, wins)

    # loop exit
    if mode.bench():
        if gamesPlayed == totalGames: break
    elif not ui.getPlayAgain(_('Play again? (yes or no)')):
            break
    else:
        # reset the scores for the new game
        ui.updateGameScores({NBK:0, NWH:0})

# calculate and display the final results
ui.updateGameResults(players, score, gamesPlayed, total, wins)


ui.stopUI(_('Thank you for playing!'))


