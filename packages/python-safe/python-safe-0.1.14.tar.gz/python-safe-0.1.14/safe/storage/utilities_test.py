"""Utilities to to support test suite
"""

import os
import types
import numpy

# Find parent parent directory to path
# Path to a directory called data at the same level of the parent module.
TESTDATA = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                        '..', 'test', 'data'))

# Known feature counts in test data
FEATURE_COUNTS = {'schools.shp': 144,
                  'tsunami_exposure.shp': 7529,
                  'buildings.shp': 3896,
                  'highway.shp': 2,
                  'buildings_poly.shp': 79}

# For testing
GEOTRANSFORMS = [(105.3000035, 0.008333, 0.0, -5.5667785, 0.0, -0.008333),
                 (105.29857, 0.0112, 0.0, -5.565233000000001, 0.0, -0.0112),
                 (96.956, 0.03074106, 0.0, 2.2894972560001, 0.0, -0.03074106)]


def _same_API(X, Y, exclude=None):
    """Check that public methods of X also exist in Y
    """

    if exclude is None:
        exclude = []

    for name in dir(X):

        # Skip internal symbols
        if name.startswith('_'):
            continue

        # Skip explicitly excluded methods
        if name in exclude:
            continue

        # Check membership of methods
        attr = getattr(X, name)
        if isinstance(attr, types.MethodType):
            if name not in dir(Y):
                msg = ('Method "%s" of "%s" was not found in "%s"'
                       % (name, X, Y))
                raise Exception(msg)


def same_API(X, Y, exclude=None):
    """Check that public methods of X and Y are the same.

    Input
        X, Y: Python objects
        exclude: List of names to exclude from comparison or None
    """

    _same_API(X, Y, exclude=exclude)
    _same_API(Y, X, exclude=exclude)

    return True


def combine_coordinates(x, y):
    """Make list of all combinations of points for x and y coordinates
    """

    points = []
    for px in x:
        for py in y:
            points.append((px, py))
    points = numpy.array(points)

    return points
