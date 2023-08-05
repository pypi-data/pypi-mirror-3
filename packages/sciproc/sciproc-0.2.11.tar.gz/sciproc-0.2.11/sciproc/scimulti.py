
# aim: 
# scifunc: apply a certain function serveral times on a multidimensional matrix; calculate a certain
# function along a specified axis
# reddim: reduce the dimension of a multidimensional matrix


# todo for scifunc: 
# pass multiple variables for one function
# make an array attribute as a substitute for arraysel
# currently, it is expected that the function conserves the # of dimensions. If not, there will be problems.
#     so possibility to decrease dimension of matrix is still needed in which we may want to throw away a dimension automatically (like
#     for making averages by summing over an index for a certain dimension) 
#     we should detect automatically when it has to be removed, e.g. when the function reduces the # of dimensions of a matrix
#     
# coordinate build in as a array attributeis: 
#     array.arraysel(SEL) 
#     arraycrop (of zoiets)
# 

from numpy import *
from sciproc import arraysel


# apply a function for each element along various axis
# data: matrix to be processed
# axisref: a list of boolean which indicates along which axis the function has to be applied
#       if false: the function is applied seperately for each element along the current axis
#       if true: all elements of the current axis are used as input for the function
# example, if data is a 4x3x2 matrix and SEL=[False,True,False], the function deffunc will be applied
# for each of the 4 elements along the first axis and for each of he 2 elements along the third axis.
# So the function will be applied 4x2 times. Each time, the 3 elements along second axis are
# all passed to the function. The size of the output matrix depends on the function.
def multifunc(data,axisref,deffunc):
    SEL = list(repeat(None,len(shape(data))))
    sizeout = list(repeat(None,len(shape(data))))
    #before calculating the dataout matrix, its dimension has to be acquired
    for dim in range(len(shape(data))):
        if (axisref[dim] == True):
            SEL[dim] = range(size(data,axis=dim))
        else:
            SEL[dim] = [0] 
            sizeout[dim] = size(data,axis=dim)
    # print(SEL)
    # print(data.shape)
    dummydataout = deffunc(data[arraysel(SEL,data.shape)])
    dimout = 0
    for dim in range(len(shape(data))):
        if (axisref[dim] == True):
            sizeout[dim] = size(dummydataout,axis=dimout)
            dimout = dimout + 1
    dataout = zeros(sizeout)
    #enige wat we eigenlijk nodig hebben voor scandata is shape(data) en shape(dataout) en dataout
    SEL = list(repeat(None,len(shape(data))))
    SELout = list(repeat(None,len(shape(dataout))))
    print(SELout)
    print(dataout.shape)
    scandata(0,axisref,SEL,data,deffunc,SELout,dataout)
    return dataout

# this function is called by multifunc. It iteratates through the necessary dimensions to apply a function
def scandata(dimidx,axisref,SEL,data,deffunc,SELout,dataout):
    # we lopen elk element van een as af
    print('dimidx',dimidx,' BEGIN')
    # print(size(data,axis=dimidx))
    axidx = 0
    while (((axisref[dimidx] == True) & (axidx == 0)) | \
            ((axisref[dimidx] == False) & (axidx < size(data,axis=dimidx)) )):
        if (axisref[dimidx] == False):
            SELout[dimidx] = [axidx]
            SEL[dimidx] = [axidx]
            # print('axidx',axidx)
            # print('sizeaxidx',size(data,axis=dimidx))
            # print(((axisref[dimidx] == True) & axidx < size(data,axis=dimidx) ))
        else:
            SELout[dimidx] = range(size(dataout,axis=dimidx))
            SEL[dimidx] = range(size(data,axis=dimidx))
        # we gaan naar een hogere dimensie
        if (dimidx < (len(shape(data)) - 1)):
            scandata(dimidx + 1,axisref,SEL,data,deffunc,SELout,dataout)
        else:
            # print(SELout)
            # print(dataout.shape)
            # print(SEL)
            # print(data.shape)
            dataout[arraysel(SELout,dataout.shape)] = deffunc(data[arraysel(SEL,data.shape)])

        print('axidx',axidx)
        print('SEL',SEL)
        print('SELout',SELout)
        axidx = axidx + 1
    print('dimidx',dimidx,' END')

# reduce dimension of a multidimensional matrix
# input: 
#   data: matrix
#   indices: th dimension that has to be left away
#   el: which element has to be taken for the to be removed dimension (default: first element)
def reddim(data,indices,el = 0):
    #el = repeat(0,len(indices))
    for dim in range(len(shape(data))):
        if (dim in indices):
            SEL[dim] = el
        else:
            SEL[dim] = range(size(data,axis=dim))
    return data[arraysel(SEL,shape(data))]


# # reduce multiple dimensions at ones
# # indices: list of indices
# # data: the multi-dim matrix we want to reduce
# # todo: rewrite it to make it more efficient
# def reddimmulti(data,indices):
#     dataout = data
#     for index in range(len(indices)):
#         dataout = reddim(dataout,indices[index])
#         #we have to correct the indices as dimension of the output matrix is reduced already
#         for index2 in range(index,len(indices)):
#             indices[index2] = indices[index2] - 1
#     return dataout

