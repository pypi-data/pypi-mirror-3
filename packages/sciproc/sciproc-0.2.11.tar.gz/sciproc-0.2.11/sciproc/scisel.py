#!/usr/bin/python
# Filename: scisel.py

from numpy import *
from dtrange import *

# aim:
# get the indices of coords which occur in outcoords
# notes:
# - ordered data is needed for both coords and outcoords.
# - we expect that the data at the asked sample time (outcoords) exists in the original sample (coords). If not, a nan will be produced.

# crop = option whether the unavailable ones should be filled out with nan, or whether the unavailable ones
# should be ignored. In the latter, the output array will not have the same size as outcoords!


def cosel(coords = None, outcoords = None, crop=False):
    steps = len(outcoords)
    selout = repeat(None,steps)
    idx = 0
    outidx = 0
    for datetime in coords:
        if ((datetime >= outcoords[0]) & (datetime <= outcoords[steps - 1]) & \
            (outidx < steps)):
            if ((datetime >= outcoords[outidx])):
                while ((outidx < steps) & (outcoords[outidx] < datetime)):
                    outidx = outidx + 1
                if (datetime == outcoords[outidx]):
                    #outdata[outidx] = indata[idx]
                    selout[outidx] = idx
                outidx = outidx + 1
        idx = idx + 1
    if (crop == True):
        selout = selout[selout !=None]
    return selout

# someone may want to do this (if it's possible) instead of interpolation
def datacosel(indata, cosel = None, coords = None, outcoords = None, \
              start= None,end= None,step = None,  \
              outstart = None, outend = None, outstep = None, \
              crop = False):
    if (cosel == None):
        # if coordinates not given, make it from the start, end, step arguments
        if (coords == None):
            coords = dtrange(start, end, step)
        if (outcoords == None):
            outcoords = dtrange(outstart, outend, outstep)
        if (outcoords == None):
            outcoords = coords
        cosel = cosel(coords = coords, outcoords = outcoords)

    # remove NA (None) values if specified
    # would be more elegant if we could simply do cosel = cosel[cosel!=None], but None inside [] does strange things
    if (crop == True):
        tempcosel = []
        for ecosel in cosel:
            if (ecosel != None):
                tempcosel.append(ecosel)
        cosel = array(tempcosel)

    dataout = tile(None,len(cosel))
    #dataout = indata[cosel[cosel!=None]]
    #dataout[cosel==None] = nan
    #dataout[cosel!=None] = indata[cosel[cosel!=None]]
    for iel, el in enumerate(cosel):
        if (el != None):
            dataout[iel] = indata[el]
        else:
            dataout[iel] = None
    return dataout


# aim: build an array (boolean) selection from indices of any dimension
# the coordinates from which elements of the multi-dim matrix are selected
#      wrapper function for a more advanced array selection
# SHAPE: shape of the multidim-matrix
# SEL: list indices of each dimension of a matrix we want to selected. e.g. with SEL=[[0,1,2],[0],[0]],
# we select a 3x1x1 matrix 
# usage: datasel = data[arraysel(shape(data),[[0,1,2],[0,2,4],[22,23]])
def arraysel(SEL,SHAPE = None):
    if (SHAPE == None):
        SHAPE = []
        for eSELECT in SELECT:
            SHAPE.append(max(eSELECT) + 1 )
    lfirst = True
    #ntruefalse: the matrix we want to construct, which can be used to select the data.
    ntruefalse = True
    for axidx,dimsize in reversed(list(enumerate(SHAPE))):
        # build a boolean array for current dimension
        curdimarray = (zeros(dimsize) == 1)
        for element in SEL[axidx]: 
            if (element != None): # workaround: data[None] selects all data
                curdimarray[element] = True 
        otruefalse = ntruefalse
        # for the first dimension, we initialize ntruefalse(shape)
        if (lfirst):
            ntruefalseshape = dimsize
            lfirst = False
        else:
            ntruefalseshape = list(ntruefalse.shape)
            ntruefalseshape.insert(0,dimsize)
        ntruefalse = (zeros(ntruefalseshape) == 1)
        for ielement,element in enumerate(curdimarray):
            if (element == True):
                ntruefalse[ielement] = otruefalse
            else:
                ntruefalse[ielement] = False
    return ntruefalse
 
