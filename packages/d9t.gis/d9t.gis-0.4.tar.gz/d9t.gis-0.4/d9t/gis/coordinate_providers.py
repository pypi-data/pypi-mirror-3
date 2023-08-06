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
from zope.component import getUtility
from interfaces import ICoordinateProvider, IZipDatabase
from coordinate import Coordinate
import csv
import os
import logging
import math
from BTrees.OOBTree import OOBTree

class CsvZipDatabase(object):
    """ a coordinate / zip database which loads data from a csv file
    """
    implements(IZipDatabase)
    
    data = OOBTree()
    latitudes = OOBTree()
    longitudes = OOBTree()

    log = logging.getLogger("ZipGis")


    def __init__(self, gisfile):
        """ Recieves a gis csv filename and loads data
        """
        self.log.info("Importing GIS Data...")
        reader = csv.reader(open(gisfile, "rb"), delimiter=";", quoting=csv.QUOTE_NONE)
        for row in reader:
            country = row[0]
            zip = row[1]
            latitude = row[2]
            longitude = row[3]
            self.data[(country, zip)] = Coordinate(latitude, longitude)
            self.latitudes[float(latitude)] = (country, zip)
            self.longitudes[float(longitude)] = (country, zip)
        self.log.info("Finished importing GIS Data...")

HERE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(HERE_DIR, "data")

zip_database = CsvZipDatabase(gisfile=DATA_DIR+"/DE.csv")



class ZipCoordinateProvider(object):
    implements(ICoordinateProvider)
    
    iter_index = 0
    
    def coordinate(self, country, zip):
        zip_database = getUtility(IZipDatabase)
        return zip_database.data.get((country, zip))
    


