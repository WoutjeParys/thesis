$TITLE GOA version 2.0 (December 2013) puuh
$eolcom #
# GAMS options are $included from the file GAMS.opt
# GOA options are $included from the file GOA.opt
# In order to make them apply globally, the option $ONGLOBAL will first be seet here:
$ONGLOBAL

$include '../gams/GAMS.opt';
$include '../gams/GOA.opt';


#===============================================================================
# INPUT
#===============================================================================


#-------------------------------------------------------------------------------
#* Sets
#-------------------------------------------------------------------------------

# Declaration

SETS
RCZ         All geographical entities (R_ALL + C_ALL + Z_ALL)
R_ALL(RCZ)  All regions (i.e. W-EU & E-EU & North and Baltic Sea)
C_ALL(RCZ)  All countries
Z_ALL(RCZ)  All zones within a country
R_C(R_ALL,C_ALL) 	Countries in regions
C_Z(C_ALL,Z_ALL)	Zones in countries
#R(R_ALL)   Regions in the simulation
C(C_ALL)    Countries in the simulation
Z(Z_ALL)    Zones in the simulation

Y_ALL       All years
Y(Y_ALL)    Years in the simulation
P       	Time periods
T    		Time steps within periods

G           All generation technologies
GD(G)		Dispatchable generation technologies
GC(G)		Conventional generation technologies
GCG(GC)		Gas-fueled conventional generation technologies
GCO(GC)		Other conventional generation technologies
GR(G)		Renewable generation technologies
GRI(GR)		Intermittent renewable generation technologies
GRD(GR)		Dispatchable renewable generation technologies
G_PARAM		Generation technology parameters

S			All storage technologies
SSM(S)		Short and Mid-term storage technologies
SML(S)		Mid and Long-term storage technologies
SS(S)		Short-term storage technologies
SM(S)		Mid-term storage technologies
SL(S)		Long-term storage technologies
S_PARAM		Storage technology parameterz

POL			Policy instruments

R			Reserve requirements
RU(R)		Upward reserve requirements
RD(R)		Downward reserve requirements
RUF(RU)		FCR upward reserve requirements
RUA(RU)		FCR and aFRR upward reserve requirements
RDA(RD)		aFRR downward reserve requirements

H			All possible hours
;

$GDXIN %SupplyDataFileName%
$LOAD RCZ R_ALL C_ALL Z_ALL R_C C_Z C Z
$LOAD Y_ALL Y
$LOAD P T
$LOAD G GD GC GCG GCO GR GRI GRD G_PARAM
$LOAD S SSM SML SS SM SL S_PARAM
$LOAD POL
$LOAD R RU RD RUF RUA RDA
$LOAD H

alias(T,T_MUT,T_MDT,T_E);
SSM(S) = SS(S) + SM(S);

SETS
MUT(G,T_MUT)	Minimum up time per technology
MDT(G,T_MDT)	Minimum down time per technology
;

$LOAD MUT
$LOAD MDT

PARAMETERS
G_DATA(G,G_PARAM)		Technologies characteristics
S_DATA(S,S_PARAM)  		Technologies characteristics

RG(R,GD)				Ramping ability per reserve category for generation technologies
RSC(R,SML)				Ramping ability per reserve category for storage technologies while charging
RSD(R,SM)				Ramping ability per reserve category for storage technologies while discharging

C_GAS					Cost of imported gas

DEM(Y_ALL,Z_ALL)		Energy demand per year [MWh]
DEM_T(P,T,Z_ALL) 		Relative electricity demand per hour [percentage]

RES_T(P,T,Z_ALL,GRI)	Intermittent generation profilez [MW]
REL_T(P,T,Z_ALL,GRI)	Reliable intermittent generation profilez [MW]

W(P)					Weight of period P

POL_TARGETS(POL,Y_ALL)	Policy targets such as the desired share of renewables in production [%]

#CAP_G(Y,Z,G,C_PARAM)	Installed capacities per zone per year [MW]

R_EXO(C_ALL,R)			Exogenous reserve requirements per country
R_ENDO(C_ALL,GRI,R)		Endogenous reserve requirements per country per (renewable) generation technology

T_MARKET				Time step of the market
T_R(R)                  Time factor to calculate energy for reserve provision

EGCAPEX					Annualized energy investment cost of gas storage
E_LP					Energy volume of the gas line pack

ELAST(T,H)				Elasticity relative to hour one and hour two

DIAG(T,H)				a matrix to include the controlled hour
TRI_UP(T,H)				a matrix to include the eleven earlier hours
TRI_LOW(T,H)			a matrix to include the twelve later hours

P_REF					reference price (calculated in advance)
TOTDEM					The sum of the demand over all hours
LIMITPRICE				absolute value of price difference that is allowed
LIMITDEM				absolute value of max demand shift
LIMITSHIFT				absolute value of max demand shifted away from an hour with use of elasticities
SHIFTMIN(H,T)			matrix to constraint shifting of energy inner window
SHIFTMAX(H,T)			matrix to constraint shifting of energy outer window
LENGTH_P				the length of the period as programmed in main and init (.py)

eff_factor_earlier		a factor to include the efficiency of demand shifted to an earlier time
eff_factor_later		a factor to include the efficiency of demand shifted to a later time

COMPENSATE(P,H)			a parameter that compensates for energy losses due an elasticity-matrix that is not perfect
ELAST_NEW(P,T,H)        the new calculated elasticity matrix, taking into account the compensation factor
;

$LOAD G_DATA
$LOAD S_DATA
$LOAD RG
$LOAD RSC
$LOAD RSD
$LOAD DEM DEM_T
$LOAD RES_T
$LOAD REL_T
$LOAD W
$LOAD POL_TARGETS
#$LOAD CAP_G
$LOAD R_EXO
$LOAD R_ENDO
$LOAD T_R
$LOAD ELAST
$LOAD DIAG
$LOAD TRI_UP TRI_LOW
$LOAD SHIFTMIN
$LOAD SHIFTMAX
$LOAD COMPENSATE

#C_GAS = 25.6643460843943;
C_GAS = 25.6643460843943*2;
T_MARKET = 1;
EGCAPEX = 2000000000000000000000000;
E_LP = 7100000;
P_REF = 55.5;
TOTDEM = sum((P,T,Z),DEM_T(P,T,Z));
LIMITPRICE = P_REF*0.9;
LIMITDEM = 750;
LIMITSHIFT = 2000;
LENGTH_P = card(T);
ELAST_NEW(P,T,H) = ELAST(T,H)*DIAG(T,H)+COMPENSATE(P,H)*(TRI_LOW(T,H)*ELAST(T,H)+TRI_UP(T,H)*ELAST(T,H));
#ELAST_NEW(P,T,H) = ELAST(T,H)*1;

eff_factor_earlier = 0.0;
eff_factor_later = 0.0;

VARIABLES
obj                 	Value of objective function

#######################################################

shiftforwards(P,H,Z)			Shift towards an earlier moment in time per hour
shiftforwards_total(P,Z)		Shift towards an earlier moment in time per period
shiftbackwards(P,H,Z)			Shift towards a later moment in time per hour
shiftbackwards_total(P,Z)		Shift towards a later moment in time per period
shiftaway(P,H,Z)				Shift away from an hour
shiftaway_total(P,Z)			Shift away from a period

front_up(P,H,Z)
front_down(P,H,Z)
back_up(P,H,Z)
back_down(P,H,Z)
shift_down(P,H,Z)
shift_up(P,H,Z)
;

POSITIVE VARIABLES
#######################################################

price_unit(P,H,Z)				Price of the electricity
price_unit_clone(P,T,Z)
demand_unit(P,T,Z)				demand of the electricity
demand_unit_clone(P,H,Z)
demand_tot(P,Z)					total demand, based on demand_unit
surplus(P,T,Z)
demand_ref(P,T,Z)				the reference demand with flat price
innerframe(P,H,Z)
outerframe(P,H,Z)

totalrevenue(P,Z)				the product of demand and price
totalfixedcost(Z)				the sum of the total investment cost and fixed variable cost
totalvariablecost(P,Z)			the sum of the variable O&M cost and fuel cost
totalcost(Z)					the sum of the totalvariablecost and totalfixedcost

#######################################################

cap(Y,Z,G)					Generation capacity per year, per zone and per generation technology [MW]
e_cap(Y,Z,S)				Energy capacity of storage technology S
p_cap_c(Y,Z,S)				Charging power capacity of storage technology S
p_cap_d(Y,Z,SM)				Discharging power capacity of storage technology SM
eg_cap						Gas storage capacity

gen(Y,P,T,Z,G)           	Electricity generation per time step, per zone and per generation technology [MWh]
curt(Y,P,T,Z,GRI)			Curtailment of renewable output

e(Y,P,Z,S)        			Energy content of storage technology S at period P
e_f(Y,P,T,Z,S)    			Energy content of storage technology S at time T during the first cycle of period P
e_l(Y,P,T,Z,S)    			Energy content of storage technology S at time T during the last cycle of period P
p_c(Y,P,T,Z,S)          	Electricity generation per time step, per zone and per generation technology [MWh]
p_d(Y,P,T,Z,S)        		Electricity generation per time step, per zone and per generation technology [MWh]
eg(Y,P,C)					Energy content of gas storage at period P
eg_f(Y,P,T,C)    			Energy content of gas storage at time T during the first cycle of period P
eg_l(Y,P,T,C)    			Energy content of gas storage at time T during the last cycle of period P
pg_c(Y,P,T,C)				Charging of gas storage
pg_d(Y,P,T,C)				Discharging of gas storage

