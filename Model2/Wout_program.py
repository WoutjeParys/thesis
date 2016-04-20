__author__ = 'Wout'

#import some usefull things
import os
from pandas import pivot_table, merge, ExcelWriter, DataFrame
import numpy as np
from openpyxl import Workbook
from openpyxl import load_workbook
from gams_addon import gdx_to_df, DomainInfo
from openpyxl.styles import Style, Border, Alignment, Protection, Font, colors
import sqlite3 as sq
import csv
import xlrd
import os
from matplotlib import pyplot as plt
import Wout_initialise
import Wout_main


file = 'results\out_db_75.6_50.gdx'
gdx_file = os.path.join(os.getcwd(), '%s' % file)
writefile = os.getcwd() + '\\' + 'excel\output_elasticity_model_tempory.xlsx'

length_period = 168
amount_of_periods = 1

def balance_m_to_excel():
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
            factors.append((p,h,1))
            print (p,' & ', h)
    cur.executemany('INSERT INTO Factor VALUES (?,?,?)', factors)
    conn.commit()
    ############################################

# Reset factor to 1
# reset_factor_to_one()
# set balance_price to flat price
#Wout_initialise.initialise(length_period)


for i in range (0,1):
    Wout_main.main(length_period)
    # balance_m_to_excel()
    # balance_m_to_sqlite()






