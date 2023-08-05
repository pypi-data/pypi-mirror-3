#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Feb  7 11:53:29 2011
@author: sat kumar tomer (http://civil.iisc.ernet.in/~satkumar/)

functions:
    EarthDistance: calculate earth distance in AU
    sun_rise_set:  calculate sunrise and sunset time
"""

import datetime as dt
import time
from math import pi
import numpy as np
from math import cos, sin
from numpy import mod, arcsin, arccos

def EarthDistance(dn):
    """
    module to calculate the earth distance in AU
    
    Input:
        dn:    julian day
    
    Output:
        D:     distance of earth to sun in AU
    """
    thetaD = 2*pi*dn/365
    a0 = 1.000110; a1 = 0.034221; b1 = 0.001280; 
    a2 = 0.000719; b2 = 0.000077;
    D = np.sqrt(a0+a1*cos(thetaD)+b1*cos(thetaD)+a2*cos(2*thetaD)+b2*cos(2*thetaD));
    return D

def sun_rise_set(dn):
    """
    module to calculate the earth distance in AU
    
    Input:
        dn:    julian day
    
    Output:
        D:     distance of earth to sun in AU
    """
    thetaD = 2*pi*dn/365
    a0 = 1.000110; a1 = 0.034221; b1 = 0.001280; 
    a2 = 0.000719; b2 = 0.000077;
    D = np.sqrt(a0+a1*cos(thetaD)+b1*cos(thetaD)+a2*cos(2*thetaD)+b2*cos(2*thetaD));
    return D

def sun_rise_set(day,month,year,lw=-76.44,ln=11.95):
    """
    module to calculate the sunset and sunrise time
    
    Input:
        day:    day of the month (0-31)
        month:  month
        year:   year
        lw:     longitude (west positive)
        ln:     latitude (north positive)
    
    Output:
        Trise:     sunrise time in GMT+5.5
        Tset:      sunset time in GMT+5.5
        
    """
    
    Jdate = dt.date(year,month,day).toordinal()-dt.date(2000,1,1).toordinal() + 2451545
    n_star = (Jdate - 2451545 - 0.0009) - (lw/360.0)
    n = round(n_star)
    J_star = 2451545 + 0.0009 + (lw/360.0) + n
    
    M = mod(357.5291 + 0.98560028 * (J_star - 2451545), 360.0)
    C = (1.9148 * sin(M*pi/180)) + (0.0200 * sin(2 * M*pi/180)) + (0.0003 * sin(3 * M*pi/180))
    
    #Now, using C and M, calculate the ecliptical longitude of the sun.
    lam = mod(M + 102.9372 + C + 180,360)
    
    #Now there is enough data to calculate an accurate Julian date for solar noon.
    Jtransit = J_star + (0.0053 * sin(M*pi/180)) - (0.0069 * sin(2 * lam*pi/180))
    
    #To calculate the hour angle we need to find the declination of the sun
    delta = arcsin( sin(lam*pi/180) * sin(23.45*pi/180) )*180/pi
    
    #Now, calculate the hour angle, which corresponds to half of the arc length of 
    #the sun at this latitude at this declination of the sun
    H = arccos((sin(-0.83*pi/180) - sin(ln*pi/180) * sin(delta*pi/180)) / (cos(ln*pi/180) * cos(delta*pi/180)))*180/pi
    
    #Note: If H is undefined, then there is either no sunrise (in winter) or no sunset (in summer) for the supplied latitude.
    #Okay, time to go back through the approximation again, this time we use H in the calculation
    
    J_star_star = 2451545 + 0.0009 + ((H + lw)/360) + n
    #The values of M and λ from above don't really change from solar noon to sunset, so there is no need to recalculate them before calculating sunset.
    Jset = J_star_star + (0.0053 * sin(M*pi/180)) - (0.0069 * sin(2 * lam*pi/180))
    
    #Instead of going through that mess again, assume that solar noon is half-way between sunrise and sunset (valid for latitudes < 60) and approximate sunrise.
    Jrise = Jtransit - (Jset - Jtransit)
    
    Trise = mod(Jrise,1)*24+5.5-12
    
    Tset = mod(Jset,1)*24+5.5+12
    
    return Trise, Tset 
