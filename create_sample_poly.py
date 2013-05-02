#-------------------------------------------------------------------------------
# Name:        module1
# Purpose: create sampling polygon with a defined sized around
# randomly selected point constraint by the valid area polygon
#
# Author:      Ron Drori (ron.drori@hamaarag.org.il)
#
# Created:     02/05/2013
# Copyright:   hamaarag
# Licence:     CC
#-------------------------------------------------------------------------------

import shapely
import fiona
from shapely.geometry import mapping, shape
from fiona import collection


def find_containing_poly(point, polyfile):
    sample_poly = fiona.open(polyfile,"r")
    poly = sample_poly.next()
    spoly = shape(poly["geometry"])
    while (not point.within(spoly)):
        poly = sample_poly.next()
        spoly = shape(poly["geometry"])
    sample_poly.close
    return spoly


def create_sample_poly(spoly, spoint):

    #some parameters
    buf_r     = 125.        # buffer around the point in meters
    poly_area = 62500.      # output polygon area
    eps       = 1e-6        # desired accuracy of polygon area
    delt      = 1.0        # delta for changing change buffer (buf_r)
    max_iteration = 10000    # maximum number of iteration

    #dummy varibles
    flip  = 0
    count = 0

    # first creat a buffer around the random point
    bpoint=spoint.buffer(buf_r)

    # find the intersection between the buffer polygon and the
    # valid area polygon
    inter = spoly.intersection(bpoint.envelope)

    # find the area of the intersection polygon
    area = inter.area
    dif = poly_area - area


    while ((abs(dif) > eps) and count < max_iteration):
        if (dif > 0):
            buf_r = buf_r + delt
        else:
            flip = 1
            delt = delt/2.      # for convegence
            buf_r = buf_r - delt
            flip = 0
        bpoint=spoint.buffer(buf_r)
        inter = spoly.intersection(bpoint.envelope)
        area = inter.area
        dif = poly_area - area
        count = count + 1

    return inter


def main():


    path = "G:\\Data\\UNITS\\Harhanegev\\test_sample\\"
    pntfile = "G:\\Data\\UNITS\\Harhanegev\\near_sample\\points_250m.shp"
    polfile = "G:\\Data\\UNITS\\Harhanegev\\near_clean\\near_yeruham_single_gt250.shp"
    intfile = path+"sampling_polygons1.shp"
    cntfile = path+"sampling_centroids1.shp"


    # loop over points
    id = 0
    with collection(pntfile, "r", "ESRI Shapefile") as points:
            for p in points:
                spoint = shape(p["geometry"])
                spoly = find_containing_poly(spoint, polfile)
                poly  = create_sample_poly(spoly, spoint)
                #writing out
                schema = { 'geometry': 'Polygon', 'properties': { 'id': 'int' } }
                id=id+1
                print id
                if (id == 1):
                    status = "w"
                else:
                    status = "a"

                # write polygon
                with collection(
                       intfile, status, "ESRI Shapefile", schema,{'init': 'epsg:2039'}) as output:
                           output.write({
                                'properties': {
                                    'id': id
                                },
                                 'geometry': mapping(poly)
                            })
                # write centroid
                schema = { 'geometry': 'Point', 'properties': { 'id': 'int' } }
                center = poly.centroid
                with collection(
                       cntfile, status, "ESRI Shapefile", schema,{'init': 'epsg:2039'}) as output:
                           output.write({
                                'properties': {
                                    'id': id
                                },
                                 'geometry': mapping(center)
                            })

if __name__ == '__main__':
    main()