res_g(Y,P,T,Z,R,G)			Reserve allocation of generation technology GD for reserve category R
res_s(Y,P,T,Z,R,S)			Reserve allocation of storage technology S for reserve category R

load_shedding(Y,P,T,Z)		Load shedding
q_endo(Y,P,T,C,R,GRI)		Endogenous reserve requirements for category R
co2(Y,C,G)					CO2-emissions per year, per zone and per generation technology [kg]
lcg(Y,C,G)					Life cycle greenhouse gas emissions per year, per zone and per generation technology [kg]

res_g_s(Y,P,T,Z,R,GD)		Spinning reserve allocation of generation technology GD for reserve category R
res_g_ns(Y,P,T,Z,RU,GD)		Start-up reserve allocation of generation technology GD for reserve category RU
res_g_sd(Y,P,T,Z,RD,GD)		Shut-down reserve allocation of generation technology GD for reserve category RD

n(Y,P,T,Z,GD)				Number of units of each generation technology per year, time step and zone [-]
n_su(Y,P,T,Z,GD)			Number of units starting up of each generation technology
n_sd(Y,P,T,Z,GD)			Number of units shutting down of each generation technology
n_su_r(Y,P,T,Z,RU,GD)		Number of units starting up of each generation technology
n_sd_r(Y,P,T,Z,RD,GD)		Number of units shutting down of each generation technology

ramp_up(Y,P,T,Z,GD)			Increase in output by ramping up
ramp_dn(Y,P,T,Z,GD)			Decrease in output by ramping down
ramp_su(Y,P,T,Z,GD)			Increase in output by starting up additional units
ramp_sd(Y,P,T,Z,GD)			Decrease in output by shutting down units

curt_dummy(Y,P,T,Z,GRI)		Dummy variable in case RES objective cannot be reached

res_s_c(Y,P,T,Z,R,S)		Reserve allocation of charging storage technology S for reserve category R
res_s_c_s(Y,P,T,Z,R,SML)	Spinning reserve allocation of charging storage technology SML for reserve category R
res_s_c_ns(Y,P,T,Z,RD,SML)	Start-up reserve allocation of charging storage technology SML for reserve category RD
res_s_c_sd(Y,P,T,Z,RU,SML)	Shut-down reserve allocation of charging storage technology SML for reserve category RU
res_s_d(Y,P,T,Z,R,S)		Reserve allocation of discharging storage technology S for reserve category R
res_s_d_s(Y,P,T,Z,R,SM)		Spinning reserve allocation of discharging storage technology SM for reserve category R
res_s_d_ns(Y,P,T,Z,RU,SM)	Start-up reserve allocation of discharging storage technology SM for reserve category RU
res_s_d_sd(Y,P,T,Z,RD,SM)	Shut-down reserve allocation of discharging storage technology SM for reserve category RD

n_c(Y,P,T,Z,SML)			Number of units of each generation technology per year, time step and zone [-]
n_c_su(Y,P,T,Z,SML)			Number of units starting up of each generation technology
n_c_sd(Y,P,T,Z,SML)			Number of units shutting down of each generation technology
n_c_su_r(Y,P,T,Z,RD,SML)	Number of units starting up of each generation technology
n_c_sd_r(Y,P,T,Z,RU,SML)	Number of units shutting down of each generation technology

ramp_c_up(Y,P,T,Z,S)		Increase in output by ramping up
ramp_c_dn(Y,P,T,Z,S)		Decrease in output by ramping down
ramp_c_su(Y,P,T,Z,SML)		Increase in output by starting up additional units
ramp_c_sd(Y,P,T,Z,SML)		Decrease in output by shutting down units

n_d(Y,P,T,Z,SM)				Number of units of each generation technology per year, time step and zone [-]
n_d_su(Y,P,T,Z,SM)			Number of units starting up of each generation technology
n_d_sd(Y,P,T,Z,SM)			Number of units shutting down of each generation technology
n_d_su_r(Y,P,T,Z,RU,SM)		Number of units starting up of each generation technology
n_d_sd_r(Y,P,T,Z,RD,SM)		Number of units shutting down of each generation technology

ramp_d_up(Y,P,T,Z,S)		Increase in output by ramping up
ramp_d_dn(Y,P,T,Z,S)		Decrease in output by ramping down
ramp_d_su(Y,P,T,Z,SM)		Increase in output by starting up additional units
ramp_d_sd(Y,P,T,Z,SM)		Decrease in output by shutting down units

pg_import(Y,P,T,C)			Import of gas
pg_syn(Y,P,T,Z,GCG)			Use of synthetic gas in gas-fueled conventional generation technologies GCG
pg_fos(Y,P,T,Z,GCG)			Use of natural gas in gas-fueled conventional generation technologies GCG

;

EQUATIONS
#--Objective function--#
qobj

#--System constraints--#
qbalance(Y,P,T,Z)
qresprod(Y,C)
qco2lim(Y,C)
qresendomin(Y,P,T,C,R,GRI)
qresendomax(Y,P,T,C,R,GRI)
qres(Y,P,T,C,R)
qgendisp(Y,P,T,C)
qgendisppeak(Y,C)
qco2(Y,C,G)
qlcg(Y,C,G)

#--Generation technologies--#
qpotcapmin(Y,C,G)
#qpotcapmax(Y,C,G)
#qpotgenmin(Y,C,G)
#qpotgenmax(Y,C,G)

qresgcu(Y,P,T,Z,RU,GD)
qresgcd(Y,P,T,Z,RD,GD)
qn(Y,P,T,Z,GD)
qnmax(Y,P,T,Z,GD)
qnsu(Y,P,T,Z,GD)
qnsd(Y,P,T,Z,GD)
qgen(Y,P,T,Z,GD)
qgenmin(Y,P,T,Z,GD)
qgenmax(Y,P,T,Z,GD)
qrudyn(Y,P,T,Z,GD)
qrucap(Y,P,T,Z,GD)
qrddyn(Y,P,T,Z,GD)
qrdcap(Y,P,T,Z,GD)
qsumin(Y,P,T,Z,GD)
qsumax(Y,P,T,Z,GD)
qsdmin(Y,P,T,Z,GD)
qsdmax(Y,P,T,Z,GD)
qrufu(Y,P,T,Z,GD)
qruau(Y,P,T,Z,GD)
qrumus(Y,P,T,Z,GD)
qrdad(Y,P,T,Z,GD)
qrdmd(Y,P,T,Z,GD)
qrunsmin(Y,P,T,Z,RU,GD)
qrunsmax(Y,P,T,Z,RU,GD)
qrdsdmin(Y,P,T,Z,RD,GD)
qrdsdmax(Y,P,T,Z,RD,GD)

qresgru(Y,P,T,Z,RU,GRI)
qgenr(Y,P,T,Z,GRI)
qresgrdr(Y,P,T,Z,GRI)
qresgrdg(Y,P,T,Z,GRI)

#--Storage technologies--#
qress(Y,P,T,Z,R,S)
qspotcapmin(Y,C,S)
qspotcapmax(Y,C,S)

qe(Y,P,Z,S)
qemax(Y,P,Z,S)
qef(Y,P,T,Z,S)
qefmin(Y,P,T,Z,S)
qefmax(Y,P,T,Z,S)
qefstart(Y,P,T,Z,S)
qel(Y,P,T,Z,S)
qelmin(Y,P,T,Z,S)
qelmax(Y,P,T,Z,S)
qelstart(Y,P,T,Z,S)
qdurmin(Y,Z,S)
qdurmax(Y,Z,S)

qssc(Y,P,T,Z,SS)
qsscru(Y,P,T,Z,SS)
qsscrd(Y,P,T,Z,SS)
qssd(Y,P,T,Z,SS)
qssdru(Y,P,T,Z,SS)
qssdrd(Y,P,T,Z,SS)

qresscu(Y,P,T,Z,RU,SML)
qresscd(Y,P,T,Z,RD,SML)
qressdu(Y,P,T,Z,RU,SM)
qressdd(Y,P,T,Z,RD,SM)
qnc(Y,P,T,Z,SML)
qncmax(Y,P,T,Z,SML)
qncsu(Y,P,T,Z,SML)
qncsd(Y,P,T,Z,SML)
qsmlc(Y,P,T,Z,SML)
qsmlcmin(Y,P,T,Z,SML)
qsmlcmax(Y,P,T,Z,SML)
qcrudyn(Y,P,T,Z,SML)
qcrucap(Y,P,T,Z,SML)
qcrddyn(Y,P,T,Z,SML)
qcrdcap(Y,P,T,Z,SML)
qcsumin(Y,P,T,Z,SML)
qcsumax(Y,P,T,Z,SML)
qcsdmin(Y,P,T,Z,SML)
qcsdmax(Y,P,T,Z,SML)
qcruad(Y,P,T,Z,SML)
qcrumd(Y,P,T,Z,SML)
qcrdfu(Y,P,T,Z,SML)
qcrdau(Y,P,T,Z,SML)
qcrdmus(Y,P,T,Z,SML)
qcrunsmin(Y,P,T,Z,RD,SML)
qcrunsmax(Y,P,T,Z,RD,SML)
qcrdsdmin(Y,P,T,Z,RU,SML)
qcrdsdmax(Y,P,T,Z,RU,SML)

