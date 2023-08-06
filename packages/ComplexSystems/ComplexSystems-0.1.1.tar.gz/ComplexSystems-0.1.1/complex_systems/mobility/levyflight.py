#!/usr/bin/env python 

""""
Copyright 2010-2011 Vincent Gauthier
Email: vincent.gauthier@telecom-sudparis.eu
"""

import numpy as np
import pylab as plt
import scipy as sp

##############################
#
# Variables 
#
##############################

alpha = 3
xmax = 100
ymax = 100

##############################
#
# Fucntions 
#
##############################

def nextPoint(prev,alpha,xymax):
    """Draw a new step in the levy flight
    
    Args:
        prev: Tulpe (x,y)
            The previous position of a node
        alpha: float > 0
            Shape of the pareto distribution 
        xymax : Tulpe (x,y)
            boundary of the simulation area
    Returns:
        next: Tulpe (x,y) 
    """
    if alpha < 0:
        raise ValueError('alpha < 0') 
    xmax, ymax = xymax
    next = (-1,-1)
    x,y = prev
    while not(next[0] < xmax and next[0] > 0 and next[1] < ymax and next[1] > 0):
        theta = np.random.uniform(0,(2*np.pi),1)
        distance = np.random.pareto(alpha,1)
        next = (x + distance*np.cos(theta), y + distance * np.sin(theta))
    return next, float(distance)

##############################
#
# Main 
#
##############################

def main():
    """Main function"""
    x0,y0 = 50,50
    xdata = []
    ydata = []
    lengthdistribution = []
    for i in xrange(5000):
        xdata.append(x0)
        ydata.append(y0)
        (x0,y0),l = nextPoint((x0,y0),alpha,(100,100))
        lengthdistribution.append(l)
    plt.figure(1)
    plt.plot(xdata,ydata)
    plt.show()


if __name__ == "__main__":
    main()