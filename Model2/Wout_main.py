__author__ = 'Wout'

import numpy as np
import matplotlib.pyplot as plt
import gams
import os, sys
import glob
from shutil import move
import sqlite3 as sq
import sqlite3 as sq

# length_period = 168

folder = 'gams'

file = '../gams/LinearModel_Wout_comp.gms'

def main(length_period):
    # 1. Setup Gams Workspace
    # ws = gams.GamsWorkspace(working_directory=os.getcwd(), debug=gams.DebugLevel.ShowLog)
    print os.getcwd() + '\gams'
    ws = gams.GamsWorkspace(working_directory=os.path.join(os.getcwd() , 'run'), debug=gams.DebugLevel.ShowLog)
    # 2. Initialize Job
    job = ws.add_job_from_file('%s' % file)
    opt = ws.add_options()

    db = ws.add_database()
    cp = ws.add_checkpoint()

    opt.defines["SupplyDataFileName"] = db.name
    opt.threads = 0
    # opt.defines["F"] = "12"

    #===============================================================================
    # 5. Define and add Sets, Parameters,...
    RCZ = db.add_set('RCZ', 1, 'All geographical entities (R_ALL + C_ALL + Z_ALL)')
    R_ALL = db.add_set_dc('R_ALL', RCZ, 'All Regions (i.e. W-EU & E-EU $ North and Baltic Sea)')
    C_ALL = db.add_set_dc('C_ALL', RCZ, 'All Countries')
    Z_ALL = db.add_set_dc('Z_ALL', RCZ, 'All Zones')
    R_C = db.add_set_dc('R_C' , (R_ALL, C_ALL), 'Countries in regions')
    C_Z = db.add_set_dc('C_Z' , (C_ALL, Z_ALL), 'Zones in countries')
    # R = db.add_set_dc('R', R_ALL, 'Regions in the simulation')
    C = db.add_set_dc('C', C_ALL, 'Countries in the simulation')
    Z = db.add_set_dc('Z', Z_ALL, 'Zones in the simulation')

    Y_ALL = db.add_set('Y_ALL', 1, 'All years')
    Y = db.add_set_dc('Y', Y_ALL, 'Years in the simulation')
    P = db.add_set('P', 1, 'Time periods')
    T = db.add_set('T', 1, 'Time steps within periods')
    H = db.add_set('H',1,'All hours')

    G = db.add_set('G', 1, 'All generation technologies')
    GD = db.add_set_dc('GD', G, 'Dispatchable generation technologies')
    GC = db.add_set_dc('GC', G, 'Conventional generation technologies')
    GCG = db.add_set_dc('GCG', GC, 'Gas-fueled conventional generation technologies')
    GCO = db.add_set_dc('GCO', GC, 'Other conventional generation technologies')
    GR = db.add_set_dc('GR', G, 'Renewable generation technologies')
    GRI = db.add_set_dc('GRI', GR, 'Intermittent renewable generation technologies')
    GRD = db.add_set_dc('GRD', GR, 'Dispatchable renewable generation technologies')
    G_PARAM = db.add_set('G_PARAM', 1, 'Generation technology parameters')

    S = db.add_set('S', 1, 'All storage technologies')
    SSM = db.add_set_dc('SSM', S, 'Short and Mid-term storage technologies')
    SML = db.add_set_dc('SML', S, 'Mid and Long-term storage technologies')
    SS = db.add_set_dc('SS', S, 'Short-term storage technologies')
    SM = db.add_set_dc('SM', S, 'Mid-term storage technologies')
    SL = db.add_set_dc('SL', S, 'Long-term storage technologies')
    S_PARAM = db.add_set('S_PARAM', 1, 'Storage technology parameters')

    POL = db.add_set('POL', 1, 'Policy instruments')

    R = db.add_set('R', 1, 'Reserve requirements')
    RU = db.add_set_dc('RU', R, 'Upward reserve requirements')
    RD = db.add_set_dc('RD', R, 'Downward reserve requirements')
    RUA = db.add_set_dc('RUA', RU, 'FCR and aFRR upward reserve requirements')
    RUF = db.add_set_dc('RUF', RU, 'FCR upward reserve requirements')
    RDA = db.add_set_dc('RDA', RD, 'aFRR downward reserve requirements')

    MUT = db.add_set_dc('MUT', (G,T), 'Minimum up times')
    MDT = db.add_set_dc('MDT', (G,T), 'Minimum down times')

    conn = sq.connect('database/database.sqlite')
    cur = conn.cursor()

    ############################################

    sql = 'Select r.Code from Region r;'
    cur.execute(sql)
    region = cur.fetchall()
    for r in region:
        RCZ.add_record(str(r[0]))
        R_ALL.add_record(str(r[0]))

    sql = 'Select Code, Region_Code, Include from Country;'
    cur.execute(sql)
    country = cur.fetchall()
    for c in country:
        RCZ.add_record(str(c[0]))
        C_ALL.add_record(str(c[0]))
        R_C.add_record((str(c[1]), str(c[0])))
        if c[2]:
            C.add_record(str(c[0]))

    sql = 'Select Code, Country_Code from Zone;'
    cur.execute(sql)
    zone = cur.fetchall()
    for z in zone:
        RCZ.add_record(str(z[0]))
        Z_ALL.add_record(str(z[0]))
        C_Z.add_record((str(z[1]), str(z[0])))
        # print z[1], z[0]
        for c in country:
            if c[2]:
                if (c[0] == z[1]):
                    Z.add_record(str(z[0]))
                    # print z[0]

    ############################################

    for t in range(1, length_period+1):
        T.add_record('%d' % t)

    # TODO
    for h in range(1,length_period+1):
        H.add_record('%d' % h)

    sql = 'Select Year, Include from Years;'
    cur.execute(sql)
    year = cur.fetchall()
    for y in year:
        Y_ALL.add_record(str(y[0]))
        if y[1]:
            Y.add_record(str(y[0]))

    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()

    for p in range(1,len(periods)+1):
        P.add_record('%d' % p)
        # print '%d' %p

    ############################################

    sql = 'Select Code, Include, Dispatchable, RES, Gas from Generation_technologies;'
    cur.execute(sql)
    generation = cur.fetchall()
    for g in generation:
        if g[1]:    #if included
            G.add_record(str(g[0]))
            if g[2]:    #if dispatchable
                GD.add_record(str(g[0]))
            if g[3]:    #if renewable
                GR.add_record(str(g[0]))
                if g[2]:#if dispatchable
                    GRD.add_record(str(g[0]))
                else:   #if not dispatchable, i.e. intermittent
                    GRI.add_record(str(g[0]))
            else:       #if not renewable, i.e. conventional
                GC.add_record(str(g[0]))
                if g[4]:    #if gas-fired
                    GCG.add_record(str(g[0]))
                else:
                    GCO.add_record(str(g[0]))

    sql = 'Select Code from Generation_parameters;'
    cur.execute(sql)
    parameter = cur.fetchall()
    for p in parameter:
        G_PARAM.add_record(str(p[0]))

    ############################################

    sql = 'Select Code, Include, Short, Mid, Long from Storage_technologies;'
    cur.execute(sql)
    storage = cur.fetchall()
    for s in storage:
        if s[1]:    #if included
            S.add_record(str(s[0]))
            if s[2]:    #Short-term storage
                SS.add_record(str(s[0]))
                SSM.add_record(str(s[0]))
            if s[3]:    #Mid-term storage
                SM.add_record(str(s[0]))
                SSM.add_record(str(s[0]))
                SML.add_record(str(s[0]))
            if s[4]:    #Long-term storage
                SL.add_record(str(s[0]))
                SML.add_record(str(s[0]))

    sql = 'Select Code from Storage_parameters;'
    cur.execute(sql)
    parameter = cur.fetchall()
    for p in parameter:
        S_PARAM.add_record(str(p[0]))

    ############################################

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select Technology, Value from Generation_data where Parameter = "MUT";'
    cur.execute(sql)
    muts = cur.fetchall()
    # print muts
    for t in technologies:
        for m in muts:
            # print m[0], m[1]
            if m[0] in t:
                for j in range(int(m[1])):
                    # print str(m[0]), j+1
                    MUT.add_record((str(m[0]), str(j + 1)))

    sql = 'Select Technology, Value from Generation_data where Parameter = "MDT";'
    cur.execute(sql)
    mdts = cur.fetchall()
    # print mdts
    for t in technologies:
        for m in mdts:
            # print m[0], m[1]
            if m[0] in t:
                for j in range(int(m[1])):
                    # print str(m[0]), t+1
                    MDT.add_record((str(m[0]), str(j + 1)))

    ############################################

    sql = 'Select Instrument from Policy_instruments;'
    cur.execute(sql)
    instruments = cur.fetchall()
    for i in instruments:
        POL.add_record(str(i[0]))

    ############################################

    sql = 'Select Type, Include, RU, RUA, RUF, RDA from Reserves;'
    cur.execute(sql)
    reserves = cur.fetchall()
    for r in reserves:
        if r[1]:    #if included
            R.add_record(str(r[0]))
            if r[2]:    #if upward reserves
                RU.add_record(str(r[0]))
                if r[3]:    #if afrr or quicker
                    RUA.add_record(str(r[0]))
                    if r[4]:    #if fcr or quicker
                        RUF.add_record(str(r[0]))
            else:
                RD.add_record(str(r[0]))
                if r[5]:    #if afrr or quicker
                    RDA.add_record(str(r[0]))

    ############################################

    #===============================================================================

    G_DATA = db.add_parameter_dc('G_DATA', [G,G_PARAM], 'Technologies characteristics')
    S_DATA = db.add_parameter_dc('S_DATA', [S,S_PARAM], 'Storage characteristics')

    RG = db.add_parameter_dc('RG', [R,GD], 'Ramping ability per reserve category for generation technologies')
    RSC = db.add_parameter_dc('RSC', [R,SML], 'Ramping ability per reserve category for storage technologies while charging')
    RSD = db.add_parameter_dc('RSD', [R,SM], 'Ramping ability per reserve category for storage technologies while discharging')

    # C_GAS = db.add_parameter_dc('C_GAS', 1, 'Cost of imported gas')

    DEM = db.add_parameter_dc('DEM', [Y_ALL,Z_ALL], 'Energy demand per year [MWh]')
    DEM_T = db.add_parameter_dc('DEM_T', [P,T,Z_ALL], 'Relative electricity demand per hour [%]')

    RES_T = db.add_parameter_dc('RES_T', [P,T,Z_ALL,GRI], 'Intermittent generation profile [MW]')
    REL_T = db.add_parameter_dc('REL_T', [P,T,Z_ALL,GRI], 'Reliable intermittent generation profile [MW]')

    W = db.add_parameter_dc('W', [P], 'Weight of period P [-]')

    POL_TARGETS = db.add_parameter_dc('POL_TARGETS', [POL, Y_ALL], 'Policy targets for each year')

    R_EXO = db.add_parameter_dc('R_EXO', [C_ALL,R], 'Exogenous reserve requirements per country')
    R_ENDO = db.add_parameter_dc('R_ENDO', [C_ALL,GRI,R], 'Endogenous reserve requirements per country per (renewable) generation technology')

    T_R = db.add_parameter_dc('T_R', [R], 'Time factor to calculate energy for reserve provision')

    # EGCAPEX = db.add_parameter_dc('EGCAPEX', 1, 'Annualized energy investment cost of gas storage')
    # E_LP = db.add_parameter_dc('E_LP', 1, 'Energy volume of the gas line pack')

    ELAST = db.add_parameter_dc('ELAST', [P,T,H], 'Elasticity relative to hour one and hour two')
    DIAG = db.add_parameter_dc('DIAG', [T,H], 'Diagonal matrix with ones and zeros')
    TRI_UP = db.add_parameter_dc('TRI_UP', [T,H], 'Diagonal matrix with ones and zeros')
    TRI_LOW = db.add_parameter_dc('TRI_LOW', [T,H], 'Lower triangle with ones and zeros')
    SHIFTMIN = db.add_parameter_dc('SHIFTMIN', [H,T], 'matrix to constraint shifting of energy inner window')
    SHIFTMAX = db.add_parameter_dc('SHIFTMAX', [H,T], 'matrix to constraint shifting of energy outer window')
    COMPENSATE = db.add_parameter_dc('COMPENSATE', [P,H], 'a factor to multiply with the elasticity matrix to compensate energy losses')

    DEM_NON_RES = db.add_parameter_dc('DEM_NON_RES', [P,T,Z], 'amount of non residential demand')
    DEM_REF_RES = db.add_parameter_dc('DEM_REF_RES', [P,T,Z], 'amount of reference residential demand before DR')

    RATIO_H = db.add_parameter_dc('RATIO_H', [P,H], 'inbalance ratio')
    LINEARPEM = db.add_parameter_dc('LINEARPEM', [T,H], 'compensation PEM linear')
    OWNELAST = db.add_parameter_dc('OWNELAST', [T,H], 'compensation PEM elast')

    ############################################

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select Technology, Parameter, Value from Generation_data;'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        # print t
        for g in g_data:
            # print g[0]
            if g[0] in t:
                G_DATA.add_record((str(g[0]), str(g[1]))).value = g[2]
                # print g[0], g[1], g[2]

    ############################################

    sql = 'Select s.Code from Storage_technologies s where s.Include > 0;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select Technology, Parameter, Value from Storage_data;'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        # print t
        for s in s_data:
            # print s[0]
            if s[0] in t:
                S_DATA.add_record((str(s[0]), str(s[1]))).value = s[2]
                # print s[0], s[1], s[2]

    ############################################

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0 AND g.Dispatchable > 0;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "FCR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Generation_data d where d.Parameter = "RF";'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for g in g_data:
                if g[0] in t:
                    RG.add_record((str(r[0]), str(g[0]))).value = g[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "AFRR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Generation_data d where d.Parameter = "RANS";'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for g in g_data:
                if g[0] in t:
                    RG.add_record((str(r[0]), str(g[0]))).value = g[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "AFRR_DN";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Generation_data d where d.Parameter = "RA";'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for g in g_data:
                if g[0] in t:
                    RG.add_record((str(r[0]), str(g[0]))).value = g[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "MFRR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Generation_data d where d.Parameter = "RMNS";'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for g in g_data:
                if g[0] in t:
                    RG.add_record((str(r[0]), str(g[0]))).value = g[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.TYPE = "MFRR_DN";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Generation_data d where d.Parameter = "RM";'
    cur.execute(sql)
    g_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for g in g_data:
                if g[0] in t:
                    RG.add_record((str(r[0]), str(g[0]))).value = g[1]
                    # print g[0], g[1], g[2]

    ############################################

    sql = 'Select s.Code from Storage_technologies s where s.Include > 0 AND (s.Mid > 0 OR s.Long > 0);'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "FCR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RCF";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSC.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "AFRR_UP" OR r.TYPE = "AFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RCA";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSC.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "MFRR_UP" OR r.TYPE = "MFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RCM";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSC.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]

    ############################################

    sql = 'Select s.Code from Storage_technologies s where s.Include > 0 AND s.Mid > 0;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "FCR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RDF";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSD.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "AFRR_UP" OR r.TYPE = "AFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RDA";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSD.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "MFRR_UP" OR r.TYPE = "MFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    sql = 'Select d.Technology, d.Value from Storage_data d where d.Parameter = "RDM";'
    cur.execute(sql)
    s_data = cur.fetchall()
    for t in technologies:
        for r in reserves:
            for s in s_data:
                if s[0] in t:
                    RSD.add_record((str(r[0]), str(s[0]))).value = s[1]
                    # print g[0], g[1], g[2]

    ############################################

    sql = 'Select Year, Zone, Demand from Demand_energy;'
    cur.execute(sql)
    demand = cur.fetchall()

    for d in demand:
        DEM.add_record((str(d[0]), str(d[1]))).value = d[2]
        # print d[0], d[1], d[2]

    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    sql = 'Select Time, Zone, Demand from Demand_profile;'
    cur.execute(sql)
    profile = cur.fetchall()
    for per in enumerate(periods, start=1):
        # print 'per: ',per
        # print per[0],per[1][0]
        for p in range(0,length_period):
            # print str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]), profile[(int(per[1][0])-1 + p)*4][2]
            # print int(per[0]), int(per[1][0]), (int(per[1][0])-1 + p)*4, profile[(int(per[1][0])-1 + p)*4][2]
            DEM_T.add_record((str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]))).value = profile[(int(per[1][0])-1 + p)*4][2]

    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    sql = 'Select Time, Zone, Demand from Demand_non_residential;'
    cur.execute(sql)
    profile = cur.fetchall()
    for per in enumerate(periods, start=1):
        # print 'per: ',per
        # print per[0],per[1][0]
        for p in range(0,length_period):
            # print str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]), profile[(int(per[1][0])-1 + p)*4][2]
            # print int(per[0]), int(per[1][0]), (int(per[1][0])-1 + p)*4, profile[(int(per[1][0])-1 + p)*4][2]
            DEM_NON_RES.add_record((str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]))).value = profile[(int(per[1][0])-1 + p)*4][2]

    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    sql = 'Select Time, Zone, Demand from Demand_residential;'
    cur.execute(sql)
    profile = cur.fetchall()
    for per in enumerate(periods, start=1):
        # print 'per: ',per
        # print per[0],per[1][0]
        for p in range(0,length_period):
            # print str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]), profile[(int(per[1][0])-1 + p)*4][2]
            # print int(per[0]), int(per[1][0]), (int(per[1][0])-1 + p)*4, profile[(int(per[1][0])-1 + p)*4][2]
            DEM_REF_RES.add_record((str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]))).value = profile[(int(per[1][0])-1 + p)*4][2]

    ############################################

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0 AND g.RES > 0 AND g.Dispatchable < 1;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    sql = 'Select Time, Zone, Technology, Production from Intermittent_renewables;'
    cur.execute(sql)
    profile = cur.fetchall()
    for t in technologies:
        # print t
        for l in range(0,len(profile)/35040):
            # print profile[l*35040 + 3][2]
            if profile[l*35040 + 3][2] in t:
                # print 'ello'
                for per in enumerate(periods, start=1):
                    for p in range(0, length_period):
                        #print str(int(per[0])), str(p+1), str(profile[(int(per[1][0])-1 + p)*4][1]), profile[(int(per[1][0])-1 + p)*4][2]
                        #print int(per[0]), int(per[1][0]), l*35040 + (int(per[1][0])-1 + p)*4, profile[l*35040 + (int(per[1][0])-1 + p)*4][1], profile[l*35040 + (int(per[1][0])-1 + p)*4][2], profile[l*35040 + (int(per[1][0])-1 + p)*4][3]
                        RES_T.add_record((str(int(per[0])), str(p+1), str(profile[l*35040 + (int(per[1][0])-1 + p)*4][1]), str(profile[l*35040 + (int(per[1][0])-1 + p)*4][2]))).value = profile[l*35040 + (int(per[1][0])-1 + p)*4][3]

    ############################################

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0 AND g.RES > 0 AND g.Dispatchable < 1;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select First_hour from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    sql = 'Select Time, Zone, Technology, Production from Reliable_intermittent;'
    cur.execute(sql)
    profile = cur.fetchall()
    for t in technologies:
        # print len(profile)/35040
        for l in range(0,len(profile)/35040):
            # print profile[l*35040 + 3][2], profile[l*35040 + 3][1], profile[l*35040 + 3][0]
            if profile[l*35040 + 3][2] in t:
                # print 'ello'
                for per in enumerate(periods, start=1):
                    for p in range(0, length_period):
                        # print str(int(per[0])), str(p), str(profile[l*35040 + (int(per[1][0]) + p)*4 + 3][1]), str(profile[l*35040 + (int(per[1][0]) + p)*4 + 3][2]), profile[l*35040 + (int(per[1][0]) + p)*4 + 3][3]
                        # print int(per[0]), int(per[1][0]), l*35040 + (int(per[1][0])-1 + p)*4, profile[l*35040 + (int(per[1][0])-1 + p)*4][1], profile[l*35040 + (int(per[1][0])-1 + p)*4][2], profile[l*35040 + (int(per[1][0])-1 + p)*4][3]
                        REL_T.add_record((str(int(per[0])), str(p+1), str(profile[l*35040 + (int(per[1][0])-1 + p)*4][1]), str(profile[l*35040 + (int(per[1][0])-1 + p)*4][2]))).value = profile[l*35040 + (int(per[1][0])-1 + p)*4][3]

    ############################################

    sql = 'Select Weight from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    for per in enumerate(periods, start=1):
        # print per[0], per[1][0]
        W.add_record(str(int(per[0]))).value = per[1][0]

    ############################################

    sql = 'Select First_hour,Season from Time_steps;'
    cur.execute(sql)
    periods = cur.fetchall()
    print 'periods: ',periods

    sql = 'Select Season, Hour1, Hour2, Price_Elasticity from Elasticity;'
    cur.execute(sql)
    elasticities = cur.fetchall()
    count_per = 1
    for per in periods:
        print 'season: ', per[1]
        for e in elasticities:
            if e[0] == per[1]:
                ELAST.add_record((str(count_per),str(e[1]), str(e[2]))).value = e[3]
        count_per = count_per+1

    ###########################################

    sql = 'Select Hour1, Hour2, Include_Value from C_Diagonal;'
    cur.execute(sql)
    diagonal = cur.fetchall()
    for d in diagonal:
        DIAG.add_record((str(d[0]), str(d[1]))).value = d[2]

    ###########################################

    sql = 'Select Hour1, Hour2, Include_Value from C_UpperT;'
    cur.execute(sql)
    triangleU = cur.fetchall()
    for t in triangleU:
        TRI_UP.add_record((str(t[0]), str(t[1]))).value = t[2]

    ###########################################

    sql = 'Select Hour1, Hour2, Include_Value from C_LowerT;'
    cur.execute(sql)
    triangleL = cur.fetchall()
    for t in triangleL:
        TRI_LOW.add_record((str(t[0]), str(t[1]))).value = t[2]

    ############################################

    sql = 'Select Hour1, Hour2, Include_Value from Linear;'
    cur.execute(sql)
    linearpems = cur.fetchall()
    for l in linearpems:
        LINEARPEM.add_record((str(l[0]), str(l[1]))).value = l[2]

    ############################################

    sql = 'Select Hour1, Hour2, Include_Value from Ownelast;'
    cur.execute(sql)
    elastpems = cur.fetchall()
    for o in elastpems:
        OWNELAST.add_record((str(o[0]), str(o[1]))).value = o[2]

    ############################################

    sql = 'Select Period, Hour, Value from Factor;'
    cur.execute(sql)
    factor_to_compensate = cur.fetchall()
    for f in factor_to_compensate:
        COMPENSATE.add_record((str(f[0]), str(f[1]))).value = f[2]

    ############################################

    sql = 'Select Period, Hour, Value from Ratio;'
    cur.execute(sql)
    inbalanceratios = cur.fetchall()
    for f in inbalanceratios:
        RATIO_H.add_record((str(f[0]), str(f[1]))).value = f[2]

    ############################################

    sql = 'Select Hour1, Hour2, Inner_frame from Minframe;'
    cur.execute(sql)
    innerbooleans = cur.fetchall()
    for e in innerbooleans:
        SHIFTMIN.add_record((str(e[0]), str(e[1]))).value = e[2]

    ############################################

    sql = 'Select Hour1, Hour2, Outer_frame from Maxframe;'
    cur.execute(sql)
    outerbooleans = cur.fetchall()
    for e in outerbooleans:
        SHIFTMAX.add_record((str(e[0]), str(e[1]))).value = e[2]


    ############################################
    sql = 'Select i.Instrument from Policy_instruments i where i.Include > 0;'
    cur.execute(sql)
    instruments = cur.fetchall()
    # print len(instruments)
    sql = 'Select Instrument, Year, Target from Policy_targets;'
    cur.execute(sql)
    targets = cur.fetchall()
    # print targets
    for i in instruments:
        # print i
        for t in targets:
            # print t[0]
            if t[0] in i:
                # print t[0], t[1], t[2]
                POL_TARGETS.add_record((str(t[0]), str(t[1]))).value = t[2]

    ############################################

    sql = 'Select r.Type from Reserves r where r.Include > 0;'
    cur.execute(sql)
    reserve_types = cur.fetchall()
    # print len(instruments)
    sql = 'Select Country, Type, Requirement from Reserves_deterministic;'
    cur.execute(sql)
    requirements = cur.fetchall()
    # print requirements
    for t in reserve_types:
        # print t
        for r in requirements:
            # print r[1]
            if r[1] in t:
                # print r[0], r[1], r[2]
                R_EXO.add_record((str(r[0]), str(r[1]))).value = r[2]

    sql = 'Select g.Code from Generation_technologies g where g.Include > 0 AND g.RES > 0 AND g.Dispatchable < 1;'
    cur.execute(sql)
    technologies = cur.fetchall()
    sql = 'Select r.Type from Reserves r where r.Include > 0;'
    cur.execute(sql)
    reserve_types = cur.fetchall()
    # print len(instruments)
    sql = 'Select Country, Technology, Type, Requirement from Reserves_probabilistic;'
    cur.execute(sql)
    requirements = cur.fetchall()
    # print requirements
    for g in technologies:
        for t in reserve_types:
            # print t
            for r in requirements:
                # print r[2]
                if r[1] in g:
                    if r[2] in t:
                        # print r[0], r[1], r[2], r[3]
                        R_ENDO.add_record((str(r[0]), str(r[1]), str(r[2]))).value = r[3]

    ############################################

    sql = 'Select r.Type from Reserves r where r.Include > 0 AND r.Type = "FCR_UP";'
    cur.execute(sql)
    reserves = cur.fetchall()
    for r in reserves:
        T_R.add_record((str(r[0]))).value = (0.5/2 + 14.5)/60
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "AFRR_UP" OR r.TYPE = "AFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    for r in reserves:
        T_R.add_record((str(r[0]))).value = (7.5/2 + 7.5)/60
    sql = 'Select r.Type from Reserves r where r.Include > 0 AND (r.Type = "MFRR_UP" OR r.TYPE = "MFRR_DN");'
    cur.execute(sql)
    reserves = cur.fetchall()
    for r in reserves:
        T_R.add_record((str(r[0]))).value = (15/2 + 45)/60

    ############################################

    conn.close()
    print "Done data acquisition"

    db.suppress_auto_domain_checking = True
    db.export('my_import_data.gdx')
    db.suppress_auto_domain_checking = False
    # try:
    print db.check_domains()
    if db.check_domains():
        job.run(gams_options=opt, databases=db, checkpoint =cp)
        ##########
        ## opmerking Wouter: in deze loops, vergelijk verschillende inputs
        #########
        #for inv_cost in [25.2,50.4,75.6,100.8,126]:
        for inv_cost in [75.6]:
        #     for target in [0,10,20,30,40,50]:
                # print target
                # for res_target in [target]:
            for res_target in [50]:
                print '*'*80
                print inv_cost
                print res_target
                job_sense = ws.add_job_from_string(
                    #'S_DATA(\'STOR_S\', \'C_P_C_INV\') = {inv_cost};\n'
                    #'POL_TARGETS(\'RES_SHARE\', \'2050\') = {res_target};\n'
                    # 'cplex option OptimalityTarget=3;\n'
                    # 'option nlp=pathnlp;\n'
                    # 'SOLVE GOA using nlp maximizing obj;'.format(res_target=res_target,inv_cost=inv_cost), cp)
                    'SOLVE GOA using lp minimizing obj;\n'
                    'parameter marg(Y,P,T,Z) shadow prices of production;\n'
                    'marg(Y,P,T,Z) = qbalance.m(Y,P,T,Z)/W(P);\n'
                    # 'parameter factor(P,H,Z) compensation to avoid energy losses;\n'
                    # 'factor(P,H,Z) = -shiftaway.l(P,H,Z)/(shiftforwards.l(P,H,Z)+shiftbackwards.l(P,H,Z)+0.00000001);\n'
                    'parameter ratio(P,H,Z) inbalance ratio;\n'
                    'ratio(P,H,Z) = (-shiftaway.l(P,H,Z)-shiftfi.l(P,H,Z)-shiftbi.l(P,H,Z))/(shiftfc.l(P,H,Z)+shiftbc.l(P,H,Z)+0.00000001);\n'
                    ,cp)
                    #'SOLVE GOA using lp minimizing obj;'.format(res_target=res_target,inv_cost=inv_cost), cp)
                job_sense.run(checkpoint=cp)
                job_sense.out_db.export(os.path.join(os.getcwd(),'results', 'out_db_{inv_cost}_{res_target}.gdx'.format(res_target=res_target,inv_cost=inv_cost)))
    else:
        for dvs in db.get_database_dvs():
            print dvs.symbol.name
            db.export('wrong_database.gdx')


    # except gams.workspace.GamsException as ge:
    #     print "error running gms file"
    #     for dvs in db.get_database_dvs():
    #         print dvs.symbol.name
    #     db.suppress_auto_domain_checking = True
    #     db.export('wrong_database.gdx')