qcapdeqcapc(Y,Z,SM)
qnd(Y,P,T,Z,SM)
qndmax(Y,P,T,Z,SM)
qndsu(Y,P,T,Z,SM)
qndsd(Y,P,T,Z,SM)
qsmd(Y,P,T,Z,SM)
qsmdmin(Y,P,T,Z,SM)
qsmdmax(Y,P,T,Z,SM)
qdrudyn(Y,P,T,Z,SM)
qdrucap(Y,P,T,Z,SM)
qdrddyn(Y,P,T,Z,SM)
qdrdcap(Y,P,T,Z,SM)
qdsumin(Y,P,T,Z,SM)
qdsumax(Y,P,T,Z,SM)
qdsdmin(Y,P,T,Z,SM)
qdsdmax(Y,P,T,Z,SM)
qdrufu(Y,P,T,Z,SM)
qdruau(Y,P,T,Z,SM)
qdrumus(Y,P,T,Z,SM)
qdrdad(Y,P,T,Z,SM)
qdrdmd(Y,P,T,Z,SM)
qdrunsmin(Y,P,T,Z,RU,SM)
qdrunsmax(Y,P,T,Z,RU,SM)
qdrdsdmin(Y,P,T,Z,RD,SM)
qdrdsdmax(Y,P,T,Z,RD,SM)

qslressd(Y,P,T,Z,R,SL)
qgase(Y,P,C)
qgasemax(Y,P,C)
qgasef(Y,P,T,C)
qgasefmax(Y,P,T,C)
qgasefstart(Y,P,T,C)
qgasel(Y,P,T,C)
qgaselmax(Y,P,T,C)
qgaselstart(Y,P,T,C)
qgasc(Y,P,T,C)
qgasd(Y,P,T,C)
qgasuse(Y,C)
qgasusegen(Y,P,T,Z,GCG)

###############################
#price(P,H,Z)
price_clone(P,T,Z)
demand(P,T,Z)
demand_clone(P,H,Z)
totdemand(P,Z)
surplusdemand(P,T,Z)
totdemand2(P,Z)
refdemand(P,T,Z)
refdemand2(Z)
priceconstraint1(P,T,Z)
priceconstraint2(P,T,Z)
priceconstraint3(P,Z)
shiftconstraint_frame_1(P,H,Z)
shiftconstraint_frame_2(P,H,Z)
shiftconstraint1(P,H,Z)
shiftconstraint2(P,H,Z)
shiftedforward(P,H,Z)
shiftedforwardtotal(P,Z)
shiftedbackward(P,H,Z)
shiftedbackwardtotal(P,Z)
shiftedaway(P,H,Z)
shiftedawaytotal(P,Z)

front_d_1(P,H,Z)
front_d_2(P,H,Z)
front_u_1(P,H,Z)
front_u_2(P,H,Z)

back_d_1(P,H,Z)
back_d_2(P,H,Z)
back_u_1(P,H,Z)
back_u_2(P,H,Z)

shift_d_1(P,H,Z)
shift_d_2(P,H,Z)
shift_u_1(P,H,Z)
shift_u_2(P,H,Z)

qinnerframe(P,H,Z)
qouterframe(P,H,Z)

revenue(P,Z)
fixedcost(Z)
variablecost(P,Z)
cost(Z)

demlimitunder(P,T,Z)
demlimitupper(P,T,Z)
;

#-----######################---------------------------------------------------#
#-----# Objective function #---------------------------------------------------#
#-----######################---------------------------------------------------#
qobj..              obj
					=e=
						sum((Y,Z,G), 		(G_DATA(G,'C_INV') + G_DATA(G,'C_FOM'))*1000*cap(Y,Z,G))
						#+ sum((Y,Z,S),      (S_DATA(S,'C_P_C_INV')*1000)*p_cap_c(Y,Z,S))
						+
						(sum((Y,P,T,Z,G), 		W(P)*(G_DATA(G,'C_VOM'))*gen(Y,P,T,Z,G))
						+ sum((Y,P,T,Z,GC), 	W(P)*(G_DATA(GC,'C_FUEL'))*gen(Y,P,T,Z,GC))

						#+ sum((Y,P,T,Z,S), 		W(P)*(S_DATA(S,'OPEX'))*p_c(Y,P,T,Z,S)+p_d(Y,P,T,Z,S))

						)
						*(168/card(T));
						;




#-----######################---------------------------------------------------#
#-----# System constraints #---------------------------------------------------#
#-----######################---------------------------------------------------#

#--System balance--#

# balance with demand response
qbalance(Y,P,T,Z)..
    				sum(G, gen(Y,P,T,Z,G))
    				#+ sum(SSM, p_d(Y,P,T,Z,SSM))
					=e=
						demand_unit(P,T,Z)
#						- load_shedding(Y,P,T,Z)
						#+ sum(S, p_c(Y,P,T,Z,S))
						;

#balance without demand response
#qbalance(Y,P,T,Z)..
#    				sum(G, gen(Y,P,T,Z,G))
#					#+ sum(SSM, p_d(Y,P,T,Z,SSM))
#					=e=
#						DEM_T(P,T,Z)
#					#	- load_shedding(Y,P,T,Z)
#					#	+ sum(S, p_c(Y,P,T,Z,S))
#						;
#DEM(Y,Z)*DEM_T(T,Z);

#--Renewable target--#

#qresprod(Y,C)..
#					sum(Z $ C_Z(C,Z), 	sum((GCO,P,T), W(P)*gen(Y,P,T,Z,GCO)))
#					+ sum(Z $ C_Z(C,Z), sum((GCG,P,T), W(P)*pg_fos(Y,P,T,Z,GCG)*(G_DATA(GCG,'EFF')/100)))
#					=l=
#						(100 - POL_TARGETS('RES_SHARE', Y))/100 * sum(Z $ C_Z(C,Z), sum((P,T), W(P)*DEM_T(P,T,Z)))
#						;

qresprod(Y,C)..
					sum(Z $ C_Z(C,Z), sum((GR,P,T), W(P)*gen(Y,P,T,Z,GR)))
					=g=
						POL_TARGETS('RES_SHARE', Y)/100 * sum(Z $ C_Z(C,Z), sum((P,T), W(P)*DEM_T(P,T,Z)))
						;

qco2lim(Y,C)..
#					sum(Z $ C_Z(C,Z), sum((GCO,P,T), W(P)*gen(Y,P,T,Z,GCO)*G_DATA(GCO,'CO2')))
#					+ sum(Z $ C_Z(C,Z), sum((GCG,P,T), W(P)*pg_fos(Y,P,T,Z,GCG)*(G_DATA(GCG,'EFF')/100)*G_DATA(GCG,'CO2')))
					sum(Z $ C_Z(C,Z), sum((GC,P,T), W(P)*gen(Y,P,T,Z,GC)*G_DATA(GC,'CO2')))
					=l=
						50000000*0.4
						;

#--Reserve requirements--#

qresendomin(Y,P,T,C,R,GRI)..
					q_endo(Y,P,T,C,R,GRI)
					=g=
						R_ENDO(C,GRI,R)*sum(Z $ C_Z(C,Z), (RES_T(P,T,Z,GRI)-REL_T(P,T,Z,GRI))*cap(Y,Z,GRI)-curt(Y,P,T,Z,GRI))
						;

qresendomax(Y,P,T,C,R,GRI)..
					q_endo(Y,P,T,C,R,GRI)
					=l=
						R_ENDO(C,GRI,R)*sum(Z $ C_Z(C,Z), (RES_T(P,T,Z,GRI)-REL_T(P,T,Z,GRI))*cap(Y,Z,GRI))
						;


qres(Y,P,T,C,R)..
					sum(Z $ C_Z(C,Z), 	sum(G, res_g(Y,P,T,Z,R,G)))
					+ sum(Z $ C_Z(C,Z), sum(S, res_s(Y,P,T,Z,R,S)))
					=e=
						R_EXO(C,R)
						+ sum(GRI, q_endo(Y,P,T,C,R,GRI))
						;

#--Dispatchable capacity--#

qgendisp(Y,P,T,C)..
					sum(Z $ C_Z(C,Z), sum(GD, gen(Y,P,T,Z,GD)))
					=g=
						sum(Z $ C_Z(C,Z), DEM_T(P,T,Z))*0.20
						;

qgendisppeak(Y,C)..
					sum(Z $ C_Z(C,Z), sum(GD, cap(Y,Z,GD)))
					=g=
						10000*1.20
						;

#--Emissions--#

qco2(Y,C,G)..
					co2(Y,C,G)
					=e=
						sum(Z $ C_Z(C,Z), sum((P,T), W(P)*gen(Y,P,T,Z,G)*G_DATA(G,'CO2')))
						;

