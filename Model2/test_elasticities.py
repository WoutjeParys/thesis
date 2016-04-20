__author__ = 'Wout'

import sqlite3 as sq
import csv
import xlrd
import os

#choose winter-spring-summer-autumn
season = 4
#choose weekday (1) or weekend (2)
day = 2

if day==1:
    offset=0
else:
    offset=4

delta_price = 0.2

bookelast = xlrd.open_workbook(os.path.join(os.getcwd() , "excel\Elasticity.xlsx"))
bookdem = xlrd.open_workbook(os.path.join(os.getcwd(), "excel\Testdemand.xlsx"))
shelast = bookelast.sheet_by_index(offset+season-1)
shdem = bookdem.sheet_by_index(season-1)
dembefore = 0
demafter = 0
elasticity = list()
for row in range(0,24):
    dem1 = shdem.cell_value(row, 1)
    dembefore = dembefore+dem1
    print dem1
    print '---------'
    for col in range(1,shelast.ncols):
        elast = shelast.cell_value(row+3, col)
        dem1 = dem1 + dem1*elast*delta_price
    print dem1
    demafter = demafter+dem1
    print '======================'
print 'the total demand before the price change:'
print dembefore
print 'the total demand after the price change:'
print demafter
print 'percentage change:'
print (demafter/dembefore-1)*100