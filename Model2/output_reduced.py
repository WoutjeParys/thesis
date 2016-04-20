__author__ = 'avanstip'

import os
import time

import xlwt
from pandas import pivot_table, merge, ExcelWriter, DataFrame
import pandas as pd
import prettyplotlib as ppl
import matplotlib.pyplot as plt
import numpy as np

from gams_addon import gdx_to_df, DomainInfo

file = 'results\out_db_75.6_50.gdx'
gdx_file = os.path.join(os.getcwd(), '%s' % file)
writer = ExcelWriter('%s.xlsx' % file)
# writer = ExcelWriter('WIR-50.xlsx')
storage = True

detailed = False

overview = True
generation_pattern = True
reserves_pattern = False
storage_pattern = False
energy_plot = False
hp_gen_ex = False


# db = gams_db_import('../results/eem_2015_2014/case03/31_RES40_RM00_LSH8760/mcp_model_case03_strategic_reserves.gdx')
# db = gams_db_import('test.gdx')

print gdx_file
zone_dict = dict()
cz = gdx_to_df(gdx_file, 'C_Z')
# print cz.head()
# print cz
# print cz.head()
# print cz.index
for idx in cz.index:
    print idx, cz.loc[idx, 'C_Z'], type(cz.loc[idx, 'C_Z'])
    if cz.loc[idx, 'C_Z'] == '':
        zone_dict[idx[1]] = idx[0]
# print zone_dict

zone_dict['BEL_Z'] = 'BEL'

