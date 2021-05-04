from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
import ee
ee.Initialize()
import os
from datetime import date , timedelta
from datetime import datetime
from dateutil.parser import parse
import pandas as pd
import pygeoj
import json
def index(request):
    print("hi")
    geometry = ee.Geometry.Polygon([[[83.829803, 28.316455],[84.157677, 28.316455],[84.157677, 28.150463],
        [83.829803, 28.150463]]])
    print(geometry)
    context = {
        "dem": dem(geometry),
    }
    return render(request, 'index.html',context)
def dem(geometry):
    lulc1 = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global").select('discrete_classification');
    # print(lulc1)
    properties = lulc1.propertyNames();
    print(properties);
    image = ee.Image("USGS/SRTMGL1_003")
    viz_parameter = {'min':0,'max':3000,'palette': ['white','black','red']}
    map_id_dict = ee.Image(image).getMapId(viz_parameter)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    # print(tile)
        # return "hi i calaculated"
    return tile