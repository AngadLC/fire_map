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
    context = {
        "dem": dem(),
        "slope":slopefun(),
        "aspect":aspect(),
        "lulc":lulc(),
        'temp':temp(),
        'firerisk':firerisk()
    }
    return render(request, 'index.html',context)
def dem():
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
    return slopereclass

def aspect():
    image = ee.Image("USGS/SRTMGL1_003")
    aspect = ee.Terrain.aspect(image)
    aspectreclass = ee.Image(1) \
          .where(aspect.gt(0).And(aspect.lte(7)), 9) \
          .where(aspect.gt(7).And(aspect.lte(15)), 6) \
          .where(aspect.gt(15).And(aspect.lte(22)), 4)
    viz_parameter = {'min':0,'max':20,'palette': ['white','black','red']}
    return aspectreclass
def lulc():
    reclass = ee.Image("ESA/GLOBCOVER_L4_200901_200912_V2_3").select('landcover')    
    return reclass
# temperature
#cloud mask
def temp():
    def maskL8sr(col):
        # Bits 3 and 5 are cloud shadow and cloud, respectively.
        cloudShadowBitMask = (1 << 3)
        cloudsBitMask = (1 << 5)
        # Get the pixel QA band.
        qa = col.select('pixel_qa')
        # Both flags should be set to zero, indicating clear conditions.
        mask = qa.bitwiseAnd(cloudShadowBitMask).eq(0) \
                        .And(qa.bitwiseAnd(cloudsBitMask).eq(0))
        return col.updateMask(mask)

    
    col = ee.ImageCollection('LANDSAT/LC08/C01/T1_SR') \
        .map(maskL8sr) \
        .filterDate('2018-01-01','2018-12-31')
    
    #imagen reduction
    image = col.median()
    #median
    ndvi = image.normalizedDifference(['B5',
    'B4']).rename('NDVI')
    #select thermal band 10(with brightness tempereature), no calculation
    thermal= image.select('B10').multiply(0.1)
    #fractional vegetation
    fv =(ndvi.subtract(min).divide(max.subtract(min))).pow(ee.Number(2))
    #Emissivity
    a= ee.Number(0.004)
    b= ee.Number(0.986)
    EM=fv.multiply(a).add(b).rename('EMM')
    #LST in Celsius Degree bring -273.15
    LST = thermal.expression(
        '(Tb/(1 + (0.00115* (Tb / 1.438))*log(Ep)))-273.15', {
        'Tb': thermal.select('B10'),
        'Ep': EM.select('EMM')
        })
    
    # reclassify the land surface temperature
    reclassifylst = ee.Image(1) \
            .where(LST.gt(35),9) \
            .where(LST.gt(30).And(LST.lte(35)), 8) \
            .where(LST.gt(25).And(LST.lte(30)), 6) \
            .where(LST.gt(20).And(LST.lte(25)), 5) \
            .where(LST.gt(5).And(LST.lte(20)),3)
    return reclassifylst

# fire risk module

def firerisk():
    reclass,reclassifylst,slopereclass,reclassifyelevation,aspectreclass = aspect(),temp(),slopefun(), dem(), lulc()
    fire_risk = ee.Image.expression(
        '0.4*reclass +0.2*reclassifylst+0.15*slopereclass+0.15*reclassifyelevation+0.1*aspectreclass', {
        'reclass': reclass,
        'reclassifylst': reclassifylst,
        'slopereclass': slopereclass,
        'reclassifyelevation':reclassifyelevation,
        'aspectreclass':aspectreclass
    })

    fire_risk_reclassify = ee.Image(1) \
            .where( fire_risk.gt(7),4) \
            .where(fire_risk.gt(5).And(fire_risk.lte(7)),3) \
            .where( fire_risk.gt(3).And( fire_risk.lte(5)), 2) \
            .where( fire_risk.gt(0).And( fire_risk.lte(3)), 1)
    viz_parameter = {'min':0,'max':9,'palette': ['white','black','red']}
    map_id_dict = ee.Image(fire_risk_reclassify).getMapId(viz_parameter)
    tile = str(map_id_dict['tile_fetcher'].url_format)