if overview:
    # Overview sheet, bundling the most important results
    print 'Creating overview sheet generation'
    print 'Retrieving cap'
    cap = gdx_to_df(gdx_file, 'cap')
    old_index = cap.index.names
    cap['C'] = [zone_dict[z] for z in cap.index.get_level_values('Z')]
    cap.set_index('C', append=True, inplace=True)
    cap = cap.reorder_levels(['C'] + old_index)
    cap = pivot_table(cap.reset_index(), 'cap', index=['C', 'Y'], columns=['G'], aggfunc=np.sum)
    # print cap
    cap.insert(0, 'VAR', 'cap')
    cap.insert(0, 'R', '-')
    # print cap
    cap = cap.reset_index().set_index(['VAR', 'C', 'Y', 'R']).sort_index()
    # print cap

    print 'Retrieving gen'
    gen = gdx_to_df(gdx_file, 'gen')
    old_index = gen.index.names
    gen['C'] = [zone_dict[z] for z in gen.index.get_level_values('Z')]
    gen.set_index('C', append=True, inplace=True)
    gen = gen.reorder_levels(['C'] + old_index)
    gen = pivot_table(gen.reset_index(), 'gen', index=['C', 'Y'], columns=['G'], aggfunc=np.sum)
    # print gen.head()
    cap.loc[('gen', 'BEL', 2050, '-'), :] = gen.sum()
    cap.sort_index(inplace=True)
    # print cap

    print 'Retrieving curt'
    curt = gdx_to_df(gdx_file, 'curt')
    old_index = curt.index.names
    curt['C'] = [zone_dict[z] for z in curt.index.get_level_values('Z')]
    curt.set_index('C', append=True, inplace=True)
    curt = curt.reorder_levels(['C'] + old_index)
    curt = pivot_table(curt.reset_index(), 'curt', index=['C', 'Y'], columns=['GRI'], aggfunc=np.sum)
    # print curt.head()
    # TODO convert NaN to zero
    cap.loc[('curt', 'BEL', 2050, '-'), :] = curt.sum()
    cap.sort_index(inplace=True)
    # print cap

    print 'Retrieving res_g'
    res_g = gdx_to_df(gdx_file, 'res_g')
    old_index = res_g.index.names
    res_g['C'] = [zone_dict[z] for z in res_g.index.get_level_values('Z')]
    res_g.set_index('C', append=True, inplace=True)
    res_g = res_g.reorder_levels(['C'] + old_index)
    print res_g
    res_g = pivot_table(res_g.reset_index(), 'res_g', index=['C', 'Y', 'R'], columns=['G'], aggfunc=np.sum)
    # print res_g.head()
    for idx in res_g.index:
        cap.loc[('res_g',) + idx, :] = res_g.ix[idx]
    cap.sort_index(inplace=True)

    # print cap.head(10)

    print 'Writing overview sheet generation to Excel'
    cap.to_excel(writer, na_rep=0.0, sheet_name='overview gen', merge_cells=False)

    if storage:
        print 'Creating overview sheet storage'
        print 'Retrieving e_cap'
        stor = gdx_to_df(gdx_file, 'e_cap')
        old_index = stor.index.names
        stor['C'] = [zone_dict[z] for z in stor.index.get_level_values('Z')]
        stor.set_index('C', append=True, inplace=True)
        stor = stor.reorder_levels(['C'] + old_index)
        stor = pivot_table(stor.reset_index(), 'e_cap', index=['C', 'Y'], columns=['S'], aggfunc=np.sum)
        stor.insert(0, 'VAR', 'e_cap')
        stor.insert(0, 'R', '-')
        stor = stor.reset_index().set_index(['VAR', 'C', 'Y', 'R']).sort_index()
        # print stor.head()

        print 'Retrieving p_cap_c'
        p_cap_c = gdx_to_df(gdx_file, 'p_cap_c')
        old_index = p_cap_c.index.names
        p_cap_c['C'] = [zone_dict[z] for z in p_cap_c.index.get_level_values('Z')]
        p_cap_c.set_index('C', append=True, inplace=True)
        p_cap_c = p_cap_c.reorder_levels(['C'] + old_index)
        p_cap_c = pivot_table(p_cap_c.reset_index(), 'p_cap_c', index=['C', 'Y'], columns=['S'], aggfunc=np.sum)
        # print p_cap_c.head()
        stor.loc[('p_cap_c', 'BEL', 2050, '-'), :] = p_cap_c.sum()
        stor.sort_index(inplace=True)
        # print stor.head()

        print 'Retrieving p_cap_d'
        p_cap_d = gdx_to_df(gdx_file, 'p_cap_d')
        old_index = p_cap_d.index.names
        p_cap_d['C'] = [zone_dict[z] for z in p_cap_d.index.get_level_values('Z')]
        p_cap_d.set_index('C', append=True, inplace=True)
        p_cap_d = p_cap_d.reorder_levels(['C'] + old_index)
        p_cap_d = pivot_table(p_cap_d.reset_index(), 'p_cap_d', index=['C', 'Y'], columns=['SM'], aggfunc=np.sum)
        # print p_cap_d.head()
        stor.loc[('p_cap_d', 'BEL', 2050, '-'), :] = p_cap_d.sum()
        stor.sort_index(inplace=True)
        # print stor.head()

        print 'Retrieving p_c'
        p_c = gdx_to_df(gdx_file, 'p_c')
        old_index = p_c.index.names
        p_c['C'] = [zone_dict[z] for z in p_c.index.get_level_values('Z')]
        p_c.set_index('C', append=True, inplace=True)
        p_c = p_c.reorder_levels(['C'] + old_index)
        p_c = pivot_table(p_c.reset_index(), 'p_c', index=['C', 'Y'], columns=['S'], aggfunc=np.sum)
        # print p_c.head()
        stor.loc[('p_c', 'BEL', 2050, '-'), :] = p_c.sum()
        stor.sort_index(inplace=True)
        # print cap

        print 'Retrieving p_d'
        p_d = gdx_to_df(gdx_file, 'p_d')
        old_index = p_d.index.names
        p_d['C'] = [zone_dict[z] for z in p_d.index.get_level_values('Z')]
        p_d.set_index('C', append=True, inplace=True)
        p_d = p_d.reorder_levels(['C'] + old_index)
        p_d = pivot_table(p_d.reset_index(), 'p_d', index=['C', 'Y'], columns=['S'], aggfunc=np.sum)
        # print p_c.head()
        stor.loc[('p_d', 'BEL', 2050, '-'), :] = p_c.sum()
        stor.sort_index(inplace=True)
        # print cap

        print 'Retrieving res_s'
        res_s = gdx_to_df(gdx_file, 'res_s')
        old_index = res_s.index.names
        res_s['C'] = [zone_dict[z] for z in res_s.index.get_level_values('Z')]
        print res_s
        res_s.set_index('C', append=True, inplace=True)
        res_s = res_s.reorder_levels(['C'] + old_index)
        res_s = pivot_table(res_s.reset_index(), 'res_s', index=['C', 'Y', 'R'], columns=['S'], aggfunc=np.sum)
        # print res_g.head()
        print res_s
        for idx in res_s.index:
            stor.loc[('res_s',) + idx, :] = res_s.ix[idx]
        # print stor.head(10)
        stor.sort_index(inplace=True)
        # print stor.head(10)

        print 'Writing overview sheet storage to Excel'
        stor.to_excel(writer, na_rep=0.0, sheet_name='overview stor', merge_cells=False)

    print 'Done overview sheet(s)'
    # ------------------------------------------------------------------------------------------------------------------#

