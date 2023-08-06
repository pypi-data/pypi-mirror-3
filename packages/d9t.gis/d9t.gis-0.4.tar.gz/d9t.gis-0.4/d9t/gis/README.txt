-----------
Boilerplate
-----------

First, let's load the required zcml as this is a unit test.
  >>> from Products.Five.zcml import load_config, load_string
  >>> import d9t.gis
  >>> import Products.Five
  >>> import five.localsitemanager
  >>> load_config('configure.zcml', package=Products.Five)
  >>> load_config('configure.zcml', package=five.localsitemanager)
  >>> load_config('configure.zcml', package=d9t.gis)

-----
Usage
-----

Measurable Objects
==================

A measurable object has to provide ICoordinate, which also may be
provided by an adapter.

Let's define a generic address class (minimalistic and incomplete, i know).

  >>> from zope.interface import implements, Interface
  >>> from zope.component import queryUtility, adapts
  >>> from d9t.gis.interfaces import ICoordinate, ICoordinateProvider

  >>> class Address(object):
  ...     implements(ICoordinate)
  ...
  ...     def __init__(self, country, zip):
  ...         zip_coordinate_provider = queryUtility(ICoordinateProvider)
  ...         coordinate = zip_coordinate_provider.coordinate(country, zip)
  ...         self.latitude = coordinate.latitude
  ...         self.longitude = coordinate.longitude

Now let's generate a few addresses.

  >>> a1 = Address("DE", "89073")
  >>> a2 = Address("DE", "88299")

You can also create simple Coordinates. A demo Coordinate class is included:

  >>> from d9t.gis.coordinate import Coordinate
  >>> c1 = Coordinate(9.99968113200213, 48.4052825255534)   # DE 89073
  >>> c2 = Coordinate(10.0191253966503, 47.8117109627977)   # DE 88299

It should be noted that ZipCoordinateProvider loads the gis data from csv on zope startup.
This takes far less then a second and we decided that storing the data in
zodb wouldn't have any advantage.

Calculating Distance
====================

  >>> from d9t.gis.interfaces import IDistanceCalculation
  >>> distance_util = queryUtility(IDistanceCalculation)

You can measure distance between anything that provides ICoordinate. So:
Between Coordinates

  >>> distance_util.distance(c1, c2)
  65.033485081783098

Between Addresses

  >>> distance_util.distance(a1, a2)
  65.033485081783098

Between Coordinates and Addresses

  >>> distance_util.distance(a1, c2)
  65.033485081783098
  >>> distance_util.distance(a1, c1)
  0.0

Common usage
============

Probably you already have some address objects which are unaware of
gis information. Maybe you want - and this is indeed a good idea -
to prevent your address - objects to even know about gis information.

You can have all gis features by providing an ICoordinate Adapter for
your objects.

Imagine we have a already existing class which is unaware of any gis info:

  >>> class IMyAddress(Interface):
  ...     """ """

  >>> class MyAddress(object):
  ...     implements(IMyAddress)
  ...     address = ""
  ...     zip_code = ""
  ...     city = ""
  ...     country = ""
  ...     def __init__(self, address, zip_code, city, country):
  ...         self.address, self.zip_code, self.city, self.country = address, zip_code, city, country

You would then have objects of that type:

  >>> my_a1 = MyAddress("Ilextwiete 12", "22455", "Hamburg", "DE")
  >>> my_a2 = MyAddress("Gangweg 2", "80797", "Muenchen", "DE")

For measuring distance, your objects have to provide ICoordinate. So let's
create an adapter which simply uses a ready-to-use utility to get the coordinates.

  >>> class MyAddressCoordinate(object):
  ...     implements(ICoordinate)
  ...     adapts(IMyAddress)
  ...
  ...     def __init__(self, my_address):
  ...         self.my_address = my_address
  ...         zip_coordinate_provider = queryUtility(ICoordinateProvider)
  ...         coordinate = zip_coordinate_provider.coordinate(self.my_address.country, self.my_address.zip_code)
  ...         self.latitude = coordinate.latitude
  ...         self.longitude = coordinate.longitude

