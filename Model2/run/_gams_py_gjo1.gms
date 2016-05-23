POL_TARGETS('RES_SHARE', '2050') = 60;
LIMITPRICE = 1.5;
FACTOR_RES_DR = 0;
SOLVE GOA using lp minimizing obj;
parameter marg(Y,P,T,Z) shadow prices of production;
marg(Y,P,T,Z) = qbalance.m(Y,P,T,Z)/W(P);
parameter ratio(P,H,Z) inbalance ratio;
ratio(P,H,Z) = (-shiftaway.l(P,H,Z)-shiftfi.l(P,H,Z)-shiftbi.l(P,H,Z))/(shiftfc.l(P,H,Z)+shiftbc.l(P,H,Z)+0.00000001);