if generation_pattern:
    # GENERATION AND CURTAILMENT AND STORAGE SHARES
    print 'Creating pattern analysis'
    print 'Retrieving gen'
    gen = gdx_to_df(gdx_file, 'gen')
    old_index = gen.index.names
    gen['C'] = [zone_dict[z] for z in gen.index.get_level_values('Z')]
    gen.set_index('C', append=True, inplace=True)
    gen = gen.reorder_levels(['C'] + old_index)
    gen.reset_index(inplace=True)
    gen = pivot_table(gen, 'gen', index=['C', 'Y', 'P', 'T'], columns=['G'], aggfunc=np.sum)
    # print gen.head()

    print 'Retrieving curt'
    curt = gdx_to_df(gdx_file, 'curt')
    old_index = curt.index.names
    curt['C'] = [zone_dict[z] for z in curt.index.get_level_values('Z')]
    curt.set_index('C', append=True, inplace=True)
    curt = curt.reorder_levels(['C'] + old_index)
    curt.reset_index(inplace=True)
    curt = pivot_table(curt, 'curt', index=['C', 'Y', 'P', 'T'], columns=['GRI'], aggfunc=np.sum)
    # print curt.head()

    # First Merge
    gencurt = merge(gen, curt, left_index=True, right_index=True, how='outer', suffixes=['', '_curt'])

    if storage:
        print 'Retrieving p_c'
        p_c = gdx_to_df(gdx_file, 'p_c')
        # print p_c.head()
        old_index = p_c.index.names
        p_c['C'] = [zone_dict[z] for z in p_c.index.get_level_values('Z')]
        p_c.set_index('C', append=True, inplace=True)
        p_c = p_c.reorder_levels(['C'] + old_index)

        p_c.reset_index(inplace=True)
        p_c = pivot_table(p_c, 'p_c', index=['C', 'Y', 'P', 'T'], columns=['S'], aggfunc=np.sum)
        # TODO invert sign p_c

        # Second Merge
        gencurtc = merge(gencurt, p_c, left_index=True, right_index=True, how='outer')

        print 'Retrieving p_d'
        p_d = gdx_to_df(gdx_file, 'p_d')
        # print p_d.head()
        old_index = p_d.index.names
        p_d['C'] = [zone_dict[z] for z in p_d.index.get_level_values('Z')]
        p_d.set_index('C', append=True, inplace=True)
        p_d = p_d.reorder_levels(['C'] + old_index)

        p_d.reset_index(inplace=True)
        p_d = pivot_table(p_d, 'p_d', index=['C', 'Y', 'P', 'T'], columns=['S'], aggfunc=np.sum)
        # print p_d['STOR'].head()

        # Third Merge
        gencurtcd = merge(gencurtc, p_d, left_index=True, right_index=True, how='outer', suffixes=['_c', '_d'])

        print 'Writing pattern to Excel'
        gencurtcd.to_excel(writer, na_rep=0.0, sheet_name='pattern', merge_cells=False)

        print 'Retrieving e'
        e = gdx_to_df(gdx_file, 'e')
        # print p_d.head()
        old_index = e.index.names
        e['C'] = [zone_dict[z] for z in e.index.get_level_values('Z')]
        e.set_index('C', append=True, inplace=True)
        e = e.reorder_levels(['C'] + old_index)

        e.reset_index(inplace=True)
        e = pivot_table(e, 'e', index=['C', 'Y', 'P'], columns=['S'], aggfunc=np.sum)


        print 'Retrieving eg'
        eg = gdx_to_df(gdx_file, 'eg')
        e['gas'] = e[e.columns[0]] * np.nan
        for idx in eg.index:
            e.loc[(idx[2],idx[0],idx[1]), 'gas'] = eg.loc[idx, 'eg']

        print 'Writing energy periodic pattern to Excel'
        e.to_excel(writer, na_rep=0.0, sheet_name='ene_p', merge_cells=False)

        print 'Retrieving e_f'
        e_f = gdx_to_df(gdx_file, 'e_f')
        # print e_f.head()
        old_index = e_f.index.names
        e_f['C'] = [zone_dict[z] for z in e_f.index.get_level_values('Z')]
        e_f.set_index('C', append=True, inplace=True)
        e_f = e_f.reorder_levels(['C'] + old_index)

        e_f.reset_index(inplace=True)
        e_f = pivot_table(e_f, 'e_f', index=['C', 'Y', 'P', 'T'], columns=['S'], aggfunc=np.sum)

        print 'Retrieving eg_f'
        eg_f = gdx_to_df(gdx_file, 'eg_f')
        e_f['gas_f'] = e_f[e_f.columns[0]] * np.nan
        for idx in eg_f.index:
            e_f.loc[(idx[3],idx[0],idx[1],idx[2]), 'gas_f'] = eg_f.loc[idx, 'eg_f']

        print 'Retrieving e_l'
        e_l = gdx_to_df(gdx_file, 'e_l')
        # print e_l.head()
        old_index = e_l.index.names
        e_l['C'] = [zone_dict[z] for z in e_l.index.get_level_values('Z')]
        e_l.set_index('C', append=True, inplace=True)
        e_l = e_l.reorder_levels(['C'] + old_index)

        e_l.reset_index(inplace=True)
        e_l = pivot_table(e_l, 'e_l', index=['C', 'Y', 'P', 'T'], columns=['S'], aggfunc=np.sum)

        # First Merge
        efel = merge(e_f, e_l, left_index=True, right_index=True, how='outer', suffixes=['_f', '_l'])

        print 'Retrieving eg_l'
        eg_l = gdx_to_df(gdx_file, 'eg_l')
        efel['gas_l'] = efel[efel.columns[0]] * np.nan
        for idx in eg_l.index:
            efel.loc[(idx[3],idx[0],idx[1],idx[2]), 'gas_l'] = eg_l.loc[idx, 'eg_l']
        #print efel.head()

        print 'Writing energy temporal pattern to Excel'
        efel.to_excel(writer, na_rep=0.0, sheet_name='ene_t', merge_cells=False)

    else:
        print 'Writing pattern to Excel'
        gencurt.to_excel(writer, na_rep=0.0, sheet_name='pattern', merge_cells=False)
    print 'Done generation pattern'
    # ------------------------------------------------------------------------------------------------------------------#