qlcg(Y,C,G)..
					lcg(Y,C,G)
					=e=
						sum(Z $ C_Z(C,Z), sum((P,T), gen(Y,P,T,Z,G)*G_DATA(G,'LCG')))
						;


#-----###########################----------------------------------------------#
#-----# Generation technologies #----------------------------------------------#
#-----###########################----------------------------------------------#

##--Installed generation capacities--#

qpotcapmin(Y,C,G)..
					sum(Z $ C_Z(C,Z), cap(Y,Z,G))
					=g=
						G_DATA(G,'CAP_MIN')
						;

#qpotcapmax(Y,C,G)..
#					sum(Z $ C_Z(C,Z), cap(Y,Z,G))
#					=g=
#						CAP_G(Y,Z,G,'CAP_MAX')
#						;
#
#qpotgenmin(Y,C,G)..
#					sum(Z $ C_Z(C,Z), sum(T, gen(Y,T,Z,G)))
#					=g=
#						CAP_G(Y,Z,G,'GEN_MIN')
#						;
#
#qpotgenmax(Y,Z,G)..
#					sum(Z $ C_Z(C,Z), sum(T, gen(Y,T,Z,G)))
#					=g=
#						CAP_G(Y,Z,G,'GEN_MAX')
#						;

#-------Dispatchable generation technologies-----------------------------------#

#--Reserve allocation--#

qresgcu(Y,P,T,Z,RU,GD)..
					res_g(Y,P,T,Z,RU,GD)
					=e=
						res_g_s(Y,P,T,Z,RU,GD)
						+ res_g_ns(Y,P,T,Z,RU,GD)
						;

qresgcd(Y,P,T,Z,RD,GD)..
					res_g(Y,P,T,Z,RD,GD)
					=e=
						res_g_s(Y,P,T,Z,RD,GD)
						+ res_g_sd(Y,P,T,Z,RD,GD)
						;

#--Clustering logical constraints--#

qn(Y,P,T,Z,GD)$(ord(T)<card(T))..
					n(Y,P,T+1,Z,GD)
					=e=
						n(Y,P,T,Z,GD)
						+ n_su(Y,P,T,Z,GD)
						- n_sd(Y,P,T,Z,GD)
						;

qnmax(Y,P,T,Z,GD)..
					n(Y,P,T,Z,GD)
					=l=
						cap(Y,Z,GD)/G_DATA(GD,'P_MAX')
						;

qnsu(Y,P,T,Z,GD)..
					n_su(Y,P,T,Z,GD)
					+ sum(RU, n_su_r(Y,P,T,Z,RU,GD))
					=l=
						cap(Y,Z,GD)/G_DATA(GD,'P_MAX')
						- n(Y,P,T,Z,GD)
						- sum(MDT(GD,T_MDT), n_sd(Y,P, T-(ord(T_MDT)-1), Z, GD))
						;

qnsd(Y,P,T,Z,GD)..
					n_sd(Y,P,T,Z,GD)
					+ sum(RD, n_sd_r(Y,P,T,Z,RD,GD))
					=l=
						n(Y,P,T,Z,GD)
						- sum(MUT(GD,T_MUT), n_su(Y,P, T-(ord(T_MUT)-1), Z, GD))
						;

#--Generation constraints--#

qgen(Y,P,T,Z,GD)$(ord(T)<card(T))..
                    gen(Y,P,T+1,Z,GD)
                    =e=
                    	gen(Y,P,T,Z,GD)
                    	+ ramp_up(Y,P,T,Z,GD)
                    	- ramp_dn(Y,P,T,Z,GD)
                    	+ ramp_su(Y,P,T,Z,GD)
                    	- ramp_sd(Y,P,T,Z,GD)
                    	;

qgenmin(Y,P,T,Z,GD)..
					gen(Y,P,T,Z,GD)
					=g=
						n(Y,P,T,Z,GD)*G_DATA(GD,'P_MIN')
						;

qgenmax(Y,P,T,Z,GD)..
					gen(Y,P,T,Z,GD)
					=l=
						n(Y,P,T,Z,GD)*G_DATA(GD,'P_MAX')
						;
						#*G_DATA(G,'PM')/100;

#--Ramping constraints--#

qrudyn(Y,P,T,Z,GD)..
                    ramp_up(Y,P,T,Z,GD)
                    + sum(RU, res_g_s(Y,P,T,Z,RU,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD))*G_DATA(GD,'RH')/100*G_DATA(GD,'P_MAX')
                    	;

qrucap(Y,P,T,Z,GD)..
                    ramp_up(Y,P,T,Z,GD)
                    + sum(RU, res_g_s(Y,P,T,Z,RU,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD))*G_DATA(GD,'P_MAX')
                    	- (gen(Y,P,T,Z,GD)-ramp_sd(Y,P,T,Z,GD))
                    	;

qrddyn(Y,P,T,Z,GD)..
                    ramp_dn(Y,P,T,Z,GD)
                    + sum(RD, res_g_s(Y,P,T,Z,RD,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD)-sum(RD, n_sd_r(Y,P,T,Z,RD,GD)))*G_DATA(GD,'RH')/100*G_DATA(GD,'P_MAX')
                    	;

qrdcap(Y,P,T,Z,GD)..
                    ramp_dn(Y,P,T,Z,GD)
                    + sum(RD, res_g_s(Y,P,T,Z,RD,GD))
                    =l=
                    	(gen(Y,P,T,Z,GD)-ramp_sd(Y,P,T,Z,GD)-sum(RD, res_g_sd(Y,P,T,Z,RD,GD)))
                    	- (n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD)-sum(RD, n_sd_r(Y,P,T,Z,RD,GD)))*G_DATA(GD,'P_MIN')
                    	;

qsumin(Y,P,T,Z,GD)..
					ramp_su(Y,P,T,Z,GD)
					=g=
						n_su(Y,P,T,Z,GD)*G_DATA(GD,'P_MIN')
						;

qsumax(Y,P,T,Z,GD)..
					ramp_su(Y,P,T,Z,GD)
					=l=
						n_su(Y,P,T,Z,GD)*G_DATA(GD,'RH')/100*G_DATA(GD,'P_MAX')
						;

qsdmin(Y,P,T,Z,GD)..
					ramp_sd(Y,P,T,Z,GD)
					=g=
						n_sd(Y,P,T,Z,GD)*G_DATA(GD,'P_MIN')
						;

qsdmax(Y,P,T,Z,GD)..
					ramp_sd(Y,P,T,Z,GD)
					=l=
						n_sd(Y,P,T,Z,GD)*G_DATA(GD,'RH')/100*G_DATA(GD,'P_MAX')
						;

#--Reserve allocation constraints--#

qrufu(Y,P,T,Z,GD)..
                    sum(RUF, res_g_s(Y,P,T,Z,RUF,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD))*G_DATA(GD,'RF')/100*G_DATA(GD,'P_MAX')
                    	;

qruau(Y,P,T,Z,GD)..
                    sum(RUA, res_g_s(Y,P,T,Z,RUA,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD))*G_DATA(GD,'RA')/100*G_DATA(GD,'P_MAX')
                    	;

qrumus(Y,P,T,Z,GD)..
                    sum(RU, res_g_s(Y,P,T,Z,RU,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD))*G_DATA(GD,'RM')/100*G_DATA(GD,'P_MAX')
                    	;

qrdad(Y,P,T,Z,GD)..
                    sum(RDA, res_g_s(Y,P,T,Z,RDA,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD)-sum(RD, n_sd_r(Y,P,T,Z,RD,GD)))*G_DATA(GD,'RA')/100*G_DATA(GD,'P_MAX')
                    	;

qrdmd(Y,P,T,Z,GD)..
                    sum(RD, res_g_s(Y,P,T,Z,RD,GD))
                    =l=
                    	(n(Y,P,T,Z,GD)-n_sd(Y,P,T,Z,GD)-sum(RD, n_sd_r(Y,P,T,Z,RD,GD)))*G_DATA(GD,'RM')/100*G_DATA(GD,'P_MAX')
                    	;

qrunsmin(Y,P,T,Z,RU,GD)..
					res_g_ns(Y,P,T,Z,RU,GD)
					=g=
						n_su_r(Y,P,T,Z,RU,GD)*G_DATA(GD,'P_MIN')
						;

qrunsmax(Y,P,T,Z,RU,GD)..
					res_g_ns(Y,P,T,Z,RU,GD)
					=l=
						n_su_r(Y,P,T,Z,RU,GD)*RG(RU,GD)/100*G_DATA(GD,'P_MAX')
						;

qrdsdmin(Y,P,T,Z,RD,GD)..
					res_g_sd(Y,P,T,Z,RD,GD)
					=g=
						n_sd_r(Y,P,T,Z,RD,GD)*G_DATA(GD,'P_MIN')
						;

qrdsdmax(Y,P,T,Z,RD,GD)..
					res_g_sd(Y,P,T,Z,RD,GD)
					=l=
						n_sd_r(Y,P,T,Z,RD,GD)*RG(RD,GD)/100*G_DATA(GD,'P_MAX')
						;

#-------Intermittent renewable generation technologies-------------------------#

#--Reserve allocation--#

qresgru(Y,P,T,Z,RU,GRI)..
					res_g(Y,P,T,Z,RU,GRI)
					=e=
						0
						;

