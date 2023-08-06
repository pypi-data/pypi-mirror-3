# Copyright (c) 2009 W. Trevor King and the authors listed at the
# following URL, and/or the authors of referenced articles or
# incorporated external code:
# http://en.literateprograms.org/Quickhull_(Python,_arrays)?action=history&offset=20090125100840
# 
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
# 
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
# 
# Retrieved from: http://en.literateprograms.org/Quickhull_(Python,_arrays)?oldid=16036
# Modified by W. Trevor King to add Simplex and point_inside_hull

from numpy import *

link = lambda a,b: concatenate((a,b[1:]))
edge = lambda a,b: concatenate(([a],[b]))

def qhull(sample):
    def dome(sample,base): 
        h, t = base
        dists = dot(sample-h, dot(((0,-1),(1,0)),(t-h)))
        outer = repeat(sample, dists>0, 0)

        if len(outer):
            pivot = sample[argmax(dists)]
            return link(dome(outer, edge(h, pivot)),
                        dome(outer, edge(pivot, t)))
        else:
            return base

    if len(sample) > 2:
    	axis = sample[:,0]
    	base = take(sample, [argmin(axis), argmax(axis)], 0)
    	return link(dome(sample, base),
                    dome(sample, base[::-1]))
    else:
	return sample

class Simplex(object): # N+1 points in N dimensions
    def __init__(self, vertices):
        self.vertices = vertices
        self.origin = self.vertices[0]
        self.basis = array([v-self.origin for v in self.vertices[1:]],
                           dtype=double).transpose()
        self.inverse_basis = linalg.inv(self.basis)
    def simplex_coordinates(self, points):
        rel_coords = (points-self.origin).transpose()
        return dot(self.inverse_basis, rel_coords).transpose()
    def inside_single_point_simplex_coords(self, point, tol=1e-15):
        # check that we're in the positive coordinate
        for coordinate in point:
            if coordinate < -tol:
                return False
        # check that we're under the (1,1,1,...) plane
        if point.sum() > 1+tol:
            return False
        return True
    def inside(self, points):
        ps = self.simplex_coordinates(points)
        if not hasattr(ps[0], "__len__"): # single point
            return self.inside_single_point_simplex_coords(ps)
        else:
            insides = []
            for p in ps:
                insides.append(self.inside_single_point_simplex_coords(p))
            return insides

def points_inside_hull(hull, points):
    if not hasattr(points[0], "__len__"): # single point
        points = numpy.array([points])
    inside = [False]*len(points)
    pivot = hull[0]
    for a,b in zip(hull[1:], hull[2:]):
        rb = b-pivot
        if vdot(rb, rb) == 0: # hull is a closed loop
            continue
        simplex = Simplex([pivot,a,b])
        simplex_inside = simplex.inside(points)
        if any(simplex_inside):
            for i,value in enumerate(simplex_inside):
                if value == True:
                    inside[i] = True
    return inside

def print_postscript(sample, hull):
    print "%!"
    print "100 500 translate 2 2 scale 0 0 moveto"
    print "/tick {moveto 0 2 rlineto 0 -4 rlineto 0 2 rlineto"
    print "              2 0 rlineto -4 0 rlineto 2 0 rlineto} def"
    for (x,y) in sample:
	print x, y, "tick"
    print "stroke"
    print hull[0,0], hull[0,1], "moveto"
    for (x,y) in hull[1:]:
	print x, y, "lineto"
    print "closepath stroke showpage"

if __name__ == "__main__":
    #sample = 10*array([(x,y) for x in arange(10) for y in arange(10)])
    sample = 100*random.random((32,2))
    hull = qhull(sample)
    if all(point_inside_hull(hull, sample)) != True:
        for point in sample:
            assert point_inside_hull(hull, point) == True, \
                "point %s should be in hull\n%s" % (sample, hull)
    apoints = hull[0:-1]
    bpoints = hull[1:]
    if any(point_inside_hull(hull, apoints - 0.1*(bpoints-apoints))) == True:
        for a,b in zip(apoints, bpoints):
            assert point_inside_hull(hull, a - 0.1*(b-a)) == False, \
                "point %s (a=%s, b=%s) should be outside hull\n%s" \
                % (point, a, b, hull)
    print_postscript(sample, hull)
