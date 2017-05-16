#!/usr/bin/python

#************************************************************************************
# Copyright (c) 2017 James Sinton
#
#  All rights reserved.
#  
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  
#  * Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#  
#  * Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#  
#  * Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#  
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#  IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#  DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
#  DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#  SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
#  CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
#  OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#************************************************************************************
#   CHANGE LOG
#
#   2017-04-24  Initial development                                       - 0.1.0
#   2017-05-15  Estimate population for each voting precinct              - 0.2.0
#
#************************************************************************************

import os

import pandas as pd
import geopandas as gpd
from geopandas import GeoSeries, GeoDataFrame

#from shapely.wkt import loads

output = 'harris-county-pop'
outputGeoJSON = output + '.geojson'
precinctsFile = 'geojson/HARRIS_COUNTY_VOTING_PRECINCTS.geojson' # Public domain https://opendata.arcgis.com/datasets/b6d912f1cc09421b81b80bae315eb20b_0.geojson
popFile = 'geojson/houston-population-data-2010.geojson' # Copyright (c) 2015 PluralismProject http://worldmap.harvard.edu/data/geonode:Population_Density_2010_Houston_R0a

precincts = gpd.read_file(precinctsFile)
pop = gpd.read_file(popFile)

# remove unnecessary columns from precincts GeoDataFrame
precincts = precincts.drop('OBJECTID', axis=1)
precincts = precincts.drop('OBJECTID_1', axis=1)

precincts = precincts.sort_values(['PRECINCT'],ascending=[True])

#print precincts

area = 0.0
totalPop = 0
print "Precinct, Population"
popArray = []
for precIndex, precRow in precincts.iterrows():
    popPrecinctsBool = pop.geometry.intersects(precRow.geometry)
    popInterPrecRow = pop[popPrecinctsBool]
    
    intersection = popInterPrecRow.intersection(precRow.geometry)
    areas = intersection.area
    precPop = 0.0
    for popIndex, popRow in popInterPrecRow.iterrows():
        interArea = areas[popIndex]
        popArea = GeoSeries(popRow.geometry).area[0]

        share = (interArea/popArea)
        
        precPop = precPop + (popRow.POP2010 * share)
    
    print str(precRow.PRECINCT) + ", " + str(int(precPop))
    totalPop = totalPop + int(precPop)
    popArray.append(int(precPop))

print "Total Pop: ", totalPop

# See issue #367 https://github.com/geopandas/geopandas/issues/367
try: 
    os.remove(outputGeoJSON)
except OSError:
    pass
precincts.to_file(outputGeoJSON, driver='GeoJSON')