#--Output and curtailment constraint--#

qgenr(Y,P,T,Z,GRI)..
                    gen(Y,P,T,Z,GRI)
                    + curt(Y,P,T,Z,GRI)
                    + curt_dummy(Y,P,T,Z,GRI)
                    =e=
                    	cap(Y,Z,GRI)*RES_T(P,T,Z,GRI)
                    	;

#--Reserve allocation constraints--#

qresgrdr(Y,P,T,Z,GRI)..
					sum(RD, res_g(Y,P,T,Z,RD,GRI))
					=l=
						cap(Y,Z,GRI)*REL_T(P,T,Z,GRI)
						;

qresgrdg(Y,P,T,Z,GRI)..
					sum(RD, res_g(Y,P,T,Z,RD,GRI))
					=l=
						gen(Y,P,T,Z,GRI)
						;

#-----########################-------------------------------------------------#
#-----# Storage technologies #-------------------------------------------------#
#-----########################-------------------------------------------------#

#-------General constraints----------------------------------------------------#

#--Reserve allocation--#

qress(Y,P,T,Z,R,S)..
					res_s(Y,P,T,Z,R,S)
					=e=
						res_s_c(Y,P,T,Z,R,S)
						+ res_s_d(Y,P,T,Z,R,S)
						;

#--Installed capacities--#

qspotcapmin(Y,C,S)..
					sum(Z $ C_Z(C,Z), p_cap_c(Y,Z,S))
					=g=
						S_DATA(S,'CAP_MIN')
						;

qspotcapmax(Y,C,S)..
					sum(Z $ C_Z(C,Z), p_cap_c(Y,Z,S))
					=l=
						S_DATA(S,'CAP_MAX')
						;

#-------Short- and mid-term storage--------------------------------------------#

#--Energy constraints--#

qe(Y,P,Z,SSM)..
					e(Y,P++1,Z,SSM)
					=e=
						e(Y,P,Z,SSM)
						+ W(P)*sum(T_E, p_c(Y,P,T_E,Z,SSM)*(S_DATA(SSM,'EFF_C')/100) - p_d(Y,P,T_E,Z,SSM)/(S_DATA(SSM,'EFF_D')/100))
						;

qemax(Y,P,Z,SSM)..
					e(Y,P,Z,SSM)
					=l=
						e_cap(Y,Z,SSM)
						#p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN')
						;

qefstart(Y,P,T,Z,SSM)$(ord(T)=1)..
					e_f(Y,P,T,Z,SSM)
					=e=
						e(Y,P,Z,SSM)
						;

qef(Y,P,T,Z,SSM)$(ord(T)<card(T))..
					e_f(Y,P,T+1,Z,SSM)
					=e=
						e_f(Y,P,T,Z,SSM)
						+ p_c(Y,P,T,Z,SSM)*(S_DATA(SSM,'EFF_C')/100)
						- p_d(Y,P,T,Z,SSM)/(S_DATA(SSM,'EFF_D')/100)
						;

qefmin(Y,P,T,Z,SSM)..
					e_f(Y,P,T,Z,SSM)
					=g=
						1/(S_DATA(SSM,'EFF_D')/100)*
						(p_d(Y,P,T,Z,SSM)*T_MARKET
						+ sum(RU, res_s_d(Y,P,T,Z,RU,SSM)*T_R(RU)))
						;
qefmax(Y,P,T,Z,SSM)..
					e_f(Y,P,T,Z,SSM)
					=l=
						e_cap(Y,Z,SSM) - (S_DATA(SSM,'EFF_C')/100)*
						#p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN') - (S_DATA(SSM,'EFF_C')/100)*
						(p_c(Y,P,T,Z,SSM)*T_MARKET
						+ sum(RD, res_s_c(Y,P,T,Z,RD,SSM)*T_R(RD)))
						;

qelstart(Y,P,T,Z,SSM)$(ord(T)=1)..
					e_l(Y,P,T,Z,SSM)
					=e=
						e(Y,P,Z,SSM)
						+ (W(P)-1)*sum(T_E, p_c(Y,P,T_E,Z,SSM)*(S_DATA(SSM,'EFF_C')/100) - p_d(Y,P,T_E,Z,SSM)/(S_DATA(SSM,'EFF_D')/100))
						;

qel(Y,P,T,Z,SSM)$(ord(T)<card(T))..
					e_l(Y,P,T+1,Z,SSM)
					=e=
						e_l(Y,P,T,Z,SSM)
						+ p_c(Y,P,T,Z,SSM)*(S_DATA(SSM,'EFF_C')/100)
						- p_d(Y,P,T,Z,SSM)/(S_DATA(SSM,'EFF_D')/100)
						;

qelmin(Y,P,T,Z,SSM)..
					e_l(Y,P,T,Z,SSM)
					=g=
						1/(S_DATA(SSM,'EFF_D')/100)*
						(p_d(Y,P,T,Z,SSM)*T_MARKET
						+ sum(RU, res_s_d(Y,P,T,Z,RU,SSM)*T_R(RU)))
						;
qelmax(Y,P,T,Z,SSM)..
					e_l(Y,P,T,Z,SSM)
					=l=
						e_cap(Y,Z,SSM) - (S_DATA(SSM,'EFF_C')/100)*
						#p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN') - (S_DATA(SSM,'EFF_C')/100)*
						(p_c(Y,P,T,Z,SSM)*T_MARKET
						+ sum(RD, res_s_c(Y,P,T,Z,RD,SSM)*T_R(RD)))
						;

#--Duration limits--#

qdurmin(Y,Z,SSM)..
					e_cap(Y,Z,SSM)
					#p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN')
					=g=
						p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN')
						;

qdurmax(Y,Z,SSM)..
					e_cap(Y,Z,SSM)
					#p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MIN')
					=l=
						p_cap_c(Y,Z,SSM)*S_DATA(SSM,'DUR_MAX')
						;

#-------Short-term storage-----------------------------------------------------#

#--Charging constraints--#

qssc(Y,P,T,Z,SS)$(ord(T)<card(T))..
					p_c(Y,P,T+1,Z,SS)
					=e=
						p_c(Y,P,T,Z,SS)
						+ ramp_c_up(Y,P,T,Z,SS)
                    	- ramp_c_dn(Y,P,T,Z,SS)
                    	;

qsscru(Y,P,T,Z,SS)..
                    ramp_c_up(Y,P,T,Z,SS)
                    + sum(RD, res_s_c(Y,P,T,Z,RD,SS))
                    =l=
                    	p_cap_c(Y,Z,SS)
                    	- p_c(Y,P,T,Z,SS)
                    	;

qsscrd(Y,P,T,Z,SS)..
                    ramp_c_dn(Y,P,T,Z,SS)
                    + sum(RU, res_s_c(Y,P,T,Z,RU,SS))
                    =l=
                    	p_c(Y,P,T,Z,SS)
                    	;

#--Discharging constraints--#

qssd(Y,P,T,Z,SS)$(ord(T)<card(T))..
                  	p_d(Y,P,T+1,Z,SS)
                  	=e=
                  		p_d(Y,P,T,Z,SS)
                  		+ ramp_d_up(Y,P,T,Z,SS)
                    	- ramp_d_dn(Y,P,T,Z,SS)
                    	;

qssdru(Y,P,T,Z,SS)..
                    ramp_d_up(Y,P,T,Z,SS)
                    + sum(RU, res_s_d(Y,P,T,Z,RU,SS))
                    =l=
                    	p_cap_c(Y,Z,SS)
                    	- p_d(Y,P,T,Z,SS)
                    	;

qssdrd(Y,P,T,Z,SS)..
                    ramp_d_dn(Y,P,T,Z,SS)
                    + sum(RD, res_s_d(Y,P,T,Z,RD,SS))
                    =l=
                    	p_d(Y,P,T,Z,SS)
                    	;

#-------Mid and long-term storage----------------------------------------------#

#--Reserve allocation--#

qresscu(Y,P,T,Z,RU,SML)..
					res_s_c(Y,P,T,Z,RU,SML)
					=e=
						res_s_c_s(Y,P,T,Z,RU,SML)
						+ res_s_c_sd(Y,P,T,Z,RU,SML)
						;

qresscd(Y,P,T,Z,RD,SML)..
					res_s_c(Y,P,T,Z,RD,SML)
					=e=
						res_s_c_s(Y,P,T,Z,RD,SML)
						+ res_s_c_ns(Y,P,T,Z,RD,SML)
						;

qressdu(Y,P,T,Z,RU,SM)..
					res_s_d(Y,P,T,Z,RU,SM)
					=e=
						res_s_d_s(Y,P,T,Z,RU,SM)
						+ res_s_d_ns(Y,P,T,Z,RU,SM)
						;

qressdd(Y,P,T,Z,RD,SM)..
					res_s_d(Y,P,T,Z,RD,SM)
					=e=
						res_s_d_s(Y,P,T,Z,RD,SM)
						+ res_s_d_sd(Y,P,T,Z,RD,SM)
						;

#--Charging logical constraints--#

qnc(Y,P,T,Z,SML)$(ord(T)<card(T))..
					n_c(Y,P,T+1,Z,SML)
					=e=
						n_c(Y,P,T,Z,SML)
						+ n_c_su(Y,P,T,Z,SML)
						- n_c_sd(Y,P,T,Z,SML)
						;

qncmax(Y,P,T,Z,SML)..
					n_c(Y,P,T,Z,SML)
					=l=
						p_cap_c(Y,Z,SML)/S_DATA(SML,'P_C_MAX')
						;

qncsu(Y,P,T,Z,SML)..
					n_c_su(Y,P,T,Z,SML)
					+ sum(RD, n_c_su_r(Y,P,T,Z,RD,SML))
					=l=
						p_cap_c(Y,Z,SML)/S_DATA(SML,'P_C_MAX')
						- n_c(Y,P,T,Z,SML)
						;

qncsd(Y,P,T,Z,SML)..
					n_c_sd(Y,P,T,Z,SML)
					+ sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML))
					=l=
						n_c(Y,P,T,Z,SML)
						;

#--Charging constraints--#

qsmlc(Y,P,T,Z,SML)$(ord(T)<card(T))..
                    p_c(Y,P,T+1,Z,SML)
                    =e=
                    	p_c(Y,P,T,Z,SML)
                    	+ ramp_c_up(Y,P,T,Z,SML)
                    	- ramp_c_dn(Y,P,T,Z,SML)
                    	+ ramp_c_su(Y,P,T,Z,SML)
                    	- ramp_c_sd(Y,P,T,Z,SML)
                    	;

qsmlcmin(Y,P,T,Z,SML)..
					p_c(Y,P,T,Z,SML)
					=g=
						n_c(Y,P,T,Z,SML)*S_DATA(SML,'P_C_MIN')
						;

qsmlcmax(Y,P,T,Z,SML)..
					p_c(Y,P,T,Z,SML)
					=l=
						n_c(Y,P,T,Z,SML)*S_DATA(SML,'P_C_MAX')
						;

#--Charging ramping constraints--#

qcrudyn(Y,P,T,Z,SML)..
                    ramp_c_up(Y,P,T,Z,SML)
                    + sum(RD, res_s_c_s(Y,P,T,Z,RD,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML))*S_DATA(SML,'RCH')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrucap(Y,P,T,Z,SML)..
                    ramp_c_up(Y,P,T,Z,SML)
                    + sum(RD, res_s_c_s(Y,P,T,Z,RD,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML))*S_DATA(SML,'P_C_MAX')
                    	- (p_c(Y,P,T,Z,SML)-ramp_c_sd(Y,P,T,Z,SML))
                    	;

qcrddyn(Y,P,T,Z,SML)..
                    ramp_c_dn(Y,P,T,Z,SML)
                    + sum(RU, res_s_c_s(Y,P,T,Z,RU,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML)-sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML)))*S_DATA(SML,'RCH')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrdcap(Y,P,T,Z,SML)..
                    ramp_c_dn(Y,P,T,Z,SML)
                    + sum(RU, res_s_c_s(Y,P,T,Z,RU,SML))
                    =l=
                    	(p_c(Y,P,T,Z,SML)-ramp_c_sd(Y,P,T,Z,SML)-sum(RU, res_s_c_sd(Y,P,T,Z,RU,SML)))
                    	- (n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML)-sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML)))*S_DATA(SML,'P_C_MIN')
                    	;

qcsumin(Y,P,T,Z,SML)..
					ramp_c_su(Y,P,T,Z,SML)
					=g=
						n_c_su(Y,P,T,Z,SML)*S_DATA(SML,'P_C_MIN')
						;

qcsumax(Y,P,T,Z,SML)..
					ramp_c_su(Y,P,T,Z,SML)
					=l=
						n_c_su(Y,P,T,Z,SML)*S_DATA(SML,'RCH')/100*S_DATA(SML,'P_C_MAX')
						;

qcsdmin(Y,P,T,Z,SML)..
					ramp_c_sd(Y,P,T,Z,SML)
					=g=
						n_c_sd(Y,P,T,Z,SML)*S_DATA(SML,'P_C_MIN')
						;

qcsdmax(Y,P,T,Z,SML)..
					ramp_c_sd(Y,P,T,Z,SML)
					=l=
						n_c_sd(Y,P,T,Z,SML)*S_DATA(SML,'RCH')/100*S_DATA(SML,'P_C_MAX')
						;

#--Reserve allocation constraints--#

qcruad(Y,P,T,Z,SML)..
                    sum(RDA, res_s_c_s(Y,P,T,Z,RDA,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML))*S_DATA(SML,'RCA')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrumd(Y,P,T,Z,SML)..
                    sum(RD, res_s_c_s(Y,P,T,Z,RD,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML))*S_DATA(SML,'RCM')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrdfu(Y,P,T,Z,SML)..
                    sum(RUF, res_s_c_s(Y,P,T,Z,RUF,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML)-sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML)))*S_DATA(SML,'RCF')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrdau(Y,P,T,Z,SML)..
                    sum(RUA, res_s_c_s(Y,P,T,Z,RUA,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML)-sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML)))*S_DATA(SML,'RCA')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrdmus(Y,P,T,Z,SML)..
                    sum(RU, res_s_c_s(Y,P,T,Z,RU,SML))
                    =l=
                    	(n_c(Y,P,T,Z,SML)-n_c_sd(Y,P,T,Z,SML)-sum(RU, n_c_sd_r(Y,P,T,Z,RU,SML)))*S_DATA(SML,'RCM')/100*S_DATA(SML,'P_C_MAX')
                    	;

qcrunsmin(Y,P,T,Z,RD,SML)..
					res_s_c_ns(Y,P,T,Z,RD,SML)
					=g=
						n_c_su_r(Y,P,T,Z,RD,SML)*S_DATA(SML,'P_C_MIN')
						;

qcrunsmax(Y,P,T,Z,RD,SML)..
					res_s_c_ns(Y,P,T,Z,RD,SML)
					=l=
						n_c_su_r(Y,P,T,Z,RD,SML)*RSC(RD,SML)/100*S_DATA(SML,'P_C_MAX')
						;

qcrdsdmin(Y,P,T,Z,RU,SML)..
					res_s_c_sd(Y,P,T,Z,RU,SML)
					=g=
						n_c_sd_r(Y,P,T,Z,RU,SML)*S_DATA(SML,'P_C_MIN')
						;

qcrdsdmax(Y,P,T,Z,RU,SML)..
					res_s_c_sd(Y,P,T,Z,RU,SML)
					=l=
						n_c_sd_r(Y,P,T,Z,RU,SML)*RSC(RU,SML)/100*S_DATA(SML,'P_C_MAX')
						;

#-------Mid-term storage-------------------------------------------------------#

qcapdeqcapc(Y,Z,SM)..
					p_cap_d(Y,Z,SM)
					=e=
						p_cap_c(Y,Z,SM)
						;

#--Discharging logical constraints--#

qnd(Y,P,T,Z,SM)$(ord(T)<card(T))..
					n_d(Y,P,T+1,Z,SM)
					=e=
						n_d(Y,P,T,Z,SM)
						+ n_d_su(Y,P,T,Z,SM)
						- n_d_sd(Y,P,T,Z,SM)
						;

qndmax(Y,P,T,Z,SM)..
					n_d(Y,P,T,Z,SM)
					=l=
						p_cap_d(Y,Z,SM)/S_DATA(SM,'P_D_MAX')
						;

qndsu(Y,P,T,Z,SM)..
					n_d_su(Y,P,T,Z,SM)
					+ sum(RU, n_d_su_r(Y,P,T,Z,RU,SM))
					=l=
						p_cap_d(Y,Z,SM)/S_DATA(SM,'P_D_MAX')
						- n_d(Y,P,T,Z,SM)
						;

qndsd(Y,P,T,Z,SM)..
					n_d_sd(Y,P,T,Z,SM)
					+ sum(RD, n_d_sd_r(Y,P,T,Z,RD,SM))
					=l=
						n_d(Y,P,T,Z,SM)
						;

#--Discharging constraints--#

qsmd(Y,P,T,Z,SM)$(ord(T)<card(T))..
                    p_d(Y,P,T+1,Z,SM)
                    =e=
                    	p_d(Y,P,T,Z,SM)
                    	+ ramp_d_up(Y,P,T,Z,SM)
                    	- ramp_d_dn(Y,P,T,Z,SM)
                    	+ ramp_d_su(Y,P,T,Z,SM)
                    	- ramp_d_sd(Y,P,T,Z,SM)
                    	;

qsmdmin(Y,P,T,Z,SM)..
					p_d(Y,P,T,Z,SM)
					=g=
						n_d(Y,P,T,Z,SM)*S_DATA(SM,'P_D_MIN')
						;

qsmdmax(Y,P,T,Z,SM)..
					p_d(Y,P,T,Z,SM)
					=l=
						n_d(Y,P,T,Z,SM)*S_DATA(SM,'P_D_MAX')
						;

#--Discharging ramping constraints--#

qdrudyn(Y,P,T,Z,SM)..
                    ramp_d_up(Y,P,T,Z,SM)
                    + sum(RU, res_s_d_s(Y,P,T,Z,RU,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM))*S_DATA(SM,'RDH')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrucap(Y,P,T,Z,SM)..
                    ramp_d_up(Y,P,T,Z,SM)
                    + sum(RU, res_s_d_s(Y,P,T,Z,RU,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM))*S_DATA(SM,'P_D_MAX')
                    	- (p_d(Y,P,T,Z,SM)-ramp_d_sd(Y,P,T,Z,SM))
                    	;

qdrddyn(Y,P,T,Z,SM)..
                    ramp_d_dn(Y,P,T,Z,SM)
                    + sum(RD, res_s_d_s(Y,P,T,Z,RD,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM)-sum(RD, n_d_sd_r(Y,P,T,Z,RD,SM)))*S_DATA(SM,'RDH')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrdcap(Y,P,T,Z,SM)..
                    ramp_d_dn(Y,P,T,Z,SM)
                    + sum(RD, res_s_d_s(Y,P,T,Z,RD,SM))
                    =l=
                    	(p_d(Y,P,T,Z,SM)-ramp_d_sd(Y,P,T,Z,SM)-sum(RD, res_s_d_sd(Y,P,T,Z,RD,SM)))
                    	- (n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM)-sum(RD, n_d_sd_r(Y,P,T,Z,RD,SM)))*S_DATA(SM,'P_D_MIN')
                    	;

qdsumin(Y,P,T,Z,SM)..
					ramp_d_su(Y,P,T,Z,SM)
					=g=
						n_d_su(Y,P,T,Z,SM)*S_DATA(SM,'P_D_MIN')
						;

qdsumax(Y,P,T,Z,SM)..
					ramp_d_su(Y,P,T,Z,SM)
					=l=
						n_d_su(Y,P,T,Z,SM)*S_DATA(SM,'RDH')/100*S_DATA(SM,'P_D_MAX')
						;

qdsdmin(Y,P,T,Z,SM)..
					ramp_d_sd(Y,P,T,Z,SM)
					=g=
						n_d_sd(Y,P,T,Z,SM)*S_DATA(SM,'P_D_MIN')
						;

qdsdmax(Y,P,T,Z,SM)..
					ramp_d_sd(Y,P,T,Z,SM)
					=l=
						n_d_sd(Y,P,T,Z,SM)*S_DATA(SM,'RDH')/100*S_DATA(SM,'P_D_MAX')
						;

#--Reserve allocation constraints--#

qdrufu(Y,P,T,Z,SM)..
                    sum(RUF, res_s_d_s(Y,P,T,Z,RUF,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM))*S_DATA(SM,'RDF')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdruau(Y,P,T,Z,SM)..
                    sum(RUA, res_s_d_s(Y,P,T,Z,RUA,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM))*S_DATA(SM,'RDA')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrumus(Y,P,T,Z,SM)..
                    sum(RU, res_s_d_s(Y,P,T,Z,RU,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM))*S_DATA(SM,'RDM')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrdad(Y,P,T,Z,SM)..
                    sum(RDA, res_s_d_s(Y,P,T,Z,RDA,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM)-sum(RD, n_d_sd_r(Y,P,T,Z,RD,SM)))*S_DATA(SM,'RDA')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrdmd(Y,P,T,Z,SM)..
                    sum(RD, res_s_d_s(Y,P,T,Z,RD,SM))
                    =l=
                    	(n_d(Y,P,T,Z,SM)-n_d_sd(Y,P,T,Z,SM)-sum(RD, n_d_sd_r(Y,P,T,Z,RD,SM)))*S_DATA(SM,'RDM')/100*S_DATA(SM,'P_D_MAX')
                    	;

qdrunsmin(Y,P,T,Z,RU,SM)..
					res_s_d_ns(Y,P,T,Z,RU,SM)
					=g=
						n_d_su_r(Y,P,T,Z,RU,SM)*S_DATA(SM,'P_D_MIN')
						;

qdrunsmax(Y,P,T,Z,RU,SM)..
					res_s_d_ns(Y,P,T,Z,RU,SM)
					=l=
						n_d_su_r(Y,P,T,Z,RU,SM)*RSD(RU,SM)/100*S_DATA(SM,'P_D_MAX')
						;

qdrdsdmin(Y,P,T,Z,RD,SM)..
					res_s_d_sd(Y,P,T,Z,RD,SM)
					=g=
						n_d_sd_r(Y,P,T,Z,RD,SM)*S_DATA(SM,'P_D_MIN')
						;

qdrdsdmax(Y,P,T,Z,RD,SM)..
					res_s_d_sd(Y,P,T,Z,RD,SM)
					=l=
						n_d_sd_r(Y,P,T,Z,RD,SM)*RSD(RD,SM)/100*S_DATA(SM,'P_D_MAX')
						;

#-------Long-term storage------------------------------------------------------#

#--Discharging reserve allocation--#

qslressd(Y,P,T,Z,R,SL)..
					res_s_d(Y,P,T,Z,R,SL)
					=e=
						0
						;

#--Gas energy balance--#

qgase(Y,P,C)..
					eg(Y,P++1,C)
					=e=
						eg(Y,P,C)
						+ W(P)*sum(T_E, pg_c(Y,P,T_E,C) - pg_d(Y,P,T_E,C))
						;

qgasemax(Y,P,C)..
					eg(Y,P,C)
					=l=
						E_LP
						+ eg_cap
						;

qgasef(Y,P,T,C)$(ord(T)<card(T))..
					eg_f(Y,P,T+1,C)
					=e=
						eg_f(Y,P,T,C)
						+ pg_c(Y,P,T,C)
						- pg_d(Y,P,T,C)
						;

qgasefmax(Y,P,T,C)..
					eg_f(Y,P,T,C)
					=l=
						E_LP
						+ eg_cap
						;

qgasefstart(Y,P,T,C)$(ord(T)=1)..
					eg_f(Y,P,T,C)
					=e=
						eg(Y,P,C)
						;

qgasel(Y,P,T,C)$(ord(T)<card(T))..
					eg_l(Y,P,T+1,C)
					=e=
						eg_l(Y,P,T,C)
						+ pg_c(Y,P,T,C)
						- pg_d(Y,P,T,C)
						;

qgaselmax(Y,P,T,C)..
					eg_l(Y,P,T,C)
					=l=
						E_LP
						+ eg_cap
						;

qgaselstart(Y,P,T,C)$(ord(T)=1)..
					eg_l(Y,P,T,C)
					=e=
						eg(Y,P,C)
						+ (W(P)-1)*sum(T_E, pg_c(Y,P,T_E,C) - pg_d(Y,P,T_E,C))
						;

#--Gas charging constraints--#

qgasc(Y,P,T,C)..
					pg_c(Y,P,T,C)
					=e=
						sum(Z $ C_Z(C,Z), sum(SL, p_c(Y,P,T,Z,SL)*(S_DATA(SL,'EFF_C')/100)))
						+ pg_import(Y,P,T,C)
						;

#--Gas discharging constraints--#

qgasd(Y,P,T,C)..
					pg_d(Y,P,T,C)
					=e=
						sum(Z $ C_Z(C,Z), sum(GCG, pg_syn(Y,P,T,Z,GCG) + pg_fos(Y,P,T,Z,GCG)))
						;

#--Gas usage--#

qgasuse(Y,C)..
					sum(Z $ C_Z(C,Z), sum((GCG,P,T), pg_syn(Y,P,T,Z,GCG)))
					=l=
						sum(Z $ C_Z(C,Z), sum((SL,P,T), p_c(Y,P,T,Z,SL)*(S_DATA(SL,'EFF_C')/100)))
						;

qgasusegen(Y,P,T,Z,GCG)..
					gen(Y,P,T,Z,GCG)/(G_DATA(GCG,'EFF')/100)
					=e=
						pg_syn(Y,P,T,Z,GCG)
						+ pg_fos(Y,P,T,Z,GCG)
						;

################################################
################################################

demand(P,T,Z)..
					demand_unit(P,T,Z) =e= DEM_T(P,T,Z) + sum(H,ELAST_NEW(P,T,H)*(DEM_T(P,T,Z)/P_REF)*(price_unit(P,H,Z)-P_REF))
					;

demand_clone(P,H,Z)..
					demand_unit_clone(P,H,Z) =e= sum(T,demand_unit(P,T,Z)*DIAG(T,H))
					;

totdemand(P,Z)..
#					sum(T,DEM_T(P,T,Z)) =l= sum(T,demand_unit(P,T,Z))
					sum(T,DEM_T(P,T,Z)+eff_factor_earlier*sum(H,DIAG(T,H)*(front_up(P,H,Z)-back_down(P,H,Z)))) =l= demand_tot(P,Z)
					;

surplusdemand(P,T,Z)..
					surplus(P,T,Z) =e= eff_factor_earlier*sum(H,DIAG(T,H)*(front_up(P,H,Z)-back_down(P,H,Z)))
					;

totdemand2(P,Z)..
					demand_tot(P,Z) =e= sum(T,demand_unit(P,T,Z))
#					demand_tot(P,Z) =e= sum(T,DEM_T(P,T,Z))
					;

#price(P,H,Z)..
#					(price_unit(P,H,Z) - P_REF)*sum(H,ELAST(T,H)*(DEM_T(P,T,Z)/P_REF)) =e= (demand_unit(P,T,Z)-DEM_T(P,T,Z))
#					;

price_clone(P,T,Z)..
					price_unit_clone(P,T,Z) =e= sum(H,price_unit(P,H,Z)*DIAG(T,H))
					;

refdemand(P,T,Z)..
					demand_ref(P,T,Z) =e= DEM_T(P,T,Z)
					;

shiftedaway(P,H,Z)..
					shiftaway(P,H,Z) =e= sum(T,DIAG(T,H)*ELAST_NEW(P,T,H)*DEM_T(P,T,Z)*(price_unit(P,H,Z)-P_REF)/P_REF)
					;

shiftedawaytotal(P,Z)..
					shiftaway_total(P,Z) =e= sum(H,shift_up(P,H,Z)-shift_down(P,H,Z))
					;

shiftedforward(P,H,Z)..
					shiftforwards(P,H,Z) =e= sum(T,TRI_UP(T,H)*ELAST_NEW(P,T,H)*DEM_T(P,T,Z)*(price_unit(P,H,Z)-P_REF)/P_REF)
					;

shiftedforwardtotal(P,Z)..
#					shiftforwards_total(P,Z) =e= sum(H,shiftforwards(P,H,Z))
					shiftforwards_total(P,Z) =e= sum(H,front_up(P,H,Z)-back_down(P,H,Z))
					;

shiftedbackward(P,H,Z)..
					shiftbackwards(P,H,Z) =e= sum(T,TRI_LOW(T,H)*ELAST_NEW(P,T,H)*DEM_T(P,T,Z)*(price_unit(P,H,Z)-P_REF)/P_REF)
					;

shiftedbackwardtotal(P,Z)..
#					shiftbackwards_total(P,Z) =e= sum(H,shiftbackwards(P,H,Z))
					shiftbackwards_total(P,Z) =e= sum(H,back_up(P,H,Z)-front_down(P,H,Z))
					;

shiftconstraint_frame_1(P,H,Z)..
					sum(T,DEM_T(P,T,Z)*SHIFTMIN(H,T)) =l= sum(T,demand_unit(P,T,Z)*SHIFTMAX(H,T))
					;

shiftconstraint_frame_2(P,H,Z)..
					sum(T,DEM_T(P,T,Z)*SHIFTMAX(H,T)) =g= sum(T,demand_unit(P,T,Z)*SHIFTMIN(H,T))
					;

shiftconstraint1(P,H,Z)..
					shiftaway(P,H,Z) =l= LIMITSHIFT
					;

shiftconstraint2(P,H,Z)..
					shiftaway(P,H,Z) =g= -LIMITSHIFT
					;

priceconstraint1(P,T,Z)..
					price_unit_clone(P,T,Z) =l= P_REF + LIMITPRICE
					;

priceconstraint2(P,T,Z)..
					price_unit_clone(P,T,Z) =g= P_REF - LIMITPRICE
					;

demlimitunder(P,T,Z)..
					DEM_T(P,T,Z) - LIMITDEM =l= demand_unit(P,T,Z)
					;

demlimitupper(P,T,Z)..
					DEM_T(P,T,Z) + LIMITDEM =g= demand_unit(P,T,Z)
					;


#priceconstraint3(P,Z)..
#					sum(T,price_unit(P,T,Z))/card(T) =e= P_REF
#					;


qinnerframe(P,H,Z)..
					innerframe(P,H,Z) =e= sum(T,DEM_T(P,T,Z)*SHIFTMIN(H,T))
					;

qouterframe(P,H,Z)..
					outerframe(P,H,Z) =e= sum(T,demand_unit(P,T,Z)*SHIFTMAX(H,T))
					;

fixedcost(Z)..
					totalfixedcost(Z) =e= sum((Y,G), (G_DATA(G,'C_INV') + G_DATA(G,'C_FOM'))*1000*cap(Y,Z,G))
					;

variablecost(P,Z)..
					totalvariablecost(P,Z) =e= (sum((Y,T,G), W(P)*(G_DATA(G,'C_VOM'))*gen(Y,P,T,Z,G))
					+ sum((Y,T,GC), W(P)*(G_DATA(GC,'C_FUEL'))*gen(Y,P,T,Z,GC)))*(168/card(T))
					;

cost(Z)..
					totalcost(Z) =e= sum(P,totalvariablecost(P,Z)) + totalfixedcost(Z)
					;

####################################
# get downwards en upward numbers for front and back
####################################

front_d_1(P,H,Z)..
					front_down(P,H,Z) =l= shiftforwards(P,H,Z)
					;

front_d_2(P,H,Z)..
					front_down(P,H,Z) =l= 0
					;

front_u_1(P,H,Z)..
					front_up(P,H,Z) =g= shiftforwards(P,H,Z)
					;

front_u_2(P,H,Z)..
					front_up(P,H,Z) =g= 0
					;

back_d_1(P,H,Z)..
					back_down(P,H,Z) =l= shiftbackwards(P,H,Z)
					;

back_d_2(P,H,Z)..
					back_down(P,H,Z) =l= 0
					;

back_u_1(P,H,Z)..
					back_up(P,H,Z) =g= shiftbackwards(P,H,Z)
					;

back_u_2(P,H,Z)..
					back_up(P,H,Z) =g= 0
					;

shift_d_1(P,H,Z)..
					shift_down(P,H,Z) =l= shiftaway(P,H,Z)
					;

shift_d_2(P,H,Z)..
					shift_down(P,H,Z) =l= 0
					;

shift_u_1(P,H,Z)..
					shift_up(P,H,Z) =g= shiftaway(P,H,Z)
					;

shift_u_2(P,H,Z)..
					shift_up(P,H,Z) =g= 0
					;



MODEL GOA GOA model /

#-------Objective function-----------------------------------------------------#
		qobj

#-------System constraints-----------------------------------------------------#
		qbalance

		qresprod
		qco2lim

		qresendomin
		qresendomax
		qres

		#qgendisp
		#qgendisppeak

		qco2
		qlcg

#-------Generation technologies------------------------------------------------#
		qpotcapmin
#		qpotcapmax
#		qpotgenmin
#		qpotgenmax

#--Conventional generation technologies--#
		qresgcu
		qresgcd

		qn
		qnmax
		qnsu
		qnsd

		qgen
		qgenmin
		qgenmax

		qrudyn
		qrucap
		qrddyn
		qrdcap
		qsumin
		qsumax
		qsdmin
		qsdmax

		qrufu
		qruau
		qrumus
		qrdad
		qrdmd
		qrunsmin
		qrunsmax
		qrdsdmin
		qrdsdmax

#--Intermittent renewable generation technologies--#
		qresgru

		qgenr

		qresgrdr
		qresgrdg

#-------Storage technologies---------------------------------------------------#
#--General constraints--#
		qress
		qspotcapmin
		qspotcapmax

		qe
		qemax
		qef
		qefmin
		qefmax
		qefstart
		qel
		qelmin
		qelmax
		qelstart

		qdurmin
		qdurmax

#--Short-term storage--#
		qssc
		qsscru
		qsscrd

		qssd
		qssdru
		qssdrd

#--Mid and long-term storage--#
		qresscu
		qresscd
		qressdu
		qressdd

		qnc
		qncmax
		qncsu
		qncsd

		qsmlc
		qsmlcmin
		qsmlcmax

		qcrudyn
		qcrucap
		qcrddyn
		qcrdcap
		qcsumin
		qcsumax
		qcsdmin
		qcsdmax

		qcruad
		qcrumd
		qcrdfu
		qcrdau
		qcrdmus
		qcrunsmin
		qcrunsmax
		qcrdsdmin
		qcrdsdmax

#--Mid-term storage--#
		qcapdeqcapc

		qnd
		qndmax
		qndsu
		qndsd

		qsmd
		qsmdmin
		qsmdmax

		qdrudyn
		qdrucap
		qdrddyn
		qdrdcap
		qdsumin
		qdsumax
		qdsdmin
		qdsdmax

		qdrufu
		qdruau
		qdrumus
		qdrdad
		qdrdmd
		qdrunsmin
		qdrunsmax
		qdrdsdmin
		qdrdsdmax

#--Long-term storage--#
		qslressd

		qgase
		qgasemax
		qgasef
		qgasefmax
		qgasefstart
		qgasel
		qgaselmax
		qgaselstart

		qgasc

		qgasd

		qgasuse
		qgasusegen

#-- Price-elasticity--#

#		price
		price_clone
		demand
		demand_clone
		totdemand
		totdemand2
		refdemand

		shiftedaway
		shiftedforward
		shiftedbackward

		shiftedawaytotal
		shiftedforwardtotal
		shiftedbackwardtotal

		priceconstraint1
		priceconstraint2
#		priceconstraint3

        ##########
        # include when working with moving frames, and set in wout_program -> factor back to 1
		shiftconstraint_frame_1
		shiftconstraint_frame_2

		shiftconstraint1
		shiftconstraint2

		qinnerframe
		qouterframe

#		revenue
		fixedcost
		variablecost
		cost

		demlimitunder
		demlimitupper

		front_d_1
		front_d_2
		front_u_1
		front_u_2
		back_d_1
		back_d_2
		back_u_1
		back_u_2

		shift_u_1
		shift_u_2
		shift_d_1
		shift_d_2

		surplusdemand
/;



