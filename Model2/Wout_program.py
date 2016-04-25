__author__ = 'Wout'

#import some usefull things
import os
from pandas import pivot_table, merge, ExcelWriter, DataFrame
import numpy as np
import openpyxl
from gams_addon import gdx_to_df, DomainInfo
from openpyxl.styles import Style, Border, Alignment, Protection, Font, colors
import sqlite3 as sq
import csv
import xlrd
import os
import math
from matplotlib import pyplot as plt
import Wout_initialise
import Wout_main



file = 'results\out_db_75.6_50.gdx'
gdx_file = os.path.join(os.getcwd(), '%s' % file)
sh_shift_name = 'shifting'
excel_shift_name = 'excel\output_elasticity_model_shifting.xlsx'
list_compensation = list()

#length period needs to be a multiple of 24
length_period = 24*7
amount_of_periods = 3

#write marginal values of balance function to excel
def balance_m_to_excel():
    writefile = os.getcwd() + '\\' + 'excel\output_elasticity_model_tempory.xlsx'

    writer = ExcelWriter(writefile)
    print gdx_file
    zone_dict = dict()
    zone_dict['BEL_Z'] = 'BEL'

    print 'get balance'
    print 'retrieving marg'
    marg = gdx_to_df(gdx_file, 'marg')
    old_index = marg.index.names
    marg['C'] = [zone_dict[z] for z in marg.index.get_level_values('Z')]
    marg.set_index('C', append=True, inplace=True)
    marg = marg.reorder_levels(['C'] + old_index)
    marg.reset_index(inplace=True)
    marg = pivot_table(marg, 'marg', index=['P', 'T', 'Z'], columns=['C'], aggfunc=np.sum)

    print 'Writing balances.m to Excel'
    marg.to_excel(writer, na_rep=0.0, sheet_name='balance', merge_cells=False)
    writer.close()

#write marginal values of balance function from excel to sqlite
def balance_m_to_sqlite():
    print os.getcwd()
    conn = sq.connect("database/database.sqlite")
    cur = conn.cursor()

    print os.getcwd()

    book = xlrd.open_workbook(os.path.join(os.getcwd() , "excel\output_elasticity_model_tempory.xlsx"))
    sh = book.sheet_by_index(0)
    sql = 'DROP TABLE IF EXISTS Marketprices;'
    cur.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS Marketprices (Period TEXT, Hour TEXT, Zone Text, Price FLOAT);'
    cur.execute(sql)
    prices = list()
    for row in range(1, sh.nrows):
        period = int(sh.cell_value(row, 0))
        hour = int(sh.cell_value(row,1))
        zone = sh.cell_value(row,2)
        #if zone in zones:
        price = sh.cell_value(row, 3)
        #print period, hour, zone, price
        prices.append((period,hour,zone,price))
    cur.executemany('INSERT INTO Marketprices VALUES (?,?,?,?)', prices)
    conn.commit()

    print 'done marketprices'

#reset compensation factor for inbalances in elasticities (to 1)
def reset_factor_to_one():
    print os.getcwd()
    conn = sq.connect("database/database.sqlite")
    cur = conn.cursor()

    print os.getcwd()
    sql = 'DROP TABLE IF EXISTS Factor;'
    cur.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS Factor (Period TEXT, Hour TEXT, Value FLOAT);'
    # ,  PRIMARY KEY(Code));'
    cur.execute(sql)
    factors = list()
    for p in range(1,amount_of_periods+1):
        for h in range(1,length_period+1):
            factors.append((p,h,1.0))
            # print (p,' & ', h)
    cur.executemany('INSERT INTO Factor VALUES (?,?,?)', factors)
    conn.commit()

    for i in range(1,amount_of_periods+1):
        list_compensation.append(1)

    ############################################

#reset compensation factor for inbalances in elasticities (to 1)
def reset_factor_to_value(value):
    print os.getcwd()
    conn = sq.connect("database/database.sqlite")
    cur = conn.cursor()

    print os.getcwd()
    sql = 'DROP TABLE IF EXISTS Factor;'
    cur.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS Factor (Period TEXT, Hour TEXT, Value FLOAT);'
    # ,  PRIMARY KEY(Code));'
    cur.execute(sql)
    factors = list()
    for p in range(1,amount_of_periods+1):
        for h in range(1,length_period+1):
            factors.append((p,h,value))
            # print (p,' & ', h)
    cur.executemany('INSERT INTO Factor VALUES (?,?,?)', factors)
    conn.commit()

    for i in range(1,amount_of_periods+1):
        list_compensation.append(value)

    ############################################

#set compensation factor for inbalances to a chosen value
def set_factor_to_value():
    print os.getcwd()
    conn = sq.connect("database/database.sqlite")
    cur = conn.cursor()

    print os.getcwd()
    sql = 'DROP TABLE IF EXISTS Factor;'
    cur.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS Factor (Period TEXT, Hour TEXT, Value FLOAT);'
    # ,  PRIMARY KEY(Code));'
    cur.execute(sql)
    factors = list()
    for p in range(1,amount_of_periods+1):
        for h in range(1,length_period+1):
            factors.append((p,h,list_compensation[p-1]))
            # print (p,' & ', h)
    cur.executemany('INSERT INTO Factor VALUES (?,?,?)', factors)
    conn.commit()
    ############################################