if reserves_pattern:
    # FCR UPWARDS
    print 'Creating Reserve Pattern Analysis'
    print 'Retrieving res_g'
    res_g = gdx_to_df(gdx_file, 'res_g')
    old_index = res_g.index.names
    res_g['C'] = [zone_dict[z] for z in res_g.index.get_level_values('Z')]
    res_g.set_index('C', append=True, inplace=True)
    res_g = res_g.reorder_levels(['C'] + old_index)
    res_g.reset_index(inplace=True)
    res_g = pivot_table(res_g, 'res_g', index=['C', 'Y', 'P', 'T'], columns=['R', 'G'], aggfunc=np.sum)
    # print res_g.head()

    print 'Writing reserve pattern generation to Excel'
    res_g.to_excel(writer, na_rep=0.0, sheet_name='res_g', merge_cells=True)

    if detailed:
        print 'Retrieving res_g_s'
        res_g_s = gdx_to_df(gdx_file, 'res_g_s')
        old_index = res_g_s.index.names
        res_g_s['C'] = [zone_dict[z] for z in res_g_s.index.get_level_values('Z')]
        res_g_s.set_index('C', append=True, inplace=True)
        res_g_s = res_g_s.reorder_levels(['C'] + old_index)
        res_g_s.reset_index(inplace=True)
        res_g_s = pivot_table(res_g_s, 'res_g_s', index=['C', 'Y', 'P', 'T'], columns=['R', 'GD'], aggfunc=np.sum)
        # print res_g.head()

        print 'Writing res_g_s to Excel'
        res_g_s.to_excel(writer, na_rep=0.0, sheet_name='res_g_s', merge_cells=True)

        print 'Retrieving res_g_ns'
        res_g_ns = gdx_to_df(gdx_file, 'res_g_ns')
        old_index = res_g_ns.index.names
        res_g_ns['C'] = [zone_dict[z] for z in res_g_ns.index.get_level_values('Z')]
        res_g_ns.set_index('C', append=True, inplace=True)
        res_g_ns = res_g_ns.reorder_levels(['C'] + old_index)
        res_g_ns.reset_index(inplace=True)
        res_g_ns = pivot_table(res_g_ns, 'res_g_ns', index=['C', 'Y', 'P', 'T'], columns=['RU', 'GD'], aggfunc=np.sum)
        # print res_g.head()

        print 'Writing res_g_ns to Excel'
        res_g_ns.to_excel(writer, na_rep=0.0, sheet_name='res_g_ns', merge_cells=True)

        print 'Retrieving res_g_sd'
        res_g_sd = gdx_to_df(gdx_file, 'res_g_sd')
        old_index = res_g_sd.index.names
        res_g_sd['C'] = [zone_dict[z] for z in res_g_sd.index.get_level_values('Z')]
        res_g_sd.set_index('C', append=True, inplace=True)
        res_g_sd = res_g_sd.reorder_levels(['C'] + old_index)
        res_g_sd.reset_index(inplace=True)
        res_g_sd = pivot_table(res_g_sd, 'res_g_sd', index=['C', 'Y', 'P', 'T'], columns=['RD', 'GD'], aggfunc=np.sum)
        # print res_g.head()

        print 'Writing res_g_sd to Excel'
        res_g_sd.to_excel(writer, na_rep=0.0, sheet_name='res_g_sd', merge_cells=True)

    if storage:
        print 'Retrieving res_s'
        res_s = gdx_to_df(gdx_file, 'res_s')
        old_index = res_s.index.names
        res_s['C'] = [zone_dict[z] for z in res_s.index.get_level_values('Z')]
        res_s.set_index('C', append=True, inplace=True)
        res_s = res_s.reorder_levels(['C'] + old_index)
        res_s.reset_index(inplace=True)
        res_s = pivot_table(res_s, 'res_s', index=['C', 'Y', 'P', 'T'], columns=['R', 'S'], aggfunc=np.sum)
        # print res_s.head()

        print 'Writing reserve pattern storage to Excel'
        res_s.to_excel(writer, na_rep=0.0, sheet_name='res_s', merge_cells=True)
        # ------------------------------------------------------------------------------------------------------------------#

