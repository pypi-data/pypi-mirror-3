
def mergedata(x):
    x1 = x[0]
    x2 = x[1]
    xout = zeros((len(x1)+len(x2))) 
    for ix1,ex1 in enumerate(x1):
        xout[ix1] = ex1
    for ix2,ex2 in enumerate(x2):
        xout[ix2+len(x1)] = ex2

    return xout

