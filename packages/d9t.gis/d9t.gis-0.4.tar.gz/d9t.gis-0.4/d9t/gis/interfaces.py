# -*- coding: utf-8 -*-
"""
    Author:     D9T
                Daniel Kraft <dk@d9t.de>
                http://d9t.de/
    Date:       2008/04/08
    License:    GPLv3
                This program is free software: you can redistribute it and/or modify
                it under the terms of the GNU General Public License as published by
                the Free Software Foundation, either version 3 of the License, or
                (at your option) any later version.

                This program is distributed in the hope that it will be useful,
                but WITHOUT ANY WARRANTY; without even the implied warranty of
                MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
                GNU General Public License for more details.

                You should have received a copy of the GNU General Public License
                along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from zope.interface import Interface, Attribute

class ICoordinate(Interface):
    """ provides a coordinate
    """
    latitude = Attribute("""latitude in degrees""")
    longitude = Attribute("""longitude in degrees""")

class IDistanceCalculation(Interface):
    """ Implementing utilities provide ways to measure distance
        between two coordinates on a globe.
    """

    def distance(c1, c2):
        """ returns the distance between the two coordinates c1 and c2,
            which are of type ICoordinate.
        """

    def nearest(coordinate, coordinate_list, limit):
        """ returns a list of nearest coordinates from coordinate_list to coordinate
            including distance.
        """
        
    def toRadiant(distance):
        """ converts a given distance in miles or km or whatever to a radiant.
        """

class ICoordinateProvider(Interface):
    """ This is a utility to get ICoordinate from a country and zip code
    """

    def coordinate(country, zip):
        """ Returns ICoordinates
        """

class INearbyZips(Interface):
    """ This looks for nearby zips within a given range.
    """
    
    def nearbyZips(coordinate, distance):
        """ coordinate is a ICoordinate. distance is radiants (float)
        """
                
class IZipDatabase(Interface):
    """ a zip database with filled attributes:
        - data
        - longitudes
        - latitudes
    """
    data = Attribute("""a dict with keys like "country-zip" and values of Coordinate""")
    latitudes = Attribute("""a OOBTree of latitudes with values like (country, zip)""")
    longitudes = Attribute("""a OOBTree of longitudes with values like (country, zip)""")
