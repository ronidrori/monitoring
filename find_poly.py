#-------------------------------------------------------------------------------
# Name:        find_poly
# Purpose: find a polygon, with a specific area, around the sampling point under
#          outer polygon constrain
# Author:      roni drori
#
# Created:     30/04/2013
# Copyright:   (c) hamaarag 2013
# Licence:     cc
#-------------------------------------------------------------------------------

#def find_poly(sampling_point, sampling_poly,):
import shapely
import fiona
from shapely.geometry import mapping, shape
from fiona import collection
import pylab
import math

buf_r = 125.
poly_area = 62500.
eps = 1e-6
delt = 0.01
max_iteration = 1000
flip = 0
print buf_r
path = "G:\\Data\\UNITS\\Harhanegev\\test_sample\\"
pntfile = path+"sample_point.shp"
bfrfile = path+"buf_point.shp"
polfile = path+"sample_polygon.shp"
intfile = path+"inter5.shp"
cntfile = path+"cnt5.shp"
# read the sample point
point = fiona.open(pntfile,"r")
sample_point = point.next()
spoint = shape(sample_point["geometry"])
bpoint=spoint.buffer(buf_r)
point.close
#read the containing polygon
poly = fiona.open(polfile,"r")
sample_poly = poly.next()
spoly = shape(sample_poly["geometry"])
poly.close
#intersect
inter = spoly.intersection(bpoint.envelope)
area = inter.area
dif = poly_area - area
count = 0
print buf_r
while ((abs(dif) > eps) and count < max_iteration):
    if (dif > 0):
        buf_r = buf_r + delt
        #print ">0",buf_r,dif
    else:
        flip = 1
        delt = delt/2.
        buf_r = buf_r - delt
        flip = 0
        #print "<0",buf_r
    bpoint=spoint.buffer(buf_r)
    inter = spoly.intersection(bpoint.envelope)
    area = inter.area
    dif = poly_area - area
    count = count + 1


schema = { 'geometry': 'Polygon', 'properties': { 'id': 'int' } }
#writing out
with collection(
       intfile, "r", "ESRI Shapefile") as output:
           output.write({
                'properties': {
                    'id': 1
                },
                 'geometry': mapping(inter)
            })

#write centroid out
schema = { 'geometry': 'Point', 'properties': { 'id': 'int' } }
center = inter.centroid
#writing out
with collection(
       cntfile, "w", "ESRI Shapefile", schema,{'init': 'epsg:2039'}) as output:
           output.write({
                'properties': {
                    'id': 1
                },
                 'geometry': mapping(center)
            })