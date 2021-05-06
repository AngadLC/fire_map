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
def project(request):
    # return HttpResponse("hi")
    return render(request,'project.html')
def index(request):
    print("hi")
    geometry = ee.Geometry.Polygon([[[83.829803, 28.316455],[84.157677, 28.316455],[84.157677, 28.150463],
        [83.829803, 28.150463]]])
    print(geometry)
    context = {
        "dem": dem(geometry),
        "slope":slopefun(),
        "aspect":aspect(),
        "lulc":lulc()
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
def slopefun():
    image = ee.Image("USGS/SRTMGL1_003")
    slopesmrt = ee.Terrain.slope(image)
    slopereclass = ee.Image(1) \
          .where(slopesmrt.gt(0).And(slopesmrt.lte(7)), 9) \
          .where(slopesmrt.gt(7).And(slopesmrt.lte(15)), 6) \
          .where(slopesmrt.gt(15).And(slopesmrt.lte(22)), 4)
    viz_parameter = {'min':0,'max':20,'palette': ['white','black','red']}
    map_id_dict = ee.Image(slopereclass).getMapId(viz_parameter)
    tile = str(map_id_dict['tile_fetcher'].url_format)
   
    return tile
def aspect():
    image = ee.Image("USGS/SRTMGL1_003")
    aspect = ee.Terrain.aspect(image)
    aspectreclass = ee.Image(1) \
          .where(aspect.gt(0).And(aspect.lte(7)), 9) \
          .where(aspect.gt(7).And(aspect.lte(15)), 6) \
          .where(aspect.gt(15).And(aspect.lte(22)), 4)
    viz_parameter = {'min':0,'max':20,'palette': ['white','black','red']}
    map_id_dict = ee.Image(aspect).getMapId(viz_parameter)
    tile = str(map_id_dict['tile_fetcher'].url_format)
    return tile
def lulc():
    lulc1 = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global").select('discrete_classification')
    # print(lulc1)
    # lulcreclass = lulc1.map(func_cbg)
    # viz_parameter = {'min':0,'max':200,'palette': ['white','black','red']}
    # map_id_dict = ee.Image(lulcreclass).getMapId(viz_parameter)
    # tile = str(map_id_dict['tile_fetcher'].url_format)
    # return tile
    

def func_cbg (img):

  return ee.Image(img) \
    .where(img.eq(0).And(img.eq(50)), 9) \
    .where(img.gt(50).And(img.lte(100)), 6) \
    .where(img.gt(100).And(img.lte(150)), 4)



