#!/usr/bin/python
# Filename: scisel.py

from numpy import *
from dtrange import *

# aim:
# get the indices of coords which occur in outcoords
# notes:
# - ordered data is needed for both coords and outcoords.
# - we expect that the data at the asked sample time (outcoords) exists in the original sample (coords). If not, a nan will be produced.
def cosel(coords = None, outcoords = None):
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
    return selout

# someone may want to do this (if it's possible) instead of interpolation
def datacosel(indata, coords = None, outcoords = None, \
              start= None,end= None,step = None,  \
              outstart = None, outend = None, outstep = None):
    # if coordinates not given, make it from the start, end, step arguments
    if (coords == None):
        coords = dtrange(start, end, step)
    if (outcoords == None):
        outcoords = dtrange(outstart, outend, outstep)
    if (outcoords == None):
        outcoords = coords
    cocosel = cosel(coords = coords, outcoords = outcoords)
    dataout = tile(None,len(cocosel))
    for iel, el in enumerate(cocosel):
        if (el != nan):
            dataout[iel] = indata[el]
        else:
            dataout[iel] = nan
    return dataout


# aim: build an array (boolean) selection from indices of any dimension
# the cooredinates from which elements of the multi-dim matrix are selected
#
# SHAPE: shape of the multidim-matrix
# SEL: list indices of each dimension of a matrix we want to selected. e.g. with SEL=[[0:3],[0],[0]],
# we select a 3x1x1 matrix 
# usage: datasel = data[arraysel(shape(data),[[0:20],[0:10],[23]])
def arraysel(SHAPE,SEL):
    lfirst = True
    #ntruefalse: the matrix we want to construct, which can be used to select the data.
    ntruefalse = True
    for axidx,dimsize in reversed(list(enumerate(SHAPE))):
        # build a boolean array for current dimension
        curdimarray = (zeros(dimsize) == 1)
        for element in SEL[axidx]: 
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
 
