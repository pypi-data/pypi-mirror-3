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
from zope.interface import implements
from interfaces import ICoordinate, IDistanceCalculation, INearbyZips, ICoordinateProvider, IZipDatabase
from zope.component import getUtility
import math

class Distance(object):
    implements(IDistanceCalculation)

    def __init__(self, earth_radius):
        self.earth_radius = earth_radius

    def distance(self, c1, c2):
        c1 = ICoordinate(c1)
        c2 = ICoordinate(c2)
        asd = (
                (math.sin(math.radians(c1.latitude)) * math.sin(math.radians(c2.latitude))) +
                (math.cos(math.radians(c1.latitude)) * math.cos(math.radians(c2.latitude)) * math.cos(math.radians(c1.longitude) - math.radians(c2.longitude)))
                )
        if asd > 1.0:
            asd = 1.0 # distance 0. Can be a slight bit > 1 due to float type errors.
        dst = math.acos(asd) * self.earth_radius

        return dst

    def nearest(self, coordinate, coordinate_list, limit=None):
        distances = []
        for c in coordinate_list:
            distances.append( (self.distance(coordinate, c), c))
        distances.sort()
        if limit:
            return distances[:limit]
        return distances
   
    def toRadiant(self, distance):
        return distance / (self.earth_radius * 2 * math.pi) * 360 


class NearbyZips(object):
    """ This implementation searches for nearby zips in a inexact, but
        _very fast_ way. It simply defines a square and looks for matches inside.
        Attention: This does not work near radiant bounderies (around 180° latitude),
        because we don't jump ;)
    """
    implements(INearbyZips)
    
    def nearbyZips(self, start, distance):
        distance = float(distance)
        start = ICoordinate(start)
        longitude_min = start.longitude - distance / 2
        latitude_min = start.latitude - distance / 2
        longitude_max = start.longitude + distance / 2
        latitude_max = start.latitude + distance / 2
        
        matched_zips = []
        
        """
        coordinate_provider = getUtility(ICoordinateProvider)
        for country, zip, latitude, longitude in coordinate_provider:
            if latitude > latitude_min and latitude < latitude_max and longitude > longitude_min and longitude < longitude_max:
                matched_zips.append((country, zip))
        """

        zip_database = getUtility(IZipDatabase)
        latitude_matches = set(zip_database.latitudes.values(latitude_min, latitude_max))
        longitude_matches = set(zip_database.longitudes.values(longitude_min, longitude_max))
        return latitude_matches & longitude_matches
         
        
        
        return matched_zips
    

km_distance = Distance(earth_radius=6371.0)
miles_distance = Distance(earth_radius=3959.0)