You would usually provide the adapter in your zcml, but as this is a testcase,
we'll do it here:

  >>> from zope.app.testing import ztapi
  >>> ztapi.provideAdapter(IMyAddress, ICoordinate, MyAddressCoordinate)

Then you can measure as usual:

  >>> distance_util.distance(my_a1, my_a2)
  624.79554959923701


Get nearby places
=================

If you want to know which of several addresses are the closest to a given one, just
give the utility a list of known ICoordinate and one to look for. You will get back
a list of tuples where [0] is the distance and [1] is the original object.
Btw: As you will see any adaptable object will be ok and returned as-is.

Let's measure what are the nearest 3 to Muenchen (my_a2) from this list:

  >>> nearest = distance_util.nearest(my_a2, (my_a1, my_a2, c1, c2, a1, a2))
  >>> ["%s (%s)" % (n[0], n[1].__class__) for n in nearest]
  ["0.0 (<class 'MyAddress'>)", "175.137634687 (<class 'Address'>)", "175.137634687 (<class 'd9t.gis.coordinate.Coordinate'>)", "175.24792832 (<class 'Address'>)", "175.24792832 (<class 'd9t.gis.coordinate.Coordinate'>)", "624.795549599 (<class 'MyAddress'>)"]

You can also limit the search to e.g. 3 results (sorted of course):

  >>> nearest = distance_util.nearest(my_a2, (my_a1, my_a2, c1, c2, a1, a2), 3)
  >>> ["%s (%s)" % (n[0], n[1].__class__) for n in nearest]
  ["0.0 (<class 'MyAddress'>)", "175.137634687 (<class 'Address'>)", "175.137634687 (<class 'd9t.gis.coordinate.Coordinate'>)"]


Get nearby ZIPs
===============

In case you need all zips within a given distance around a given coordinate, you might
find the INearbyZips utility useful.

  >>> from zope.component import getUtility
  >>> from d9t.gis.interfaces import INearbyZips, IDistanceCalculation
  >>> nbz = getUtility(INearbyZips)
  >>> distance_util = getUtility(IDistanceCalculation, name="km")
  >>> nbz.nearbyZips(c1, distance_util.toRadiant(10))
  set([('DE', '89077'), ('DE', '89231'), ('DE', '89075'), ('DE', '89073')])

This was for 10km. 
Attention! This only works away from radiant bounderies. Stay away from +-180 degrees!
This is due to speed optimizations. Sorry ;)


--------
Advanced
--------

Nearby places with portal_catalog
=================================

When using portal_catalog, you only get brains back which have no usable
interface to adapt to. Then, please don't getObject() anything. It's a
waste.

Instead, create a decorator for the brains like that:

  >>> class MyAddressBrainCoordinateDecorator(object):
  ...     implements(ICoordinate)
  ...     def __init__(self, brain):
  ...         self.brain = brain
  ...         zip_coordinate_provider = queryUtility(ICoordinationProvider)
  ...         coordinate = zip_coordinate_provider.coordinate(brain.getCountry, brain.getZip)
  ...         self.latitude = coordinate.latitude
  ...         self.longitude = coordinate.longitude

Then decorate your brains before using them for nearest search and get them back
after the search:

  >>> brains = []
  >>> decorated_brains = [MyAddressBrainCoordinateDecorator(brain) for brain in brains]
  >>> nearest = distance_util.nearest(my_a2, decorated_brains, 5)
  >>> brains = [decorated_brain.brain for decorated_brain in decorated_brains]

Too bad, that way the laziness of the portal_catalog search is gone. But with
a result set of less than 100 that shouldn't really matter. If your set is
big enough for performance impacts, any ideas are welcome.


Have fun ;)

