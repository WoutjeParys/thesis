SOLVE GOA using lp minimizing obj;
parameter marg(Y,P,T,Z) shadow prices of production;
marg(Y,P,T,Z) = qbalance.m(Y,P,T,Z)/W(P);
parameter factor(P,H,Z) compensation to avoid energy losses;
factor(P,H,Z) = -shiftaway.l(P,H,Z)/(shiftforwards.l(P,H,Z)+shiftbackwards.l(P,H,Z)+0.00000001);