#update parameter to adjust cross elasticities
def update_factor_values():
    writer = ExcelWriter(writefile)
    print gdx_file
    zone_dict = dict()
    zone_dict['BEL_Z'] = 'BEL'

    print 'get compensation'
    print 'retrieving factor'
    factor = gdx_to_df(gdx_file, 'factor')
    old_index = factor.index.names
    factor['C'] = [zone_dict[z] for z in factor.index.get_level_values('Z')]
    factor.set_index('C', append=True, inplace=True)
    factor = factor.reorder_levels(['C'] + old_index)
    factor.reset_index(inplace=True)
    factor = pivot_table(factor, 'factor', index=['P', 'H', 'Z'], columns=['C'], aggfunc=np.sum)
    print 'Writing factor to Excel'
    factor.to_excel(writer, na_rep=0.0, sheet_name='factor', merge_cells=False)
    writer.close()

    print os.getcwd()
    conn = sq.connect("database/database.sqlite")
    cur = conn.cursor()

    print os.getcwd()

    book = xlrd.open_workbook(os.path.join(os.getcwd() , "excel\output_elasticity_model_tempory.xlsx"))
    sh = book.sheet_by_index(0)
    sql = 'DROP TABLE IF EXISTS Factor;'
    cur.execute(sql)
    sql = 'CREATE TABLE IF NOT EXISTS Factor (Period TEXT, Hour TEXT, Value FLOAT);'
    cur.execute(sql)
    factors = list()
    for row in range(1, sh.nrows):
        period = int(sh.cell_value(row, 0))
        hour = int(sh.cell_value(row,1))
        factor = sh.cell_value(row, 3)
        print period, hour, factor
        factors.append((period,hour,factor))
    cur.executemany('INSERT INTO Factor VALUES (?,?,?)', factors)
    conn.commit()

#write shift forward, backward & away to excel
def shift_to_excel():
    writefile = os.getcwd() + '\\' + excel_shift_name
    writer = ExcelWriter(writefile)
    print gdx_file
    zone_dict = dict()
    zone_dict['BEL_Z'] = 'BEL'

    print 'Retrieving shiftaway'
    shiftaway = gdx_to_df(gdx_file, 'shiftaway')
    old_index = shiftaway.index.names
    shiftaway['C'] = [zone_dict[z] for z in shiftaway.index.get_level_values('Z')]
    shiftaway.set_index('C', append=True, inplace=True)
    shiftaway = shiftaway.reorder_levels(['C'] + old_index)
    shiftaway.reset_index(inplace=True)
    shiftaway = pivot_table(shiftaway, 'shiftaway', index=['P','H','Z'], columns=['C'], aggfunc=np.sum)


    print 'Retrieving shiftforward'
    shiftforward = gdx_to_df(gdx_file, 'shiftforwards')
    old_index = shiftforward.index.names
    shiftforward['C'] = [zone_dict[z] for z in shiftforward.index.get_level_values('Z')]
    shiftforward.set_index('C', append=True, inplace=True)
    shiftforward = shiftforward.reorder_levels(['C'] + old_index)
    shiftforward.reset_index(inplace=True)
    shiftforward = pivot_table(shiftforward, 'shiftforwards', index=['P','H','Z'], columns=['C'], aggfunc=np.sum)

    print 'Retrieving shiftbackward'
    shiftbackward = gdx_to_df(gdx_file, 'shiftbackwards')
    old_index = shiftbackward.index.names
    shiftbackward['C'] = [zone_dict[z] for z in shiftbackward.index.get_level_values('Z')]
    shiftbackward.set_index('C', append=True, inplace=True)
    shiftbackward = shiftbackward.reorder_levels(['C'] + old_index)
    shiftbackward.reset_index(inplace=True)
    shiftbackward = pivot_table(shiftbackward, 'shiftbackwards', index=['P','H','Z'], columns=['C'], aggfunc=np.sum)

    # First Merge
    shift = merge(shiftforward, shiftbackward, left_index=True, right_index=True, how='outer', suffixes=['_forward', '_backward'])
    shift = merge(shift, shiftaway, left_index=True, right_index=True, how='outer', suffixes=['', '_away'])

    print 'Writing demand and prices to Excel'
    shift.to_excel(writer, na_rep=0.0, sheet_name=sh_shift_name, merge_cells=False)

    writer.close()

#calculate the compensation factor for each period
def calculate_comp_factor():
    print 'open shifting excel file'
    wbread = openpyxl.load_workbook(excel_shift_name)
    print 'shifting file loaded'
    sheet = wbread.get_sheet_by_name(sh_shift_name)
    print list_compensation
    for i in range(1,amount_of_periods+1):
        forward = 0
        backward = 0
        away = 0
        for j in range(2,length_period+2):
            # print ('j: ', j)
            forward = forward + abs(sheet.cell(row = (i-1)*length_period+j,column = 4).value)
            backward = backward + abs(sheet.cell(row = (i-1)*length_period+j,column = 5).value)
            away = away + abs(sheet.cell(row = (i-1)*length_period+j,column = 6).value)
        print forward
        print backward
        print away
        compensate = away/(forward+backward)
        print 'compensate: ',compensate
        list_compensation[i-1] = list_compensation[i-1]*math.sqrt(compensate)
        print 'compensate new value: ', list_compensation[i-1]

# Reset factor (to compensate the inbalances in the cross elasticities) to 1
# reset_factor_to_one()
reset_factor_to_value(1.38)
# set balance_price to flat price
# Wout_initialise.initialise(length_period)

output = list()

output.append(list(list_compensation))
for i in range (0,1):
    # Wout_main.main(length_period)
    # balance_m_to_excel()
    # balance_m_to_sqlite()
    # shift_to_excel()
    calculate_comp_factor()
    set_factor_to_value()
    #
    output.append(list(list_compensation))

print output






