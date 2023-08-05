# calculate mean
from numpy import *
from dtrange import *
from scisel import *


# 1. [2. 3. 4.] 
#average(


# calculate averaged cycle
#input:
    # data: input data
    # timeco: data coordinates
    # timewarp: length of the cycle
# todo: add an option to count the amount of samples for each member of the cycle -> then crop in cosel should
# be set to True so that we still take the mean even though there is no data available.
def avgcycle(data, timeco = None, timewarp = None):
    if (timeco == None):
        timeco = arange(len(data))
    if (timewarp == None):
        timewarp = timeco[1] - timeco[0]
    iscounted = tile(False,len(data))
    tempco = dtrange(timeco[0],timeco[len(timeco)-1],timewarp)
    dataout = []
    timecoout = []
    for idata in range(len(data)):
        if (iscounted[idata] == False):
            tempco2 = tempco + (timeco[idata] - timeco[0])
    
            #coordinates of data taken into account for this timestamp
            tempcosel = cosel(timeco,tempco2)
    
            # include some option to ignore the times on which there is no data
            # include some option to ignore the nan data
    
            # if some data could not be selected, a nan will be produced
            # in cosel, crop is left to False, because we want to discover whenever data is not available
            tdatacosel = datacosel(data,cosel = tempcosel)

            # we don't want to end up with an error if None is met: we just want a 'nan' from the mean.
            for edata in tdatacosel:
                if (edata == None):
                    edata = nan

            dataout.append(mean(datacosel(data,cosel = tempcosel)))
            timecoout.append(timeco[idata])
            #dataout.append(mean(scisel(data,timeco,tempco2) )
    
            #it would be much more elegant if we could simple do: iscounted[tempcosel] = True
            #but None inside [] does strange things,
            #          (tempcosel!=None : manually crop (same as if we did cosel(...,crop=True)))
            for etempcosel in tempcosel:
                if (etempcosel != None): # None inside [] does strange things
                    iscounted[etempcosel] = True
    return(array(dataout),array(timecoout))    
    


# select data

