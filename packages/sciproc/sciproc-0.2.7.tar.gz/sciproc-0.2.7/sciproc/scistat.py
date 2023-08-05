# calculate mean


# 1. [2. 3. 4.] 
#average(


# calculate averaged cycle
#input:
    # data: input data
    # timeco: data coordinates
    # timewarp: length of the cycle
def avgcycle(data, timeco, timewarp,timecoout):
    iscounted = tile(False,len(data))
    tempco = dtrange(timeco[0],timeco[len(timeco)-1],timewarp)
    dataout = []
    timecoout = []
    for idata,data in enumerate(data):
        if (iscounted[idata] == False):
            tempco2 = tempco + (timeco[idata] - timeco[0])

            #coordinates of data taken into account for this timestamp
            tempcosel = cosel(timeco,tempco2)

            dataout.append(mean(data[tempcosel]))
            timecoout.append(timeco[idata])
            #dataout.append(mean(scisel(data,timeco,tempco2) )
            iscounted[tempcosel] = True
    return(array(dataout),array(timecoout))    
    


# select data

