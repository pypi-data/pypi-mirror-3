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


import numpy
from reversiConstants import *



class Location(numpy.ndarray):
    """This is a subclass of numpy.ndarray that replaces the need for lists to
    represent [x, y] grid coordinates.
    It includes some handy utility methods for location manipulations. """


    def __new__(cls, location):
        """Boilerplate instantiator for ndarray subclasses."""
        obj = numpy.array(location).view(cls)
        return obj


    def __array_finalize__(self, obj):
        """Boilerplate instance finalizer for ndarray subclasses."""
        if obj is None: return


    def isOnTheBoard(self):
        """Check if the location is on the board."""
        valid = True
        for i in range(2):
            valid = valid and self[i] >= 0 and self[i] < MAX_GRID
        return valid


    def isCorner(self):
        """Check if the location is in a corner of the board. These locations
        are special because they can never be flipped."""
        return self in CORNERS


    def __eq__(self, other):
        """Override parent to avoid ambiguity in equality tests."""
        isEqual = numpy.equal(self, other)
        allEqual = True
        for eq in isEqual: allEqual = allEqual and eq
        return allEqual


    def __str__(self):
        loc = self.tolist()
        return '(' + str(loc[0]+1) + ', ' + str(loc[1]+1) + ')'



# grid direction vectors (8 points of the compass)
DIRECTIONS = []
for x in range(-1, 2):
    for y in range(-1, 2):
        # we skip the centre
        if not (x == y == 0): DIRECTIONS.append(Location([x, y]))

# grid corners
TOP_LEFT = Location([0, 0])
BOTTOM_LEFT = Location([0, MAX_GRID-1])
TOP_RIGHT = Location([MAX_GRID-1, 0])
BOTTOM_RIGHT = Location([MAX_GRID-1, MAX_GRID-1])
CORNERS = [TOP_LEFT, BOTTOM_LEFT, TOP_RIGHT, BOTTOM_RIGHT]

