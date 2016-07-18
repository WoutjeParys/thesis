__author__ = 'Wout'

import os

from pandas import pivot_table, merge, ExcelWriter, DataFrame
import numpy as np
from gams_addon import gdx_to_df, DomainInfo

res_target = 50
costs = [0,25,50,75,100,125,150,175,200,225,250,275,300,325,350,375,400,425,450]
weight = [13.0357,13.0357,13.0357,13.0357]
totweight = sum(weight)
print totweight
hours_period = 168
startvalue = costs.pop(0)
print startvalue
type = '_cost_'

writefile = os.getcwd() + '\\' + 'excel' + '\\' + 'DemR' + '\\' + 'results\Overview_fullweek' + type + str(res_target) +'.xlsx'
writer = ExcelWriter(writefile)

file = 'results' + '\\' + '4weeksDRcost\out_db_' + str(res_target) + type + str(startvalue)
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
    # print curt.index.names
    for i in curt.index:
        value = float(curt.get_value(i,'curt'))*weight[i[2]-1]
        curt.set_value(i,'curt',value)
    curt.reset_index(inplace=True)
    curt = pivot_table(curt, 'curt', index=['Y'], columns=['C'], aggfunc=np.sum)
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
    # print old_index
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
    # print old_index
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
    # print old_index
    res_DR['C'] = [resDR[z] for z in res_DR.index.get_level_values('Z')]
    res_DR.set_index('C', append=True, inplace=True)
    res_DR = res_DR.reorder_levels(['C'] + old_index)
    for i in res_DR.index:
        value = float(res_DR.get_value(i,'res_DR'))
        res_DR.set_value(i,'res_DR',value)
    res_DR = pivot_table(res_DR.reset_index(), 'res_DR', index=['Y','R'], columns=['C'],aggfunc=np.sum)
    return res_DR

def retrieving_gen():
    gen = gdx_to_df(gdx_file, 'gen')
    old_index = gen.index.names
    gen['C'] = [zone_dict[z] for z in gen.index.get_level_values('Z')]
    gen.set_index('C', append=True, inplace=True)
    gen = gen.reorder_levels(['C'] + old_index)
    for i in gen.index:
        value = float(gen.get_value(i,'gen'))*weight[i[2]-1]
        gen.set_value(i,'gen',value)
    gen.reset_index(inplace=True)
    gen = pivot_table(gen, 'gen', index=['Y', 'G'], columns=['C'], aggfunc=np.sum)
    return gen

def retrieving_shift():
    ref = gdx_to_df(gdx_file, 'DEM_RES_FP')
    new = gdx_to_df(gdx_file, 'demand_new_res')
    old_indexr = ref.index.names
    old_indexn = new.index.names
    ref['C'] = [zone_dict[z] for z in ref.index.get_level_values('Z')]
    new['C'] = [zone_dict[z] for z in new.index.get_level_values('Z')]
    ref.set_index('C', append=True, inplace=True)
    new.set_index('C', append=True, inplace=True)
    ref = ref.reorder_levels(['C'] + old_indexr)
    new = new.reorder_levels(['C'] + old_indexn)
    shiftedtot=0
    for i in ref.index:
        value1 = float(ref.get_value(i,'DEM_RES_FP'))*weight[i[1]-1]
        value2 = float(new.get_value((i[0],i[1],i[2],i[3],'L'),'demand_new_res'))*weight[i[1]-1]
        # shifted = (value1-value2)/2
        # shifted = abs(shifted)
        if value1>value2:
            shifted = value1-value2
        else:
            shifted=0
        # print value1,value2,shifted
        ref.set_value(i,'DEM_RES_FP',shifted)
        shiftedtot = shiftedtot + shifted
    ref.reset_index(inplace=True)
    new.reset_index(inplace=True)
    shift = pivot_table(ref, 'DEM_RES_FP', index=['Z'], columns=['C'], aggfunc=np.sum)
    # print shiftedtot
    return shift

def retrieving_max_shift():
    ref = gdx_to_df(gdx_file, 'DEM_RES_FP')
    new = gdx_to_df(gdx_file, 'demand_new_res')
    old_indexr = ref.index.names
    old_indexn = new.index.names
    ref['C'] = [zone_dict[z] for z in ref.index.get_level_values('Z')]
    new['C'] = [zone_dict[z] for z in new.index.get_level_values('Z')]
    ref.set_index('C', append=True, inplace=True)
    new.set_index('C', append=True, inplace=True)
    ref = ref.reorder_levels(['C'] + old_indexr)
    new = new.reorder_levels(['C'] + old_indexn)
    shiftedtot=0
    for i in ref.index:
        value1 = float(ref.get_value(i,'DEM_RES_FP'))
        value2 = float(new.get_value((i[0],i[1],i[2],i[3],'L'),'demand_new_res'))
        shifted = (value1-value2)
        # shifted = abs(shifted)
        # print value1,value2,shifted
        ref.set_value(i,'DEM_RES_FP',shifted)
        shiftedtot = shiftedtot + shifted
    ref.reset_index(inplace=True)
    new.reset_index(inplace=True)
    maxshift = pivot_table(ref, 'DEM_RES_FP', index=['Z'], columns=['C'], aggfunc=np.max)
    # print shiftedtot
    return maxshift

def retrieving_demand():
    new = gdx_to_df(gdx_file, 'demand_unit')
    old_index = new.index.names
    new['C'] = [zone_dict[z] for z in new.index.get_level_values('Z')]
    new.set_index('C', append=True, inplace=True)
    new = new.reorder_levels(['C'] + old_index)
    print new.index.names
    for i in new.index:
        value = float(new.get_value(i,'demand_unit'))*weight[i[1]-1]
        new.set_value(i,'demand_unit',value)
    new.reset_index(inplace=True)
    new = pivot_table(new, 'demand_unit', index=['Z'], columns=['C'], aggfunc=np.sum)
    # print shiftedtot
    return new

