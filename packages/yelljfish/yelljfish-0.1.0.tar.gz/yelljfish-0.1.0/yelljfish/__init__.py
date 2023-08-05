#!/usr/bin/env python3

# yelljfish: a pixel-based, potentially pseudo-random image generator
# Copyright (C) 2011 Niels Serup

# This file is part of yelljfish.

# yelljfish is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.

# yelljfish is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more
# details.

# You should have received a copy of the GNU Affero General Public License along
# with yelljfish.  If not, see <http://www.gnu.org/licenses/>.

'''
yelljfish generates strange-looking pixelized pictures.
It currently supports outputting to PNG only.
'''
# See README.txt for more information.

__version__ = '0.1.0'
__author__ = 'Niels Serup <ns@metanohi.name>'
__copyright__ = '''\
yelljfish 0.1.0
Copyright (C) 2011  Niels Serup
License AGPLv3+: GNU AGPL version 3 or later <http://gnu.org/licenses/agpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.'''

import sys
from optparse import OptionParser
import random
from ._core import generate_image as _generate_image

def generate_image(width=640, height=480, runs=3, points=None,
                   numberofpoints=None, rangeofpoints=(3, 8), out=None):
    """
    Generate an image of size (width, height) with specified points if points is
    given, else randomly generated points, the number of which is described by
    either numberofpoints or a random number in rangeofpoints.
    """
    points = tuple(map(tuple, points))
    if points:
        if len(points) < 3:
            raise ValueError('not enough points (< 3)')
        elif len(set(points)) > width * height:
            raise ValueError('too many points (set > width * height)')
        elif tuple(filter(lambda wh: 0 > wh[0] or width <= wh[0] or
                          0 > wh[1] or height <= wh[1], points)):
            raise ValueError('all points must be within the canvas boundary')
    else:
        n = numberofpoints if numberofpoints else random.randint(*rangeofpoints)
        points = []
        for i in range(n):
            while True:
                p = (random.randrange(0, width), random.randrange(0, height))
                if not p in points: break
            points.append(p)
    points = tuple(tuple(x) if len(x) == 3 else
                   (x[0], x[1], random.randrange(0, 2**32)) for x in points)
    _generate_image(width, height, runs, points, out)

def parse_args(cmdargs=None):
    """Generate an image based on command-line arguments."""
    class _SimplerOptionParser(OptionParser):
        """A simplified OptionParser"""

        def format_description(self, formatter):
            self.description = self.description.strip()
            return OptionParser.format_description(self, formatter)

        def format_epilog(self, formatter):
            return self.epilog.strip() + '\n'

        def add_option(self, *args, **kwds):
            try: kwds['help'] = kwds['help'].strip()
            except KeyError: pass
            return OptionParser.add_option(self, *args, **kwds)

    parser = _SimplerOptionParser(
        prog='yelljfish',
        usage='Usage: yelljfish [OPTION]... OUTFILE...',
        version=__copyright__,
        description='''
a pixel-based, potentially pseudo-random image generator
''',
        epilog='''
yelljfish requires at least three starting points to be able to generate an
image. The default action is to pseudo-randomly generate between 3 and 8
starting points with pseudo-random positions (none overlapping) within a canvas
of 640x480 pixels. These defaults can be changed, see the options above.

The '-' character can be used to symbolize standard out.

yelljfish currently only supports outputting to the PNG format.

Examples:
  Output a file with default options:
    yelljfish out.png

  Use a different number of points (5):
    yelljfish -n 5 5p.png

  Use a different range (5--6):
    yelljfish -r 5 6 out.png

  Use a special canvas size:
    yelljfish -x 1280 -y 800 large.png

  Use four non-random starting points:
    yelljfish -p 40 33 -p 22 9 -p 98 98 -p 500 400 d.png
''')

    parser.add_option('-n', '--number-of-points', dest='numberofpoints',
                      type='int', metavar='INT', help='''
use a specified number of points instead of a random number between 3 and 8
''')

    parser.add_option('-r', '--range-of-number-of-points', dest='rangeofpoints',
                      type='int', metavar='FROM TO', help='''
use a specified range of numbers to select a number from at random instead of
the default 3 to 10 range
''', default=(3, 8))

    parser.add_option('-t', '--runs', dest='runs',
                      type='int', metavar='RUNS', help='''
apply the yelljfish algorithm RUNS times (defaults to 3)
''', default=3)

    parser.add_option('-x', '--width', dest='width',
                      type='int', metavar='WIDTH', help='''
set width of canvas in pixels
''', default=640)

    parser.add_option('-y', '--height', dest='height',
                      type='int', metavar='HEIGHT', help='''
set height of canvas in pixels
''', default=480)

    parser.add_option('-p', '--point', dest='points', action='append',
                  type= 'int', metavar= 'X Y VALUE', help= '''
add a user-defined point. VALUE is a 32-bit unsigned number. If just one point is added, no random points
will be generated, and at least two more user-defined points must be added.
This option invalidates both -n and -r.
''', default=[])

    parser.add_option('-P', '--point-without-value', dest='pointswithoutvalues',
                      action='append', type='int', metavar='X Y', help='''
do the same as -p, except use a random VALUE
''')

    if not cmdargs:
        cmdargs = sys.argv[1:]
    o, a = parser.parse_args(cmdargs)
    if o.pointswithoutvalues:
        o.points.extend(o.pointswithoutvalues)
    if o.points:
        if len(o.points) < 3:
            parser.error('you must specify at least 3 points')
    try: o.outfile = a[0]
    except IndexError: parser.error('you must specify an outfile')
    generate_image(width=o.width, height=o.height, points=o.points,
                   runs=o.runs, numberofpoints=o.numberofpoints,
                   rangeofpoints=o.rangeofpoints, out=o.outfile)

if __name__ == '__main__':
    parse_args()


####################
# Local Variables:
# buffertitle: "yelljfish.init"
# End:
