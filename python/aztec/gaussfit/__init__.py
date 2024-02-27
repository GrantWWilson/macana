from aztec import *

def gaussian2d ((x,y), c0, c1, x0,y0, sx, sy, theta):
    x = npy.array(x)
    y = npy.array(y)
    xp = (x-x0)*npy.cos(theta) - (y-y0)*npy.sin(theta)
    yp = (x-x0)*npy.sin(theta) + (y-y0)*npy.cos(theta)
    expn = (xp/sx)**2.0 + (yp/sy)**2.0
    ff = c0 + c1*npy.exp(-0.5*expn)
    return ff

def fitgaussian2d (data, x,y):
    from scipy.optimize import curve_fit
    
    xx, yy = npy.meshgrid(x,y)
    xx = xx.transpose()
    yy = yy.transpose()
    iguess = [0.0, npy.max(data), 0.0, 0.0, 6.0/3600.0, 6.0/3600.0, 0.0]
    try:
        popt, pcov = curve_fit(gaussian2d,(xx.ravel(),yy.ravel()), data.ravel(), p0 = iguess)
        return True,popt
    except Exception, err:
        print "Warning, this was a really bad fit: ", str(err)
        return False,-1.0*npy.ones(len(iguess))