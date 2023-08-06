import os;
from datetime import date;
import time;

def stringToDate(theDate, date_format):
    dateStr = time.strptime(theDate, date_format)
    return date(dateStr.tm_year, dateStr.tm_mon, dateStr.tm_mday)

def addMonthsToDate(theDate, duration):

    yyyy = theDate.year
    mm = theDate.month + duration
    while (mm > 12):
        mm = mm - 12
        yyyy = yyyy + 1
        
    return date(yyyy, mm, 1)

def median(alist):
    
    srtd = sorted(alist) # returns a sorted copy
    mid = len(alist)/2   # remember that integer division truncates
    
    if len(alist) % 2 == 0:  # take the avg of middle two
        return (srtd[mid-1] + srtd[mid]) / 2.0
    else:
        return srtd[mid]
