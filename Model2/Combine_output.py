__author__ = 'Wout'

import os

from pandas import pivot_table, merge, ExcelWriter, DataFrame
import numpy as np
from gams_addon import gdx_to_df, DomainInfo

startvalue = 10
type = '_DRres0_5'

writefile = os.getcwd() + '\\' + 'excel' + '\\' + 'DemR' + '\\' + 'results\Overview_fullweek' + type +'.xlsx'
writer = ExcelWriter(writefile)

file = 'results\8weeksFull\out_db_' + str(startvalue) + type
gdx_file = os.path.join(os.getcwd(), '%s' % file)
print gdx_file

zone_dict = dict()
zone_dict['BEL_Z'] = 'BEL'

storage = dict()
storage['BEL_Z'] = 'storage'

resgen = dict()
resgen['BEL_Z'] = 'generation'

resDR = dict()
resDR['BEL_Z'] = 'DR'

curtail = dict()
curtail['BEL_Z'] = 'curt'

def retrieving_cap():
    cap = gdx_to_df(gdx_file, 'cap')
    old_index = cap.index.names
    cap['C'] = [zone_dict[z] for z in cap.index.get_level_values('Z')]
    cap.set_index('C', append=True, inplace=True)
    cap = cap.reorder_levels(['C'] + old_index)
    cap.reset_index(inplace=True)
    cap = pivot_table(cap, 'cap', index=['Y', 'Z', 'G'], columns=['C'], aggfunc=np.sum)
    return cap

def retrieving_curt():
    curt = gdx_to_df(gdx_file, 'curt')
    old_index = curt.index.names
    curt['C'] = [curtail[z] for z in curt.index.get_level_values('Z')]
    curt.set_index('C', append=True, inplace=True)
    curt = curt.reorder_levels(['C'] + old_index)
    for i in curt.index:
        value = float(curt.get_value(i,'curt'))
        curt.set_value(i,'curt',value)
    curt.reset_index(inplace=True)
    curt = pivot_table(curt, 'curt', index=['Y', 'GRI'], columns=['C'], aggfunc=np.sum)
    return curt

def retrieving_stor_cap_c():
    stor = gdx_to_df(gdx_file, 'p_cap_c')
    old_index = stor.index.names
    stor['C'] = [zone_dict[z] for z in stor.index.get_level_values('Z')]
    stor.set_index('C', append=True, inplace=True)
    stor = stor.reorder_levels(['C'] + old_index)
    stor = pivot_table(stor.reset_index(), 'p_cap_c', index=['Y','Z','S'], columns=['C'], aggfunc=np.sum)
    return stor

def retrieving_res_s():
    res_s = gdx_to_df(gdx_file, 'res_s')
    old_index = res_s.index.names
    print old_index
    res_s['C'] = [storage[z] for z in res_s.index.get_level_values('Z')]
    res_s.set_index('C', append=True, inplace=True)
    res_s = res_s.reorder_levels(['C'] + old_index)
    for i in res_s.index:
        value = float(res_s.get_value(i,'res_s'))
        res_s.set_value(i,'res_s',value)
    res_s = pivot_table(res_s.reset_index(), 'res_s', index=['Y','R'], columns=['C'], aggfunc=np.sum)
    return res_s

def retrieving_res_g():
    res_g = gdx_to_df(gdx_file, 'res_g')
    old_index = res_g.index.names
    print old_index
    res_g['C'] = [resgen[z] for z in res_g.index.get_level_values('Z')]
    res_g.set_index('C', append=True, inplace=True)
    res_g = res_g.reorder_levels(['C'] + old_index)
    for i in res_g.index:
        value = float(res_g.get_value(i,'res_g'))
        res_g.set_value(i,'res_g',value)
    res_g = pivot_table(res_g.reset_index(), 'res_g', index=['Y','R'], columns=['C'],aggfunc=np.sum)
    return res_g

def retrieving_res_DR():
    res_DR = gdx_to_df(gdx_file, 'res_DR')
    old_index = res_DR.index.names
    print old_index
    res_DR['C'] = [resDR[z] for z in res_DR.index.get_level_values('Z')]
    res_DR.set_index('C', append=True, inplace=True)
    res_DR = res_DR.reorder_levels(['C'] + old_index)
    for i in res_DR.index:
        value = float(res_DR.get_value(i,'res_DR'))
        res_DR.set_value(i,'res_DR',value)
    res_DR = pivot_table(res_DR.reset_index(), 'res_DR', index=['Y','R'], columns=['C'],aggfunc=np.sum)
    return res_DR

captot=retrieving_cap()
curttot=retrieving_curt()
stortot=retrieving_stor_cap_c()

restot=retrieving_res_g()
restot=merge(restot,retrieving_res_s(), left_index=True, right_index=True, how='outer')
restot=merge(restot,retrieving_res_DR(), left_index=True, right_index=True, how='outer')

for i in [30,50,70]:
    file = 'results\8weeksFull\out_db_' + str(i) + type
    gdx_file = os.path.join(os.getcwd(), '%s' % file)
    print gdx_file

    cap=retrieving_cap()
    curt=retrieving_curt()
    stor=retrieving_stor_cap_c()

    restot=merge(restot,retrieving_res_g(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    restot=merge(restot,retrieving_res_s(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    restot=merge(restot,retrieving_res_DR(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

    captot = merge(captot,cap, left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    stortot = merge(stortot,stor, left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    curttot = merge(curttot,curt, left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

print captot
print curttot
print stortot
print restot
restot.to_excel(writer, na_rep=0.0, sheet_name='reserves', merge_cells=False)
captot.to_excel(writer, na_rep=0.0, sheet_name='capacities', merge_cells=False)
curttot.to_excel(writer, na_rep=0.0, sheet_name='curtailment', merge_cells=False)
stortot.to_excel(writer, na_rep=0.0, sheet_name='storage', merge_cells=False)
writer.close()