def retrieving_stor_c():
    storc = gdx_to_df(gdx_file, 'p_c')
    old_index = storc.index.names
    storc['C'] = [zone_dict[z] for z in storc.index.get_level_values('Z')]
    storc.set_index('C', append=True, inplace=True)
    storc = storc.reorder_levels(['C'] + old_index)
    for i in storc.index:
        value = float(storc.get_value(i,'p_c'))*weight[i[2]-1]
        storc.set_value(i,'p_c',value)
    storc.reset_index(inplace=True)
    storc = pivot_table(storc, 'p_c', index=['Y'], columns=['C'], aggfunc=np.sum)
    return storc

def retrieving_stor_d():
    stord = gdx_to_df(gdx_file, 'p_d')
    old_index = stord.index.names
    stord['C'] = [zone_dict[z] for z in stord.index.get_level_values('Z')]
    stord.set_index('C', append=True, inplace=True)
    stord = stord.reorder_levels(['C'] + old_index)
    for i in stord.index:
        value = float(stord.get_value(i,'p_d'))*weight[i[2]-1]
        stord.set_value(i,'p_d',value)
    stord.reset_index(inplace=True)
    stord = pivot_table(stord, 'p_d', index=['Y'], columns=['C'], aggfunc=np.sum)
    return stord

def retrieving_cdr_cost():
    costcDR = gdx_to_df(gdx_file, 'costcDR')
    old_index = costcDR.index.names
    costcDR['C'] = [zone_dict[z] for z in costcDR.index.get_level_values('Z')]
    costcDR.set_index('C', append=True, inplace=True)
    costcDR = costcDR.reorder_levels(['C'] + old_index)
    costcDR.reset_index(inplace=True)
    costcDR = pivot_table(costcDR, 'costcDR', index=['Z'], columns=['C'], aggfunc=np.sum)
    return costcDR

def retrieving_edr_cost():
    costgDR = gdx_to_df(gdx_file, 'costgDR')
    old_index = costgDR.index.names
    costgDR['C'] = [zone_dict[z] for z in costgDR.index.get_level_values('Z')]
    costgDR.set_index('C', append=True, inplace=True)
    costgDR = costgDR.reorder_levels(['C'] + old_index)
    costgDR.reset_index(inplace=True)
    costgDR = pivot_table(costgDR, 'costgDR', index=['Z'], columns=['C'], aggfunc=np.sum)
    return costgDR




restot=retrieving_res_g()
restot=merge(restot,retrieving_res_s(), left_index=True, right_index=True, how='outer')
restot=merge(restot,retrieving_res_DR(), left_index=True, right_index=True, how='outer')

shifttot = retrieving_shift()
maxshifttot = retrieving_max_shift()

gentot=retrieving_gen()
captot=retrieving_cap()
curttot=retrieving_curt()
stortot=retrieving_stor_cap_c()
demtot=retrieving_demand()

cstortot=retrieving_stor_c()
dstortot=retrieving_stor_d()

cdrtot = retrieving_cdr_cost()
edrtot = retrieving_edr_cost()


# print targets
# # for i in []:
for i in costs:
    file = 'results' + '\\' + '4weeksDRcost\out_db_' + str(res_target) + type + str(i)
    gdx_file = os.path.join(os.getcwd(), '%s' % file)
    print gdx_file

    restot=merge(restot,retrieving_res_g(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    restot=merge(restot,retrieving_res_s(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    restot=merge(restot,retrieving_res_DR(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

    gentot = merge(gentot,retrieving_gen(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    demtot = merge(demtot,retrieving_demand(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    captot = merge(captot,retrieving_cap(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    stortot = merge(stortot,retrieving_stor_cap_c(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    curttot = merge(curttot,retrieving_curt(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    shifttot = merge(shifttot,retrieving_shift(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    maxshifttot = merge(maxshifttot,retrieving_max_shift(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

    cstortot = merge(cstortot,retrieving_stor_c(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    dstortot = merge(dstortot,retrieving_stor_d(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

    cdrtot = merge(cdrtot,retrieving_cdr_cost(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])
    edrtot = merge(edrtot,retrieving_edr_cost(), left_index=True, right_index=True, how='outer',suffixes=['',str(i)])

print captot
print curttot
print stortot
print restot
print gentot
print shifttot
print maxshifttot
print demtot
print edrtot
print cdrtot
restot.to_excel(writer, na_rep=0.0, sheet_name='reserves', merge_cells=False)
captot.to_excel(writer, na_rep=0.0, sheet_name='capacities', merge_cells=False)
stortot.to_excel(writer, na_rep=0.0, sheet_name='storage', merge_cells=False)
gentot.to_excel(writer, na_rep=0.0, sheet_name='generation', merge_cells=False)
shifttot.to_excel(writer, na_rep=0.0, sheet_name='demandshift', merge_cells=False)
curttot.to_excel(writer, na_rep=0.0, sheet_name='curtailment', merge_cells=False)
cstortot.to_excel(writer, na_rep=0.0, sheet_name='storc', merge_cells=False)
dstortot.to_excel(writer, na_rep=0.0, sheet_name='stordisc', merge_cells=False)
maxshifttot.to_excel(writer, na_rep=0.0, sheet_name='maxshift', merge_cells=False)
cdrtot.to_excel(writer, na_rep=0.0, sheet_name='cap_DR', merge_cells=False)
edrtot.to_excel(writer, na_rep=0.0, sheet_name='en_DR', merge_cells=False)

writer.close()

# x = [1,2,3,4,5]
# print x
# y = x.pop(0)
# print y
# print x
