from numpy import *
import inspect
from operator import itemgetter


def procdf(function,allvars,procaxis,dimidx=0):
    iterate = False
    if (dimidx <= len(shape(allvars[0]))):
        if (procaxis[dimidx] == False):
            iterate = True

    if iterate:
        #procaxis[dimidx] == False  !!!
        #so  the first item shape of each variable allvars is allvars[0].shape[0] 
        dataout = []
        for axidx in range(allvars[0].shape[0]):
            allvarsin = []
            for evar in allvars:
                allvarsin.append(evar[axidx])
            dtotmp, outcoords = procdf(function,allvarsin,procaxis,dimidx=dimidx+1)
            dataout.append(dtotmp)
    else:
        #print(allvars)
        dataouttemp = function(allvars)
        if (type(dataouttemp).__name__ == 'list'):
            dataout = dataouttemp[0]
            outcoords = dataouttemp[1]
            # vardimsout...
        else:
            dataout = dataouttemp
            shapeout = shape(dataout)
            outcoords = []
            for eshape in shapeout:
                # <False> means that the dimension given by the output of the 
                # function is not specified. Afterwards, it should be checked 
                # whether this dimension is the same as the input dimension
                # If so, this should become None
                outcoords.append(False)
    return dataout, outcoords

def multifunc(function,allvars,procaxis,vardims):
    """
    function: the function that has to be applied on the variable
    procaxis:
          Description: indicates for each variable (ranked from 0 to ... ) that 
                       have to be processed 
          Dimensions: the amount of variables occuring in any variable: 
          Example: (False, True, True, False, ...).
        
    vardims: 
          Description: list of 'pointers' to dimensions for each variable array 
          Dimensions: (amount of variables, dimensions of that variable) ,
                          so the second dimension is not fixed for each row
          Example: [[3,     1   , 2   , 4    , ...],
                    [2,     3   , 4   , 6    , ...],
                    ....                     
                   ]
    """
    
    # add dimensions to variables (i.e. expand array) 
    #in case they are missing (tbi: make this unnecessary)
    dimcount = len(procaxis) 
    for ivar,evar in enumerate(allvars):
        for idim in reversed(range(dimcount)):
            if idim not in vardims[ivar]:
                # if a function has to be applied on that dimension, 
                #only add an 'axis' for that dimension
                if procaxis[ivar] == True:
                    allvars[ivar] = allvars[ivar][newaxes,:]
                # else: length of dimension is 
                # considered the same for all variables! 
                # so multiple copies are made from the dimension 
                # of an arbitrary other variable 
                # (we just take the first that has this variable)
                else:
                    ldone = False
                    for ivar2,evar2 in enumerate(allvars):
                        if idim in vardims[evar2]:
                            if ldone == False:
                                allvars[ivar] = repeat(allvars[ivar][newaxis,:],0)
                            ldone = True
                vardims[ivar].insert(0,idim)
                    
    # put dimensions of all variables arrays in the same order 
    # as the standard order (which is implicitely given by vardims)
    for ivar,evar in enumerate(allvars):
        allvars[ivar] = transpose(evar,vardims[ivar])
    
    # now transpose all matrices in a similar way in such a way that the dimensions 
    # to be processed are at the end
    
    refsorted = sorted(zip(procaxis,range(dimcount)), key=itemgetter(0,1)) 
    trns = [] # the transpose indices
    trnsprocaxis = [] # procaxis after transpose
    #print('data processing started')
    for irefsorted,erefsorted in enumerate(refsorted):
        trns.append(erefsorted[1])
        trnsprocaxis.append(erefsorted[0])
    for ivar,evar in enumerate(allvars):
        allvars[ivar] = transpose(evar,trns)
    # ...
    dataouttrns,outcoordstrnstmp = procdf(function,allvars,trnsprocaxis)
    
    # Reorganize the output coordinate list, so that they 
    # are aligned with the standard dimension numbering. So add #nones where needed
    outcoordstrns = []
    iocttmp = 0
    for i,etrnsprocaxis in enumerate(trnsprocaxis):
        if etrnsprocaxis: # if the function is applied along the current dimension
            outcoordstrns.append(outcoordstrnstmp[iocttmp])
            iocttmp = iocttmp + 1
        else:
            # <None> means that the current dimension corresponds to the input data 
            # dimensions (is trivially none when this dimension isn't processed)
            outcoordstrns.append(None)
    
    #print('data processing ended')
    
    # build the 'inverse permutation operator'
    inv = range(len(trns))
    for itrns,etrns in enumerate(trns):
        inv[etrns] = itrns
    
    # inverse permutation of the output data
    dataout = transpose(dataouttrns,inv)
    
    outcoords = []
    # inverse permuation of the output coordinates
    for iinv,einv in enumerate(inv):
        outcoords.append(outcoordstrns[einv])
    
    return dataout,outcoords