if storage_pattern:
    print 'Creating storage behaviour analysis'
    # Charging behaviour
    res_up_mfrr_c = gdx_to_df(gdx_file, 'res_up_mfrr_c')
    print 'Done retrieving res_up_mfrr_c'
    old_index = res_up_mfrr_c.index.names
    res_up_mfrr_c['C'] = [zone_dict[z] for z in res_up_mfrr_c.index.get_level_values('Z')]
    res_up_mfrr_c.set_index('C', append=True, inplace=True)
    res_up_mfrr_c = res_up_mfrr_c.reorder_levels(['C'] + old_index)

    res_up_mfrr_c.reset_index(inplace=True)
    res_up_mfrr_c = pivot_table(res_up_mfrr_c, 'res_up_mfrr_c', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_up_mfrr_c.head()

    res_up_afrr_c = gdx_to_df(gdx_file, 'res_up_afrr_c')
    print 'Done retrieving res_up_afrr_c'
    old_index = res_up_afrr_c.index.names
    res_up_afrr_c['C'] = [zone_dict[z] for z in res_up_afrr_c.index.get_level_values('Z')]
    res_up_afrr_c.set_index('C', append=True, inplace=True)
    res_up_afrr_c = res_up_afrr_c.reorder_levels(['C'] + old_index)

    res_up_afrr_c.reset_index(inplace=True)
    res_up_afrr_c = pivot_table(res_up_afrr_c, 'res_up_afrr_c', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_up_afrr_c.head()

    # First Merge
    stor = merge(res_up_mfrr_c, res_up_afrr_c, left_index=True, right_index=True, how='outer',
                 suffixes=['_up_mfrr', '_up_afrr'])
    # print stor.head()

    p_c = gdx_to_df(gdx_file, 'p_c')
    print 'Done retrieving p_c'
    # print p_c.head()
    old_index = p_c.index.names
    p_c['C'] = [zone_dict[z] for z in p_c.index.get_level_values('Z')]
    p_c.set_index('C', append=True, inplace=True)
    p_c = p_c.reorder_levels(['C'] + old_index)

    p_c.reset_index(inplace=True)
    p_c = pivot_table(p_c, 'p_c', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print p_c['STOR'].head()

    stor['p_c'] = p_c['STOR'] - stor['STOR_up_afrr'] - stor['STOR_up_mfrr']
    # print stor.head()

    p_cap = gdx_to_df(gdx_file, 'p_cap')
    print 'Done retrieving p_cap'
    # print p_cap['p_cap']
    # print p_cap.iloc[0]['p_cap']

    res_dn_afrr_c = gdx_to_df(gdx_file, 'res_dn_afrr_c')
    print 'Done retrieving res_dn_afrr_c'
    old_index = res_dn_afrr_c.index.names
    res_dn_afrr_c['C'] = [zone_dict[z] for z in res_dn_afrr_c.index.get_level_values('Z')]
    res_dn_afrr_c.set_index('C', append=True, inplace=True)
    res_dn_afrr_c = res_dn_afrr_c.reorder_levels(['C'] + old_index)

    res_dn_afrr_c.reset_index(inplace=True)
    res_dn_afrr_c = pivot_table(res_dn_afrr_c, 'res_dn_afrr_c', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_dn_afrr_c.head()

    res_dn_mfrr_c = gdx_to_df(gdx_file, 'res_dn_mfrr_c')
    print 'Done retrieving res_dn_mfrr_c'
    old_index = res_dn_mfrr_c.index.names
    res_dn_mfrr_c['C'] = [zone_dict[z] for z in res_dn_mfrr_c.index.get_level_values('Z')]
    res_dn_mfrr_c.set_index('C', append=True, inplace=True)
    res_dn_mfrr_c = res_dn_mfrr_c.reorder_levels(['C'] + old_index)

    res_dn_mfrr_c.reset_index(inplace=True)
    res_dn_mfrr_c = pivot_table(res_dn_mfrr_c, 'res_dn_mfrr_c', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_dn_mfrr_c.head()

    stor['margin'] = p_cap.iloc[0]['p_cap'] - p_c['STOR'] - res_dn_afrr_c['STOR'] - res_dn_mfrr_c['STOR']
    # print stor.head()

    # Second Merge
    stor = merge(stor, res_dn_afrr_c, left_index=True, right_index=True, how='outer')

    # Third Merge
    stor = merge(stor, res_dn_mfrr_c, left_index=True, right_index=True, how='outer', suffixes=['_dn_afrr', '_dn_mfrr'])

    stor.to_excel(writer, na_rep=0.0, sheet_name='charging', merge_cells=False)
    print 'Done charging behaviour'
    # ------------------------------------------------------------------------------------------------------------------#

    # Discharging behaviour
    # Charging behaviour
    res_dn_mfrr_d = gdx_to_df(gdx_file, 'res_dn_mfrr_d')
    print 'Done retrieving res_dn_mfrr_d'
    old_index = res_dn_mfrr_d.index.names
    res_dn_mfrr_d['C'] = [zone_dict[z] for z in res_dn_mfrr_d.index.get_level_values('Z')]
    res_dn_mfrr_d.set_index('C', append=True, inplace=True)
    res_dn_mfrr_d = res_dn_mfrr_d.reorder_levels(['C'] + old_index)

    res_dn_mfrr_d.reset_index(inplace=True)
    res_dn_mfrr_d = pivot_table(res_dn_mfrr_d, 'res_dn_mfrr_d', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_dn_mfrr_d.head()

    res_dn_afrr_d = gdx_to_df(gdx_file, 'res_dn_afrr_d')
    print 'Done retrieving res_dn_afrr_d'
    old_index = res_dn_afrr_d.index.names
    res_dn_afrr_d['C'] = [zone_dict[z] for z in res_dn_afrr_d.index.get_level_values('Z')]
    res_dn_afrr_d.set_index('C', append=True, inplace=True)
    res_dn_afrr_d = res_dn_afrr_d.reorder_levels(['C'] + old_index)

    res_dn_afrr_d.reset_index(inplace=True)
    res_dn_afrr_d = pivot_table(res_dn_afrr_d, 'res_dn_afrr_d', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_dn_afrr_d.head()

    # First Merge
    stor = merge(res_dn_mfrr_d, res_dn_afrr_d, left_index=True, right_index=True, how='outer',
                 suffixes=['_dn_mfrr', '_dn_afrr'])
    # print stor.head()

    p_d = gdx_to_df(gdx_file, 'p_d')
    print 'Done retrieving p_d'
    # print p_d.head()
    old_index = p_d.index.names
    p_d['C'] = [zone_dict[z] for z in p_d.index.get_level_values('Z')]
    p_d.set_index('C', append=True, inplace=True)
    p_d = p_d.reorder_levels(['C'] + old_index)

    p_d.reset_index(inplace=True)
    p_d = pivot_table(p_d, 'p_d', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print p_c['STOR'].head()

    stor['p_d'] = p_d['STOR'] - stor['STOR_dn_afrr'] - stor['STOR_dn_mfrr']
    # print stor.head()

    p_cap = gdx_to_df(gdx_file, 'p_cap')
    print 'Done retrieving p_cap'
    # print p_cap['p_cap']
    # print p_cap.iloc[0]['p_cap']

    res_up_afrr_d = gdx_to_df(gdx_file, 'res_up_afrr_d')
    print 'Done retrieving res_up_afrr_d'
    old_index = res_up_afrr_d.index.names
    res_up_afrr_d['C'] = [zone_dict[z] for z in res_up_afrr_d.index.get_level_values('Z')]
    res_up_afrr_d.set_index('C', append=True, inplace=True)
    res_up_afrr_d = res_up_afrr_d.reorder_levels(['C'] + old_index)

    res_up_afrr_d.reset_index(inplace=True)
    res_up_afrr_d = pivot_table(res_up_afrr_d, 'res_up_afrr_d', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_dn_afrr_c.head()

    res_up_mfrr_d = gdx_to_df(gdx_file, 'res_up_mfrr_d')
    print 'Done retrieving res_up_mfrr_d'
    old_index = res_up_mfrr_d.index.names
    res_up_mfrr_d['C'] = [zone_dict[z] for z in res_up_mfrr_d.index.get_level_values('Z')]
    res_up_mfrr_d.set_index('C', append=True, inplace=True)
    res_up_mfrr_d = res_up_mfrr_d.reorder_levels(['C'] + old_index)

    res_up_mfrr_d.reset_index(inplace=True)
    res_up_mfrr_d = pivot_table(res_up_mfrr_d, 'res_up_mfrr_d', index=['C', 'Y', 'T'], columns=['S'], aggfunc=np.sum)
    # print res_up_mfrr_d.head()

    stor['margin'] = p_cap.iloc[0]['p_cap'] - p_d['STOR'] - res_up_afrr_d['STOR'] - res_up_mfrr_d['STOR']
    # print stor.head()

    # Second Merge
    stor = merge(stor, res_up_afrr_d, left_index=True, right_index=True, how='outer')

    # Third Merge
    stor = merge(stor, res_up_mfrr_d, left_index=True, right_index=True, how='outer', suffixes=['_up_afrr', '_up_mfrr'])

    stor.to_excel(writer, na_rep=0.0, sheet_name='discharging', merge_cells=False)
    print 'Done discharging behaviour'

if energy_plot:
    ene = gdx_to_df(gdx_file, 'e')
    # ene = gdx_to_df(gdx_file, 'p_d')
    # print ene.head()
    # print ene.tail()
    data = np.array(ene.query('Type=="L"'))
    data = np.vstack((data, [data[0]]))
    data = data / data.max()
    # print type(data), len(data)
    # print data

    B = np.reshape(data, (-1, 24))
    # print B

    img = plt.imshow(data, aspect=24 / 365.)
    img.set_cmap('winter')
    x = np.arange(len(ene.query('Type=="L"')))
    # print len(x), len(ene.query('Type=="L"'))
    # plt.fill_between(x, np.array(ene.query('Type=="L"'))[0])
    plt.colorbar()
    plt.grid()
    plt.show()
    # exit()

if hp_gen_ex:
    gen = gdx_to_df(gdx_file, 'gen')

    # print gen.query('Type=="L" and  G=="Coal"').head(110)
    # print gen.count()
    # print gen.query('gen > 0').count()

    ppl.plot(gen.query('Type=="L" and  G=="Coal"'), drawstyle='steps')
    ppl.plot(gen.query('Type=="L" and  G=="Nuclear"'), drawstyle='steps')
    plt.savefig('awesome.pdf')
    plt.show()

    df_new = gen.reset_index()
    # print df_new.head(10)
    table_prod = pivot_table(df_new.query('Type=="L"'), 'gen', columns=['G'], index=['Y', 'T'], aggfunc=np.sum)
    table_prod = pivot_table(df_new.query('Type=="L" and (Z >= 1000 and Z <2000)'), 'gen', columns=['G'],
                             index=['Y', 'T'], aggfunc=np.sum)
    # print table_prod
    table_prod.to_csv('out.csv')

    gen = gdx_to_df(gdx_file, 'DEM_T')
    # print gen.head(10)
    ppl.plot(gen.query('Z_ALL=="BEL_Z"'), drawstyle='steps')
    plt.show()


# exit()
# c_energy_market_lambda = db_to_df(db, 'c_energy_market_lambda', 'eqn', value='m')
# lmd = db_to_df(db, 'lambda', 'var')
#
# ppl.plot(c_energy_market_lambda['c_energy_market_lambda'], drawstyle='steps')
# ppl.plot(lmd['lambda'], drawstyle='steps')
# plt.show()
#
# df_DEMAND = db_to_df(db, 'DEMAND', 'param')
# ppl.plot(df_DEMAND['DEMAND'], label='DEMAND')
#
# df_stor_cons = db_to_df(db, 'stor_cons', 'var')
# df_stor_cons.reset_index(inplace=True)
# table_stor = pivot_table(df_stor_cons, 'stor_cons', rows=['y', 'h'], cols=['f'])
#
# df_stor_prod = db_to_df(db, 'stor_prod', 'var')
# df_stor_prod.reset_index(inplace=True)
# table_prod = pivot_table(df_stor_prod, 'stor_prod', rows=['y', 'h'], cols=['f'])
# data = np.array(df_DEMAND['DEMAND']) + np.array(table_stor.sum(axis=1)) - np.array(table_prod.sum(axis=1)[:])
# ppl.plot(data, label='DEMAND+Storage')
#
# df_gen_gen = db_to_df(db, 'gen_gen', 'var')
# df_gen_gen.reset_index(inplace=True)
# table_gen = pivot_table(df_gen_gen, 'gen_gen', rows=['y', 'h'], cols=['f'])
# print table_gen.head()
# data = data * 0
# x = np.arange(0, len(data))
# for col in table_gen.columns:
# if table_gen[col].sum() != 0:
# ppl.fill_between(x, data + np.array(table_gen[col]), data, label=col)
# data = data + np.array(table_gen[col])
#
# df_res_gen = db_to_df(db, 'res_gen', 'var')
# df_res_gen.reset_index(inplace=True)
# table_res = pivot_table(df_res_gen, 'res_gen', rows=['y', 'h'], cols=['f', 'j'])
# print table_res.head()
#
# x = np.arange(0, len(data))
# for col in table_res.columns:
# if table_res[col].sum() != 0:
# ppl.fill_between(x, data + np.array(table_res[col]), data, label=col)
# data = data + np.array(table_res[col])
#
# df_sr = db_to_df(db, 'gen_sr', 'var')
# ppl.fill_between(x, data + np.array(df_sr['gen_sr']), data, label=col)
# data = data + np.array(df_sr['gen_sr'])
#
# df_ls = db_to_df(db, 'ls', 'var')
# ppl.fill_between(x, data + np.array(df_ls['ls']), data, label=col)
# data = data + np.array(df_ls['ls'])
#
# df_alpha = db_to_df(db, 'lambda', 'var')
# ppl.plot(df_alpha['lambda'] / 42 * 365 * 4)
#
# ppl.legend()
# plt.grid()
# plt.xlim((0, 1008))
# plt.ylim((0, 15000))
# plt.show()

print 'Writing to Excel'
writer.save()
print 'Done %s' % file
