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


from strategy import *
from player import *
from reversiToken import *
from mode import *



# Utility functions for the main loop

def giveName():
    """Get the player's name."""
    return ui.getPlayersName(_('Your name:'))


def choosePlayers(mode):
    """Set up the players depending on the mode of play.
    Returns a list containing the two players."""
    # Computer strategy options
    VANILLA_STRATEGY = [FindACorner(), MaximizeScore()]
    CLEVER_STRATEGY = [FindUnflippable(), MaximizeScore()]


    # allow the first player to choose their token (if it is human)
    choices = playerTokens.copy()

    # set up player 1
    if mode.normal() or mode.pvp(): # player 1 is human
        player1 = Human(giveName(), choices, mode)
    else:       # the other modes use a vanilla computer for player 1
        player1 = Computer(_('Mr Niceguy'), {NBK:BLACK_TK}, mode)
        player1.strategies = VANILLA_STRATEGY

    # set up player 2
    if mode.pvp():    # player 2 is human only for pvp mode
        player2 = Human(giveName(), choices, mode)
    elif mode.normal():   # token choice is different for the computers
        player2 = Computer(_('Mr Cleverclogs'), choices, mode)
        player2.strategies = CLEVER_STRATEGY # 'clever'
    else:
        player2 = Computer(_('Mr Cleverclogs'), {NWH:WHITE_TK}, mode)
        player2.strategies = CLEVER_STRATEGY # 'clever'

    return [player1, player2]

