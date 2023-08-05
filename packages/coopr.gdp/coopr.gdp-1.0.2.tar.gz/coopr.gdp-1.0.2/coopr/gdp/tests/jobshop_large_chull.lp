min 
makespan:
+1.000000 ms

s.t.

c_u_Feas(A)_:
-1.000000 ms
+1.000000 t(A)
<= -10

c_u_Feas(B)_:
-1.000000 ms
+1.000000 t(B)
<= -10

c_u_Feas(C)_:
-1.000000 ms
+1.000000 t(C)
<= -15

c_u_Feas(D)_:
-1.000000 ms
+1.000000 t(D)
<= -14

c_u_Feas(E)_:
-1.000000 ms
+1.000000 t(E)
<= -12

c_u_Feas(F)_:
-1.000000 ms
+1.000000 t(F)
<= -14

c_u_Feas(G)_:
-1.000000 ms
+1.000000 t(G)
<= -17

c_u_NoClash_(E,F,3,1)_c_hi_:
+8.000000 NoClash_(E,F,3,1)_indicator_var
+1.000000 NoClash_(E,F,3,1)_t(E)
-1.000000 NoClash_(E,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(B,E,3,0)_c_hi_:
+7.000000 NoClash_(B,E,3,0)_indicator_var
-1.000000 NoClash_(B,E,3,0)_t(B)
+1.000000 NoClash_(B,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(E,F,3,0)_c_hi_:
+3.000000 NoClash_(E,F,3,0)_indicator_var
-1.000000 NoClash_(E,F,3,0)_t(E)
+1.000000 NoClash_(E,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(D,G,2,1)_c_hi_:
+8.000000 NoClash_(D,G,2,1)_indicator_var
+1.000000 NoClash_(D,G,2,1)_t(D)
-1.000000 NoClash_(D,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(F,G,4,1)_c_hi_:
+6.000000 NoClash_(F,G,4,1)_indicator_var
+1.000000 NoClash_(F,G,4,1)_t(F)
-1.000000 NoClash_(F,G,4,1)_t(G)
<= 0.0

c_u_NoClash_(C,E,2,1)_c_hi_:
+9.000000 NoClash_(C,E,2,1)_indicator_var
+1.000000 NoClash_(C,E,2,1)_t(C)
-1.000000 NoClash_(C,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(E,G,2,0)_c_hi_:
+8.000000 NoClash_(E,G,2,0)_indicator_var
-1.000000 NoClash_(E,G,2,0)_t(E)
+1.000000 NoClash_(E,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(A,D,3,1)_c_hi_:
+1.000000 NoClash_(A,D,3,1)_t(A)
-1.000000 NoClash_(A,D,3,1)_t(D)
<= 0.0

c_u_NoClash_(D,E,3,1)_c_hi_:
+9.000000 NoClash_(D,E,3,1)_indicator_var
+1.000000 NoClash_(D,E,3,1)_t(D)
-1.000000 NoClash_(D,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(C,D,2,0)_c_hi_:
+2.000000 NoClash_(C,D,2,0)_indicator_var
-1.000000 NoClash_(C,D,2,0)_t(C)
+1.000000 NoClash_(C,D,2,0)_t(D)
<= 0.0

c_u_NoClash_(B,D,3,1)_c_hi_:
-1.000000 NoClash_(B,D,3,1)_indicator_var
+1.000000 NoClash_(B,D,3,1)_t(B)
-1.000000 NoClash_(B,D,3,1)_t(D)
<= 0.0

c_u_NoClash_(B,G,2,0)_c_hi_:
+8.000000 NoClash_(B,G,2,0)_indicator_var
-1.000000 NoClash_(B,G,2,0)_t(B)
+1.000000 NoClash_(B,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(A,B,3,0)_c_hi_:
+4.000000 NoClash_(A,B,3,0)_indicator_var
-1.000000 NoClash_(A,B,3,0)_t(A)
+1.000000 NoClash_(A,B,3,0)_t(B)
<= 0.0

c_u_NoClash_(B,C,2,1)_c_hi_:
-3.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(B)
-1.000000 NoClash_(B,C,2,1)_t(C)
<= 0.0

c_u_NoClash_(A,E,5,1)_c_hi_:
+1.000000 NoClash_(A,E,5,1)_t(A)
-1.000000 NoClash_(A,E,5,1)_t(E)
<= 0.0

c_u_NoClash_(C,D,4,1)_c_hi_:
+2.000000 NoClash_(C,D,4,1)_indicator_var
+1.000000 NoClash_(C,D,4,1)_t(C)
-1.000000 NoClash_(C,D,4,1)_t(D)
<= 0.0

c_u_NoClash_(B,G,5,0)_c_hi_:
+10.000000 NoClash_(B,G,5,0)_indicator_var
-1.000000 NoClash_(B,G,5,0)_t(B)
+1.000000 NoClash_(B,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(A,G,5,0)_c_hi_:
+9.000000 NoClash_(A,G,5,0)_indicator_var
-1.000000 NoClash_(A,G,5,0)_t(A)
+1.000000 NoClash_(A,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(D,F,3,1)_c_hi_:
+11.000000 NoClash_(D,F,3,1)_indicator_var
+1.000000 NoClash_(D,F,3,1)_t(D)
-1.000000 NoClash_(D,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(D,E,2,0)_c_hi_:
+4.000000 NoClash_(D,E,2,0)_indicator_var
-1.000000 NoClash_(D,E,2,0)_t(D)
+1.000000 NoClash_(D,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(C,F,1,1)_c_hi_:
+6.000000 NoClash_(C,F,1,1)_indicator_var
+1.000000 NoClash_(C,F,1,1)_t(C)
-1.000000 NoClash_(C,F,1,1)_t(F)
<= 0.0

c_u_NoClash_(D,E,3,0)_c_hi_:
+2.000000 NoClash_(D,E,3,0)_indicator_var
-1.000000 NoClash_(D,E,3,0)_t(D)
+1.000000 NoClash_(D,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(B,F,3,0)_c_hi_:
+4.000000 NoClash_(B,F,3,0)_indicator_var
-1.000000 NoClash_(B,F,3,0)_t(B)
+1.000000 NoClash_(B,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(C,E,2,0)_c_hi_:
-2.000000 NoClash_(C,E,2,0)_indicator_var
-1.000000 NoClash_(C,E,2,0)_t(C)
+1.000000 NoClash_(C,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(A,D,3,0)_c_hi_:
+10.000000 NoClash_(A,D,3,0)_indicator_var
-1.000000 NoClash_(A,D,3,0)_t(A)
+1.000000 NoClash_(A,D,3,0)_t(D)
<= 0.0

c_u_NoClash_(C,G,4,1)_c_hi_:
+7.000000 NoClash_(C,G,4,1)_indicator_var
+1.000000 NoClash_(C,G,4,1)_t(C)
-1.000000 NoClash_(C,G,4,1)_t(G)
<= 0.0

c_u_NoClash_(C,D,2,1)_c_hi_:
+9.000000 NoClash_(C,D,2,1)_indicator_var
+1.000000 NoClash_(C,D,2,1)_t(C)
-1.000000 NoClash_(C,D,2,1)_t(D)
<= 0.0

c_u_NoClash_(C,F,4,0)_c_hi_:
+5.000000 NoClash_(C,F,4,0)_indicator_var
-1.000000 NoClash_(C,F,4,0)_t(C)
+1.000000 NoClash_(C,F,4,0)_t(F)
<= 0.0

c_u_NoClash_(B,G,2,1)_c_hi_:
+3.000000 NoClash_(B,G,2,1)_indicator_var
+1.000000 NoClash_(B,G,2,1)_t(B)
-1.000000 NoClash_(B,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(E,G,5,0)_c_hi_:
+7.000000 NoClash_(E,G,5,0)_indicator_var
-1.000000 NoClash_(E,G,5,0)_t(E)
+1.000000 NoClash_(E,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(A,B,5,0)_c_hi_:
+2.000000 NoClash_(A,B,5,0)_indicator_var
-1.000000 NoClash_(A,B,5,0)_t(A)
+1.000000 NoClash_(A,B,5,0)_t(B)
<= 0.0

c_u_NoClash_(C,G,2,1)_c_hi_:
+9.000000 NoClash_(C,G,2,1)_indicator_var
+1.000000 NoClash_(C,G,2,1)_t(C)
-1.000000 NoClash_(C,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(B,E,5,1)_c_hi_:
+1.000000 NoClash_(B,E,5,1)_t(B)
-1.000000 NoClash_(B,E,5,1)_t(E)
<= 0.0

c_u_NoClash_(B,D,2,1)_c_hi_:
+3.000000 NoClash_(B,D,2,1)_indicator_var
+1.000000 NoClash_(B,D,2,1)_t(B)
-1.000000 NoClash_(B,D,2,1)_t(D)
<= 0.0

c_u_NoClash_(B,E,2,0)_c_hi_:
+4.000000 NoClash_(B,E,2,0)_indicator_var
-1.000000 NoClash_(B,E,2,0)_t(B)
+1.000000 NoClash_(B,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(A,B,5,1)_c_hi_:
+3.000000 NoClash_(A,B,5,1)_indicator_var
+1.000000 NoClash_(A,B,5,1)_t(A)
-1.000000 NoClash_(A,B,5,1)_t(B)
<= 0.0

c_u_NoClash_(D,F,4,0)_c_hi_:
+1.000000 NoClash_(D,F,4,0)_indicator_var
-1.000000 NoClash_(D,F,4,0)_t(D)
+1.000000 NoClash_(D,F,4,0)_t(F)
<= 0.0

c_u_NoClash_(A,F,1,1)_c_hi_:
+3.000000 NoClash_(A,F,1,1)_indicator_var
+1.000000 NoClash_(A,F,1,1)_t(A)
-1.000000 NoClash_(A,F,1,1)_t(F)
<= 0.0

c_u_NoClash_(A,G,5,1)_c_hi_:
-3.000000 NoClash_(A,G,5,1)_indicator_var
+1.000000 NoClash_(A,G,5,1)_t(A)
-1.000000 NoClash_(A,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(D,F,4,1)_c_hi_:
+7.000000 NoClash_(D,F,4,1)_indicator_var
+1.000000 NoClash_(D,F,4,1)_t(D)
-1.000000 NoClash_(D,F,4,1)_t(F)
<= 0.0

c_u_NoClash_(D,E,2,1)_c_hi_:
+8.000000 NoClash_(D,E,2,1)_indicator_var
+1.000000 NoClash_(D,E,2,1)_t(D)
-1.000000 NoClash_(D,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(A,E,3,0)_c_hi_:
+7.000000 NoClash_(A,E,3,0)_indicator_var
-1.000000 NoClash_(A,E,3,0)_t(A)
+1.000000 NoClash_(A,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(D,G,4,0)_c_hi_:
-1.000000 NoClash_(D,G,4,0)_t(D)
+1.000000 NoClash_(D,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(C,F,1,0)_c_hi_:
+2.000000 NoClash_(C,F,1,0)_indicator_var
-1.000000 NoClash_(C,F,1,0)_t(C)
+1.000000 NoClash_(C,F,1,0)_t(F)
<= 0.0

c_u_NoClash_(A,F,3,1)_c_hi_:
+6.000000 NoClash_(A,F,3,1)_indicator_var
+1.000000 NoClash_(A,F,3,1)_t(A)
-1.000000 NoClash_(A,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(B,E,3,1)_c_hi_:
+3.000000 NoClash_(B,E,3,1)_indicator_var
+1.000000 NoClash_(B,E,3,1)_t(B)
-1.000000 NoClash_(B,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(B,F,3,1)_c_hi_:
+5.000000 NoClash_(B,F,3,1)_indicator_var
+1.000000 NoClash_(B,F,3,1)_t(B)
-1.000000 NoClash_(B,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(D,G,2,0)_c_hi_:
+8.000000 NoClash_(D,G,2,0)_indicator_var
-1.000000 NoClash_(D,G,2,0)_t(D)
+1.000000 NoClash_(D,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(C,G,4,0)_c_hi_:
+4.000000 NoClash_(C,G,4,0)_indicator_var
-1.000000 NoClash_(C,G,4,0)_t(C)
+1.000000 NoClash_(C,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(F,G,4,0)_c_hi_:
+6.000000 NoClash_(F,G,4,0)_indicator_var
-1.000000 NoClash_(F,G,4,0)_t(F)
+1.000000 NoClash_(F,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(E,G,2,1)_c_hi_:
+4.000000 NoClash_(E,G,2,1)_indicator_var
+1.000000 NoClash_(E,G,2,1)_t(E)
-1.000000 NoClash_(E,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(C,F,4,1)_c_hi_:
+8.000000 NoClash_(C,F,4,1)_indicator_var
+1.000000 NoClash_(C,F,4,1)_t(C)
-1.000000 NoClash_(C,F,4,1)_t(F)
<= 0.0

c_u_NoClash_(B,C,2,0)_c_hi_:
+9.000000 NoClash_(B,C,2,0)_indicator_var
-1.000000 NoClash_(B,C,2,0)_t(B)
+1.000000 NoClash_(B,C,2,0)_t(C)
<= 0.0

c_u_NoClash_(E,G,5,1)_c_hi_:
-1.000000 NoClash_(E,G,5,1)_indicator_var
+1.000000 NoClash_(E,G,5,1)_t(E)
-1.000000 NoClash_(E,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(B,D,3,0)_c_hi_:
+10.000000 NoClash_(B,D,3,0)_indicator_var
-1.000000 NoClash_(B,D,3,0)_t(B)
+1.000000 NoClash_(B,D,3,0)_t(D)
<= 0.0

c_u_NoClash_(C,G,2,0)_c_hi_:
+2.000000 NoClash_(C,G,2,0)_indicator_var
-1.000000 NoClash_(C,G,2,0)_t(C)
+1.000000 NoClash_(C,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(A,B,3,1)_c_hi_:
+5.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(A)
-1.000000 NoClash_(A,B,3,1)_t(B)
<= 0.0

c_u_NoClash_(B,E,5,0)_c_hi_:
+5.000000 NoClash_(B,E,5,0)_indicator_var
-1.000000 NoClash_(B,E,5,0)_t(B)
+1.000000 NoClash_(B,E,5,0)_t(E)
<= 0.0

c_u_NoClash_(B,D,2,0)_c_hi_:
+8.000000 NoClash_(B,D,2,0)_indicator_var
-1.000000 NoClash_(B,D,2,0)_t(B)
+1.000000 NoClash_(B,D,2,0)_t(D)
<= 0.0

c_u_NoClash_(A,E,5,0)_c_hi_:
+4.000000 NoClash_(A,E,5,0)_indicator_var
-1.000000 NoClash_(A,E,5,0)_t(A)
+1.000000 NoClash_(A,E,5,0)_t(E)
<= 0.0

c_u_NoClash_(C,D,4,0)_c_hi_:
+5.000000 NoClash_(C,D,4,0)_indicator_var
-1.000000 NoClash_(C,D,4,0)_t(C)
+1.000000 NoClash_(C,D,4,0)_t(D)
<= 0.0

c_u_NoClash_(B,E,2,1)_c_hi_:
+3.000000 NoClash_(B,E,2,1)_indicator_var
+1.000000 NoClash_(B,E,2,1)_t(B)
-1.000000 NoClash_(B,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(A,F,1,0)_c_hi_:
+2.000000 NoClash_(A,F,1,0)_indicator_var
-1.000000 NoClash_(A,F,1,0)_t(A)
+1.000000 NoClash_(A,F,1,0)_t(F)
<= 0.0

c_u_NoClash_(A,C,1,0)_c_hi_:
+6.000000 NoClash_(A,C,1,0)_indicator_var
-1.000000 NoClash_(A,C,1,0)_t(A)
+1.000000 NoClash_(A,C,1,0)_t(C)
<= 0.0

c_u_NoClash_(B,G,5,1)_c_hi_:
-3.000000 NoClash_(B,G,5,1)_indicator_var
+1.000000 NoClash_(B,G,5,1)_t(B)
-1.000000 NoClash_(B,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(A,E,3,1)_c_hi_:
+4.000000 NoClash_(A,E,3,1)_indicator_var
+1.000000 NoClash_(A,E,3,1)_t(A)
-1.000000 NoClash_(A,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(A,C,1,1)_c_hi_:
+3.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(A)
-1.000000 NoClash_(A,C,1,1)_t(C)
<= 0.0

c_u_NoClash_(D,G,4,1)_c_hi_:
+6.000000 NoClash_(D,G,4,1)_indicator_var
+1.000000 NoClash_(D,G,4,1)_t(D)
-1.000000 NoClash_(D,G,4,1)_t(G)
<= 0.0

c_u_NoClash_(D,F,3,0)_c_hi_:
-1.000000 NoClash_(D,F,3,0)_indicator_var
-1.000000 NoClash_(D,F,3,0)_t(D)
+1.000000 NoClash_(D,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(A,F,3,0)_c_hi_:
+4.000000 NoClash_(A,F,3,0)_indicator_var
-1.000000 NoClash_(A,F,3,0)_t(A)
+1.000000 NoClash_(A,F,3,0)_t(F)
<= 0.0

c_e_disj(_A_,_B_,3)_:
+1.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,1)_indicator_var
= 1.0

c_e_disj(_A_,_B_,5)_:
+1.000000 NoClash_(A,B,5,0)_indicator_var
+1.000000 NoClash_(A,B,5,1)_indicator_var
= 1.0

c_e_disj(_A_,_C_,1)_:
+1.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,1)_indicator_var
= 1.0

c_e_disj(_A_,_D_,3)_:
+1.000000 NoClash_(A,D,3,0)_indicator_var
+1.000000 NoClash_(A,D,3,1)_indicator_var
= 1.0

c_e_disj(_A_,_E_,3)_:
+1.000000 NoClash_(A,E,3,0)_indicator_var
+1.000000 NoClash_(A,E,3,1)_indicator_var
= 1.0

c_e_disj(_A_,_E_,5)_:
+1.000000 NoClash_(A,E,5,0)_indicator_var
+1.000000 NoClash_(A,E,5,1)_indicator_var
= 1.0

c_e_disj(_A_,_F_,1)_:
+1.000000 NoClash_(A,F,1,0)_indicator_var
+1.000000 NoClash_(A,F,1,1)_indicator_var
= 1.0

c_e_disj(_A_,_F_,3)_:
+1.000000 NoClash_(A,F,3,0)_indicator_var
+1.000000 NoClash_(A,F,3,1)_indicator_var
= 1.0

c_e_disj(_A_,_G_,5)_:
+1.000000 NoClash_(A,G,5,0)_indicator_var
+1.000000 NoClash_(A,G,5,1)_indicator_var
= 1.0

c_e_disj(_B_,_C_,2)_:
+1.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,1)_indicator_var
= 1.0

c_e_disj(_B_,_D_,2)_:
+1.000000 NoClash_(B,D,2,0)_indicator_var
+1.000000 NoClash_(B,D,2,1)_indicator_var
= 1.0

c_e_disj(_B_,_D_,3)_:
+1.000000 NoClash_(B,D,3,0)_indicator_var
+1.000000 NoClash_(B,D,3,1)_indicator_var
= 1.0

c_e_disj(_B_,_E_,2)_:
+1.000000 NoClash_(B,E,2,0)_indicator_var
+1.000000 NoClash_(B,E,2,1)_indicator_var
= 1.0

c_e_disj(_B_,_E_,3)_:
+1.000000 NoClash_(B,E,3,0)_indicator_var
+1.000000 NoClash_(B,E,3,1)_indicator_var
= 1.0

c_e_disj(_B_,_E_,5)_:
+1.000000 NoClash_(B,E,5,0)_indicator_var
+1.000000 NoClash_(B,E,5,1)_indicator_var
= 1.0

c_e_disj(_B_,_F_,3)_:
+1.000000 NoClash_(B,F,3,0)_indicator_var
+1.000000 NoClash_(B,F,3,1)_indicator_var
= 1.0

c_e_disj(_B_,_G_,2)_:
+1.000000 NoClash_(B,G,2,0)_indicator_var
+1.000000 NoClash_(B,G,2,1)_indicator_var
= 1.0

c_e_disj(_B_,_G_,5)_:
+1.000000 NoClash_(B,G,5,0)_indicator_var
+1.000000 NoClash_(B,G,5,1)_indicator_var
= 1.0

c_e_disj(_C_,_D_,2)_:
+1.000000 NoClash_(C,D,2,0)_indicator_var
+1.000000 NoClash_(C,D,2,1)_indicator_var
= 1.0

c_e_disj(_C_,_D_,4)_:
+1.000000 NoClash_(C,D,4,0)_indicator_var
+1.000000 NoClash_(C,D,4,1)_indicator_var
= 1.0

c_e_disj(_C_,_E_,2)_:
+1.000000 NoClash_(C,E,2,0)_indicator_var
+1.000000 NoClash_(C,E,2,1)_indicator_var
= 1.0

c_e_disj(_C_,_F_,1)_:
+1.000000 NoClash_(C,F,1,0)_indicator_var
+1.000000 NoClash_(C,F,1,1)_indicator_var
= 1.0

c_e_disj(_C_,_F_,4)_:
+1.000000 NoClash_(C,F,4,0)_indicator_var
+1.000000 NoClash_(C,F,4,1)_indicator_var
= 1.0

c_e_disj(_C_,_G_,2)_:
+1.000000 NoClash_(C,G,2,0)_indicator_var
+1.000000 NoClash_(C,G,2,1)_indicator_var
= 1.0

c_e_disj(_C_,_G_,4)_:
+1.000000 NoClash_(C,G,4,0)_indicator_var
+1.000000 NoClash_(C,G,4,1)_indicator_var
= 1.0

c_e_disj(_D_,_E_,2)_:
+1.000000 NoClash_(D,E,2,0)_indicator_var
+1.000000 NoClash_(D,E,2,1)_indicator_var
= 1.0

c_e_disj(_D_,_E_,3)_:
+1.000000 NoClash_(D,E,3,0)_indicator_var
+1.000000 NoClash_(D,E,3,1)_indicator_var
= 1.0

c_e_disj(_D_,_F_,3)_:
+1.000000 NoClash_(D,F,3,0)_indicator_var
+1.000000 NoClash_(D,F,3,1)_indicator_var
= 1.0

c_e_disj(_D_,_F_,4)_:
+1.000000 NoClash_(D,F,4,0)_indicator_var
+1.000000 NoClash_(D,F,4,1)_indicator_var
= 1.0

c_e_disj(_D_,_G_,2)_:
+1.000000 NoClash_(D,G,2,0)_indicator_var
+1.000000 NoClash_(D,G,2,1)_indicator_var
= 1.0

c_e_disj(_D_,_G_,4)_:
+1.000000 NoClash_(D,G,4,0)_indicator_var
+1.000000 NoClash_(D,G,4,1)_indicator_var
= 1.0

c_e_disj(_E_,_F_,3)_:
+1.000000 NoClash_(E,F,3,0)_indicator_var
+1.000000 NoClash_(E,F,3,1)_indicator_var
= 1.0

c_e_disj(_E_,_G_,2)_:
+1.000000 NoClash_(E,G,2,0)_indicator_var
+1.000000 NoClash_(E,G,2,1)_indicator_var
= 1.0

c_e_disj(_E_,_G_,5)_:
+1.000000 NoClash_(E,G,5,0)_indicator_var
+1.000000 NoClash_(E,G,5,1)_indicator_var
= 1.0

c_e_disj(_F_,_G_,4)_:
+1.000000 NoClash_(F,G,4,0)_indicator_var
+1.000000 NoClash_(F,G,4,1)_indicator_var
= 1.0

c_e_disj_(D,G,2)_t(D)_:
-1.000000 NoClash_(D,G,2,0)_t(D)
-1.000000 NoClash_(D,G,2,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,G,2)_t(G)_:
-1.000000 NoClash_(D,G,2,0)_t(G)
-1.000000 NoClash_(D,G,2,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(C,F,1)_t(C)_:
-1.000000 NoClash_(C,F,1,0)_t(C)
-1.000000 NoClash_(C,F,1,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,F,1)_t(F)_:
-1.000000 NoClash_(C,F,1,0)_t(F)
-1.000000 NoClash_(C,F,1,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(A,B,5)_t(A)_:
-1.000000 NoClash_(A,B,5,0)_t(A)
-1.000000 NoClash_(A,B,5,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,B,5)_t(B)_:
-1.000000 NoClash_(A,B,5,0)_t(B)
-1.000000 NoClash_(A,B,5,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(A,E,5)_t(A)_:
-1.000000 NoClash_(A,E,5,0)_t(A)
-1.000000 NoClash_(A,E,5,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,E,5)_t(E)_:
-1.000000 NoClash_(A,E,5,0)_t(E)
-1.000000 NoClash_(A,E,5,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(D,G,4)_t(D)_:
-1.000000 NoClash_(D,G,4,0)_t(D)
-1.000000 NoClash_(D,G,4,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,G,4)_t(G)_:
-1.000000 NoClash_(D,G,4,0)_t(G)
-1.000000 NoClash_(D,G,4,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(F,G,4)_t(F)_:
-1.000000 NoClash_(F,G,4,0)_t(F)
-1.000000 NoClash_(F,G,4,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(F,G,4)_t(G)_:
-1.000000 NoClash_(F,G,4,0)_t(G)
-1.000000 NoClash_(F,G,4,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(C,F,4)_t(C)_:
-1.000000 NoClash_(C,F,4,0)_t(C)
-1.000000 NoClash_(C,F,4,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,F,4)_t(F)_:
-1.000000 NoClash_(C,F,4,0)_t(F)
-1.000000 NoClash_(C,F,4,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(A,G,5)_t(A)_:
-1.000000 NoClash_(A,G,5,0)_t(A)
-1.000000 NoClash_(A,G,5,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,G,5)_t(G)_:
-1.000000 NoClash_(A,G,5,0)_t(G)
-1.000000 NoClash_(A,G,5,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(D,F,4)_t(D)_:
-1.000000 NoClash_(D,F,4,0)_t(D)
-1.000000 NoClash_(D,F,4,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,F,4)_t(F)_:
-1.000000 NoClash_(D,F,4,0)_t(F)
-1.000000 NoClash_(D,F,4,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(B,E,2)_t(B)_:
-1.000000 NoClash_(B,E,2,0)_t(B)
-1.000000 NoClash_(B,E,2,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,E,2)_t(E)_:
-1.000000 NoClash_(B,E,2,0)_t(E)
-1.000000 NoClash_(B,E,2,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(A,C,1)_t(A)_:
-1.000000 NoClash_(A,C,1,0)_t(A)
-1.000000 NoClash_(A,C,1,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,C,1)_t(C)_:
-1.000000 NoClash_(A,C,1,0)_t(C)
-1.000000 NoClash_(A,C,1,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(B,E,3)_t(B)_:
-1.000000 NoClash_(B,E,3,0)_t(B)
-1.000000 NoClash_(B,E,3,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,E,3)_t(E)_:
-1.000000 NoClash_(B,E,3,0)_t(E)
-1.000000 NoClash_(B,E,3,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(A,D,3)_t(A)_:
-1.000000 NoClash_(A,D,3,0)_t(A)
-1.000000 NoClash_(A,D,3,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,D,3)_t(D)_:
-1.000000 NoClash_(A,D,3,0)_t(D)
-1.000000 NoClash_(A,D,3,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(B,C,2)_t(B)_:
-1.000000 NoClash_(B,C,2,0)_t(B)
-1.000000 NoClash_(B,C,2,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,C,2)_t(C)_:
-1.000000 NoClash_(B,C,2,0)_t(C)
-1.000000 NoClash_(B,C,2,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,E,2)_t(C)_:
-1.000000 NoClash_(C,E,2,0)_t(C)
-1.000000 NoClash_(C,E,2,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,E,2)_t(E)_:
-1.000000 NoClash_(C,E,2,0)_t(E)
-1.000000 NoClash_(C,E,2,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(D,E,2)_t(D)_:
-1.000000 NoClash_(D,E,2,0)_t(D)
-1.000000 NoClash_(D,E,2,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,E,2)_t(E)_:
-1.000000 NoClash_(D,E,2,0)_t(E)
-1.000000 NoClash_(D,E,2,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(D,F,3)_t(D)_:
-1.000000 NoClash_(D,F,3,0)_t(D)
-1.000000 NoClash_(D,F,3,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,F,3)_t(F)_:
-1.000000 NoClash_(D,F,3,0)_t(F)
-1.000000 NoClash_(D,F,3,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(C,G,4)_t(C)_:
-1.000000 NoClash_(C,G,4,0)_t(C)
-1.000000 NoClash_(C,G,4,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,G,4)_t(G)_:
-1.000000 NoClash_(C,G,4,0)_t(G)
-1.000000 NoClash_(C,G,4,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(D,E,3)_t(D)_:
-1.000000 NoClash_(D,E,3,0)_t(D)
-1.000000 NoClash_(D,E,3,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(D,E,3)_t(E)_:
-1.000000 NoClash_(D,E,3,0)_t(E)
-1.000000 NoClash_(D,E,3,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(C,D,2)_t(C)_:
-1.000000 NoClash_(C,D,2,0)_t(C)
-1.000000 NoClash_(C,D,2,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,D,2)_t(D)_:
-1.000000 NoClash_(C,D,2,0)_t(D)
-1.000000 NoClash_(C,D,2,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(B,F,3)_t(B)_:
-1.000000 NoClash_(B,F,3,0)_t(B)
-1.000000 NoClash_(B,F,3,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,F,3)_t(F)_:
-1.000000 NoClash_(B,F,3,0)_t(F)
-1.000000 NoClash_(B,F,3,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(A,B,3)_t(A)_:
-1.000000 NoClash_(A,B,3,0)_t(A)
-1.000000 NoClash_(A,B,3,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,B,3)_t(B)_:
-1.000000 NoClash_(A,B,3,0)_t(B)
-1.000000 NoClash_(A,B,3,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(C,G,2)_t(C)_:
-1.000000 NoClash_(C,G,2,0)_t(C)
-1.000000 NoClash_(C,G,2,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,G,2)_t(G)_:
-1.000000 NoClash_(C,G,2,0)_t(G)
-1.000000 NoClash_(C,G,2,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(B,G,5)_t(B)_:
-1.000000 NoClash_(B,G,5,0)_t(B)
-1.000000 NoClash_(B,G,5,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,G,5)_t(G)_:
-1.000000 NoClash_(B,G,5,0)_t(G)
-1.000000 NoClash_(B,G,5,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(B,G,2)_t(B)_:
-1.000000 NoClash_(B,G,2,0)_t(B)
-1.000000 NoClash_(B,G,2,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,G,2)_t(G)_:
-1.000000 NoClash_(B,G,2,0)_t(G)
-1.000000 NoClash_(B,G,2,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(B,D,3)_t(B)_:
-1.000000 NoClash_(B,D,3,0)_t(B)
-1.000000 NoClash_(B,D,3,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,D,3)_t(D)_:
-1.000000 NoClash_(B,D,3,0)_t(D)
-1.000000 NoClash_(B,D,3,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(E,F,3)_t(E)_:
-1.000000 NoClash_(E,F,3,0)_t(E)
-1.000000 NoClash_(E,F,3,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(E,F,3)_t(F)_:
-1.000000 NoClash_(E,F,3,0)_t(F)
-1.000000 NoClash_(E,F,3,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(B,D,2)_t(B)_:
-1.000000 NoClash_(B,D,2,0)_t(B)
-1.000000 NoClash_(B,D,2,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,D,2)_t(D)_:
-1.000000 NoClash_(B,D,2,0)_t(D)
-1.000000 NoClash_(B,D,2,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(A,E,3)_t(A)_:
-1.000000 NoClash_(A,E,3,0)_t(A)
-1.000000 NoClash_(A,E,3,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,E,3)_t(E)_:
-1.000000 NoClash_(A,E,3,0)_t(E)
-1.000000 NoClash_(A,E,3,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(A,F,3)_t(A)_:
-1.000000 NoClash_(A,F,3,0)_t(A)
-1.000000 NoClash_(A,F,3,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,F,3)_t(F)_:
-1.000000 NoClash_(A,F,3,0)_t(F)
-1.000000 NoClash_(A,F,3,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(C,D,4)_t(C)_:
-1.000000 NoClash_(C,D,4,0)_t(C)
-1.000000 NoClash_(C,D,4,1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(C,D,4)_t(D)_:
-1.000000 NoClash_(C,D,4,0)_t(D)
-1.000000 NoClash_(C,D,4,1)_t(D)
+1.000000 t(D)
= 0.0

c_e_disj_(E,G,2)_t(E)_:
-1.000000 NoClash_(E,G,2,0)_t(E)
-1.000000 NoClash_(E,G,2,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(E,G,2)_t(G)_:
-1.000000 NoClash_(E,G,2,0)_t(G)
-1.000000 NoClash_(E,G,2,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(A,F,1)_t(A)_:
-1.000000 NoClash_(A,F,1,0)_t(A)
-1.000000 NoClash_(A,F,1,1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A,F,1)_t(F)_:
-1.000000 NoClash_(A,F,1,0)_t(F)
-1.000000 NoClash_(A,F,1,1)_t(F)
+1.000000 t(F)
= 0.0

c_e_disj_(E,G,5)_t(E)_:
-1.000000 NoClash_(E,G,5,0)_t(E)
-1.000000 NoClash_(E,G,5,1)_t(E)
+1.000000 t(E)
= 0.0

c_e_disj_(E,G,5)_t(G)_:
-1.000000 NoClash_(E,G,5,0)_t(G)
-1.000000 NoClash_(E,G,5,1)_t(G)
+1.000000 t(G)
= 0.0

c_e_disj_(B,E,5)_t(B)_:
-1.000000 NoClash_(B,E,5,0)_t(B)
-1.000000 NoClash_(B,E,5,1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B,E,5)_t(E)_:
-1.000000 NoClash_(B,E,5,0)_t(E)
-1.000000 NoClash_(B,E,5,1)_t(E)
+1.000000 t(E)
= 0.0

c_u_NoClash_(A,B,3,0)_t(A)_hi_:
-92.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,0)_t(A)
<= 0.0

c_u_NoClash_(A,B,3,0)_t(B)_hi_:
-92.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,0)_t(B)
<= 0.0

c_u_NoClash_(A,B,3,1)_t(A)_hi_:
-92.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(A)
<= 0.0

c_u_NoClash_(A,B,3,1)_t(B)_hi_:
-92.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(B)
<= 0.0

c_u_NoClash_(A,B,5,0)_t(A)_hi_:
-92.000000 NoClash_(A,B,5,0)_indicator_var
+1.000000 NoClash_(A,B,5,0)_t(A)
<= 0.0

c_u_NoClash_(A,B,5,0)_t(B)_hi_:
-92.000000 NoClash_(A,B,5,0)_indicator_var
+1.000000 NoClash_(A,B,5,0)_t(B)
<= 0.0

c_u_NoClash_(A,B,5,1)_t(A)_hi_:
-92.000000 NoClash_(A,B,5,1)_indicator_var
+1.000000 NoClash_(A,B,5,1)_t(A)
<= 0.0

c_u_NoClash_(A,B,5,1)_t(B)_hi_:
-92.000000 NoClash_(A,B,5,1)_indicator_var
+1.000000 NoClash_(A,B,5,1)_t(B)
<= 0.0

c_u_NoClash_(A,C,1,0)_t(A)_hi_:
-92.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,0)_t(A)
<= 0.0

c_u_NoClash_(A,C,1,0)_t(C)_hi_:
-92.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,0)_t(C)
<= 0.0

c_u_NoClash_(A,C,1,1)_t(A)_hi_:
-92.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(A)
<= 0.0

c_u_NoClash_(A,C,1,1)_t(C)_hi_:
-92.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(C)
<= 0.0

c_u_NoClash_(A,D,3,0)_t(A)_hi_:
-92.000000 NoClash_(A,D,3,0)_indicator_var
+1.000000 NoClash_(A,D,3,0)_t(A)
<= 0.0

c_u_NoClash_(A,D,3,0)_t(D)_hi_:
-92.000000 NoClash_(A,D,3,0)_indicator_var
+1.000000 NoClash_(A,D,3,0)_t(D)
<= 0.0

c_u_NoClash_(A,D,3,1)_t(A)_hi_:
-92.000000 NoClash_(A,D,3,1)_indicator_var
+1.000000 NoClash_(A,D,3,1)_t(A)
<= 0.0

c_u_NoClash_(A,D,3,1)_t(D)_hi_:
-92.000000 NoClash_(A,D,3,1)_indicator_var
+1.000000 NoClash_(A,D,3,1)_t(D)
<= 0.0

c_u_NoClash_(A,E,3,0)_t(A)_hi_:
-92.000000 NoClash_(A,E,3,0)_indicator_var
+1.000000 NoClash_(A,E,3,0)_t(A)
<= 0.0

c_u_NoClash_(A,E,3,0)_t(E)_hi_:
-92.000000 NoClash_(A,E,3,0)_indicator_var
+1.000000 NoClash_(A,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(A,E,3,1)_t(A)_hi_:
-92.000000 NoClash_(A,E,3,1)_indicator_var
+1.000000 NoClash_(A,E,3,1)_t(A)
<= 0.0

c_u_NoClash_(A,E,3,1)_t(E)_hi_:
-92.000000 NoClash_(A,E,3,1)_indicator_var
+1.000000 NoClash_(A,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(A,E,5,0)_t(A)_hi_:
-92.000000 NoClash_(A,E,5,0)_indicator_var
+1.000000 NoClash_(A,E,5,0)_t(A)
<= 0.0

c_u_NoClash_(A,E,5,0)_t(E)_hi_:
-92.000000 NoClash_(A,E,5,0)_indicator_var
+1.000000 NoClash_(A,E,5,0)_t(E)
<= 0.0

c_u_NoClash_(A,E,5,1)_t(A)_hi_:
-92.000000 NoClash_(A,E,5,1)_indicator_var
+1.000000 NoClash_(A,E,5,1)_t(A)
<= 0.0

c_u_NoClash_(A,E,5,1)_t(E)_hi_:
-92.000000 NoClash_(A,E,5,1)_indicator_var
+1.000000 NoClash_(A,E,5,1)_t(E)
<= 0.0

c_u_NoClash_(A,F,1,0)_t(A)_hi_:
-92.000000 NoClash_(A,F,1,0)_indicator_var
+1.000000 NoClash_(A,F,1,0)_t(A)
<= 0.0

c_u_NoClash_(A,F,1,0)_t(F)_hi_:
-92.000000 NoClash_(A,F,1,0)_indicator_var
+1.000000 NoClash_(A,F,1,0)_t(F)
<= 0.0

c_u_NoClash_(A,F,1,1)_t(A)_hi_:
-92.000000 NoClash_(A,F,1,1)_indicator_var
+1.000000 NoClash_(A,F,1,1)_t(A)
<= 0.0

c_u_NoClash_(A,F,1,1)_t(F)_hi_:
-92.000000 NoClash_(A,F,1,1)_indicator_var
+1.000000 NoClash_(A,F,1,1)_t(F)
<= 0.0

c_u_NoClash_(A,F,3,0)_t(A)_hi_:
-92.000000 NoClash_(A,F,3,0)_indicator_var
+1.000000 NoClash_(A,F,3,0)_t(A)
<= 0.0

c_u_NoClash_(A,F,3,0)_t(F)_hi_:
-92.000000 NoClash_(A,F,3,0)_indicator_var
+1.000000 NoClash_(A,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(A,F,3,1)_t(A)_hi_:
-92.000000 NoClash_(A,F,3,1)_indicator_var
+1.000000 NoClash_(A,F,3,1)_t(A)
<= 0.0

c_u_NoClash_(A,F,3,1)_t(F)_hi_:
-92.000000 NoClash_(A,F,3,1)_indicator_var
+1.000000 NoClash_(A,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(A,G,5,0)_t(A)_hi_:
-92.000000 NoClash_(A,G,5,0)_indicator_var
+1.000000 NoClash_(A,G,5,0)_t(A)
<= 0.0

c_u_NoClash_(A,G,5,0)_t(G)_hi_:
-92.000000 NoClash_(A,G,5,0)_indicator_var
+1.000000 NoClash_(A,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(A,G,5,1)_t(A)_hi_:
-92.000000 NoClash_(A,G,5,1)_indicator_var
+1.000000 NoClash_(A,G,5,1)_t(A)
<= 0.0

c_u_NoClash_(A,G,5,1)_t(G)_hi_:
-92.000000 NoClash_(A,G,5,1)_indicator_var
+1.000000 NoClash_(A,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(B,C,2,0)_t(B)_hi_:
-92.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,0)_t(B)
<= 0.0

c_u_NoClash_(B,C,2,0)_t(C)_hi_:
-92.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,0)_t(C)
<= 0.0

c_u_NoClash_(B,C,2,1)_t(B)_hi_:
-92.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(B)
<= 0.0

c_u_NoClash_(B,C,2,1)_t(C)_hi_:
-92.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(C)
<= 0.0

c_u_NoClash_(B,D,2,0)_t(B)_hi_:
-92.000000 NoClash_(B,D,2,0)_indicator_var
+1.000000 NoClash_(B,D,2,0)_t(B)
<= 0.0

c_u_NoClash_(B,D,2,0)_t(D)_hi_:
-92.000000 NoClash_(B,D,2,0)_indicator_var
+1.000000 NoClash_(B,D,2,0)_t(D)
<= 0.0

c_u_NoClash_(B,D,2,1)_t(B)_hi_:
-92.000000 NoClash_(B,D,2,1)_indicator_var
+1.000000 NoClash_(B,D,2,1)_t(B)
<= 0.0

c_u_NoClash_(B,D,2,1)_t(D)_hi_:
-92.000000 NoClash_(B,D,2,1)_indicator_var
+1.000000 NoClash_(B,D,2,1)_t(D)
<= 0.0

c_u_NoClash_(B,D,3,0)_t(B)_hi_:
-92.000000 NoClash_(B,D,3,0)_indicator_var
+1.000000 NoClash_(B,D,3,0)_t(B)
<= 0.0

c_u_NoClash_(B,D,3,0)_t(D)_hi_:
-92.000000 NoClash_(B,D,3,0)_indicator_var
+1.000000 NoClash_(B,D,3,0)_t(D)
<= 0.0

c_u_NoClash_(B,D,3,1)_t(B)_hi_:
-92.000000 NoClash_(B,D,3,1)_indicator_var
+1.000000 NoClash_(B,D,3,1)_t(B)
<= 0.0

c_u_NoClash_(B,D,3,1)_t(D)_hi_:
-92.000000 NoClash_(B,D,3,1)_indicator_var
+1.000000 NoClash_(B,D,3,1)_t(D)
<= 0.0

c_u_NoClash_(B,E,2,0)_t(B)_hi_:
-92.000000 NoClash_(B,E,2,0)_indicator_var
+1.000000 NoClash_(B,E,2,0)_t(B)
<= 0.0

c_u_NoClash_(B,E,2,0)_t(E)_hi_:
-92.000000 NoClash_(B,E,2,0)_indicator_var
+1.000000 NoClash_(B,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(B,E,2,1)_t(B)_hi_:
-92.000000 NoClash_(B,E,2,1)_indicator_var
+1.000000 NoClash_(B,E,2,1)_t(B)
<= 0.0

c_u_NoClash_(B,E,2,1)_t(E)_hi_:
-92.000000 NoClash_(B,E,2,1)_indicator_var
+1.000000 NoClash_(B,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(B,E,3,0)_t(B)_hi_:
-92.000000 NoClash_(B,E,3,0)_indicator_var
+1.000000 NoClash_(B,E,3,0)_t(B)
<= 0.0

c_u_NoClash_(B,E,3,0)_t(E)_hi_:
-92.000000 NoClash_(B,E,3,0)_indicator_var
+1.000000 NoClash_(B,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(B,E,3,1)_t(B)_hi_:
-92.000000 NoClash_(B,E,3,1)_indicator_var
+1.000000 NoClash_(B,E,3,1)_t(B)
<= 0.0

c_u_NoClash_(B,E,3,1)_t(E)_hi_:
-92.000000 NoClash_(B,E,3,1)_indicator_var
+1.000000 NoClash_(B,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(B,E,5,0)_t(B)_hi_:
-92.000000 NoClash_(B,E,5,0)_indicator_var
+1.000000 NoClash_(B,E,5,0)_t(B)
<= 0.0

c_u_NoClash_(B,E,5,0)_t(E)_hi_:
-92.000000 NoClash_(B,E,5,0)_indicator_var
+1.000000 NoClash_(B,E,5,0)_t(E)
<= 0.0

c_u_NoClash_(B,E,5,1)_t(B)_hi_:
-92.000000 NoClash_(B,E,5,1)_indicator_var
+1.000000 NoClash_(B,E,5,1)_t(B)
<= 0.0

c_u_NoClash_(B,E,5,1)_t(E)_hi_:
-92.000000 NoClash_(B,E,5,1)_indicator_var
+1.000000 NoClash_(B,E,5,1)_t(E)
<= 0.0

c_u_NoClash_(B,F,3,0)_t(B)_hi_:
-92.000000 NoClash_(B,F,3,0)_indicator_var
+1.000000 NoClash_(B,F,3,0)_t(B)
<= 0.0

c_u_NoClash_(B,F,3,0)_t(F)_hi_:
-92.000000 NoClash_(B,F,3,0)_indicator_var
+1.000000 NoClash_(B,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(B,F,3,1)_t(B)_hi_:
-92.000000 NoClash_(B,F,3,1)_indicator_var
+1.000000 NoClash_(B,F,3,1)_t(B)
<= 0.0

c_u_NoClash_(B,F,3,1)_t(F)_hi_:
-92.000000 NoClash_(B,F,3,1)_indicator_var
+1.000000 NoClash_(B,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(B,G,2,0)_t(B)_hi_:
-92.000000 NoClash_(B,G,2,0)_indicator_var
+1.000000 NoClash_(B,G,2,0)_t(B)
<= 0.0

c_u_NoClash_(B,G,2,0)_t(G)_hi_:
-92.000000 NoClash_(B,G,2,0)_indicator_var
+1.000000 NoClash_(B,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(B,G,2,1)_t(B)_hi_:
-92.000000 NoClash_(B,G,2,1)_indicator_var
+1.000000 NoClash_(B,G,2,1)_t(B)
<= 0.0

c_u_NoClash_(B,G,2,1)_t(G)_hi_:
-92.000000 NoClash_(B,G,2,1)_indicator_var
+1.000000 NoClash_(B,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(B,G,5,0)_t(B)_hi_:
-92.000000 NoClash_(B,G,5,0)_indicator_var
+1.000000 NoClash_(B,G,5,0)_t(B)
<= 0.0

c_u_NoClash_(B,G,5,0)_t(G)_hi_:
-92.000000 NoClash_(B,G,5,0)_indicator_var
+1.000000 NoClash_(B,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(B,G,5,1)_t(B)_hi_:
-92.000000 NoClash_(B,G,5,1)_indicator_var
+1.000000 NoClash_(B,G,5,1)_t(B)
<= 0.0

c_u_NoClash_(B,G,5,1)_t(G)_hi_:
-92.000000 NoClash_(B,G,5,1)_indicator_var
+1.000000 NoClash_(B,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(C,D,2,0)_t(C)_hi_:
-92.000000 NoClash_(C,D,2,0)_indicator_var
+1.000000 NoClash_(C,D,2,0)_t(C)
<= 0.0

c_u_NoClash_(C,D,2,0)_t(D)_hi_:
-92.000000 NoClash_(C,D,2,0)_indicator_var
+1.000000 NoClash_(C,D,2,0)_t(D)
<= 0.0

c_u_NoClash_(C,D,2,1)_t(C)_hi_:
-92.000000 NoClash_(C,D,2,1)_indicator_var
+1.000000 NoClash_(C,D,2,1)_t(C)
<= 0.0

c_u_NoClash_(C,D,2,1)_t(D)_hi_:
-92.000000 NoClash_(C,D,2,1)_indicator_var
+1.000000 NoClash_(C,D,2,1)_t(D)
<= 0.0

c_u_NoClash_(C,D,4,0)_t(C)_hi_:
-92.000000 NoClash_(C,D,4,0)_indicator_var
+1.000000 NoClash_(C,D,4,0)_t(C)
<= 0.0

c_u_NoClash_(C,D,4,0)_t(D)_hi_:
-92.000000 NoClash_(C,D,4,0)_indicator_var
+1.000000 NoClash_(C,D,4,0)_t(D)
<= 0.0

c_u_NoClash_(C,D,4,1)_t(C)_hi_:
-92.000000 NoClash_(C,D,4,1)_indicator_var
+1.000000 NoClash_(C,D,4,1)_t(C)
<= 0.0

c_u_NoClash_(C,D,4,1)_t(D)_hi_:
-92.000000 NoClash_(C,D,4,1)_indicator_var
+1.000000 NoClash_(C,D,4,1)_t(D)
<= 0.0

c_u_NoClash_(C,E,2,0)_t(C)_hi_:
-92.000000 NoClash_(C,E,2,0)_indicator_var
+1.000000 NoClash_(C,E,2,0)_t(C)
<= 0.0

c_u_NoClash_(C,E,2,0)_t(E)_hi_:
-92.000000 NoClash_(C,E,2,0)_indicator_var
+1.000000 NoClash_(C,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(C,E,2,1)_t(C)_hi_:
-92.000000 NoClash_(C,E,2,1)_indicator_var
+1.000000 NoClash_(C,E,2,1)_t(C)
<= 0.0

c_u_NoClash_(C,E,2,1)_t(E)_hi_:
-92.000000 NoClash_(C,E,2,1)_indicator_var
+1.000000 NoClash_(C,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(C,F,1,0)_t(C)_hi_:
-92.000000 NoClash_(C,F,1,0)_indicator_var
+1.000000 NoClash_(C,F,1,0)_t(C)
<= 0.0

c_u_NoClash_(C,F,1,0)_t(F)_hi_:
-92.000000 NoClash_(C,F,1,0)_indicator_var
+1.000000 NoClash_(C,F,1,0)_t(F)
<= 0.0

c_u_NoClash_(C,F,1,1)_t(C)_hi_:
-92.000000 NoClash_(C,F,1,1)_indicator_var
+1.000000 NoClash_(C,F,1,1)_t(C)
<= 0.0

c_u_NoClash_(C,F,1,1)_t(F)_hi_:
-92.000000 NoClash_(C,F,1,1)_indicator_var
+1.000000 NoClash_(C,F,1,1)_t(F)
<= 0.0

c_u_NoClash_(C,F,4,0)_t(C)_hi_:
-92.000000 NoClash_(C,F,4,0)_indicator_var
+1.000000 NoClash_(C,F,4,0)_t(C)
<= 0.0

c_u_NoClash_(C,F,4,0)_t(F)_hi_:
-92.000000 NoClash_(C,F,4,0)_indicator_var
+1.000000 NoClash_(C,F,4,0)_t(F)
<= 0.0

c_u_NoClash_(C,F,4,1)_t(C)_hi_:
-92.000000 NoClash_(C,F,4,1)_indicator_var
+1.000000 NoClash_(C,F,4,1)_t(C)
<= 0.0

c_u_NoClash_(C,F,4,1)_t(F)_hi_:
-92.000000 NoClash_(C,F,4,1)_indicator_var
+1.000000 NoClash_(C,F,4,1)_t(F)
<= 0.0

c_u_NoClash_(C,G,2,0)_t(C)_hi_:
-92.000000 NoClash_(C,G,2,0)_indicator_var
+1.000000 NoClash_(C,G,2,0)_t(C)
<= 0.0

c_u_NoClash_(C,G,2,0)_t(G)_hi_:
-92.000000 NoClash_(C,G,2,0)_indicator_var
+1.000000 NoClash_(C,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(C,G,2,1)_t(C)_hi_:
-92.000000 NoClash_(C,G,2,1)_indicator_var
+1.000000 NoClash_(C,G,2,1)_t(C)
<= 0.0

c_u_NoClash_(C,G,2,1)_t(G)_hi_:
-92.000000 NoClash_(C,G,2,1)_indicator_var
+1.000000 NoClash_(C,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(C,G,4,0)_t(C)_hi_:
-92.000000 NoClash_(C,G,4,0)_indicator_var
+1.000000 NoClash_(C,G,4,0)_t(C)
<= 0.0

c_u_NoClash_(C,G,4,0)_t(G)_hi_:
-92.000000 NoClash_(C,G,4,0)_indicator_var
+1.000000 NoClash_(C,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(C,G,4,1)_t(C)_hi_:
-92.000000 NoClash_(C,G,4,1)_indicator_var
+1.000000 NoClash_(C,G,4,1)_t(C)
<= 0.0

c_u_NoClash_(C,G,4,1)_t(G)_hi_:
-92.000000 NoClash_(C,G,4,1)_indicator_var
+1.000000 NoClash_(C,G,4,1)_t(G)
<= 0.0

c_u_NoClash_(D,E,2,0)_t(D)_hi_:
-92.000000 NoClash_(D,E,2,0)_indicator_var
+1.000000 NoClash_(D,E,2,0)_t(D)
<= 0.0

c_u_NoClash_(D,E,2,0)_t(E)_hi_:
-92.000000 NoClash_(D,E,2,0)_indicator_var
+1.000000 NoClash_(D,E,2,0)_t(E)
<= 0.0

c_u_NoClash_(D,E,2,1)_t(D)_hi_:
-92.000000 NoClash_(D,E,2,1)_indicator_var
+1.000000 NoClash_(D,E,2,1)_t(D)
<= 0.0

c_u_NoClash_(D,E,2,1)_t(E)_hi_:
-92.000000 NoClash_(D,E,2,1)_indicator_var
+1.000000 NoClash_(D,E,2,1)_t(E)
<= 0.0

c_u_NoClash_(D,E,3,0)_t(D)_hi_:
-92.000000 NoClash_(D,E,3,0)_indicator_var
+1.000000 NoClash_(D,E,3,0)_t(D)
<= 0.0

c_u_NoClash_(D,E,3,0)_t(E)_hi_:
-92.000000 NoClash_(D,E,3,0)_indicator_var
+1.000000 NoClash_(D,E,3,0)_t(E)
<= 0.0

c_u_NoClash_(D,E,3,1)_t(D)_hi_:
-92.000000 NoClash_(D,E,3,1)_indicator_var
+1.000000 NoClash_(D,E,3,1)_t(D)
<= 0.0

c_u_NoClash_(D,E,3,1)_t(E)_hi_:
-92.000000 NoClash_(D,E,3,1)_indicator_var
+1.000000 NoClash_(D,E,3,1)_t(E)
<= 0.0

c_u_NoClash_(D,F,3,0)_t(D)_hi_:
-92.000000 NoClash_(D,F,3,0)_indicator_var
+1.000000 NoClash_(D,F,3,0)_t(D)
<= 0.0

c_u_NoClash_(D,F,3,0)_t(F)_hi_:
-92.000000 NoClash_(D,F,3,0)_indicator_var
+1.000000 NoClash_(D,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(D,F,3,1)_t(D)_hi_:
-92.000000 NoClash_(D,F,3,1)_indicator_var
+1.000000 NoClash_(D,F,3,1)_t(D)
<= 0.0

c_u_NoClash_(D,F,3,1)_t(F)_hi_:
-92.000000 NoClash_(D,F,3,1)_indicator_var
+1.000000 NoClash_(D,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(D,F,4,0)_t(D)_hi_:
-92.000000 NoClash_(D,F,4,0)_indicator_var
+1.000000 NoClash_(D,F,4,0)_t(D)
<= 0.0

c_u_NoClash_(D,F,4,0)_t(F)_hi_:
-92.000000 NoClash_(D,F,4,0)_indicator_var
+1.000000 NoClash_(D,F,4,0)_t(F)
<= 0.0

c_u_NoClash_(D,F,4,1)_t(D)_hi_:
-92.000000 NoClash_(D,F,4,1)_indicator_var
+1.000000 NoClash_(D,F,4,1)_t(D)
<= 0.0

c_u_NoClash_(D,F,4,1)_t(F)_hi_:
-92.000000 NoClash_(D,F,4,1)_indicator_var
+1.000000 NoClash_(D,F,4,1)_t(F)
<= 0.0

c_u_NoClash_(D,G,2,0)_t(D)_hi_:
-92.000000 NoClash_(D,G,2,0)_indicator_var
+1.000000 NoClash_(D,G,2,0)_t(D)
<= 0.0

c_u_NoClash_(D,G,2,0)_t(G)_hi_:
-92.000000 NoClash_(D,G,2,0)_indicator_var
+1.000000 NoClash_(D,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(D,G,2,1)_t(D)_hi_:
-92.000000 NoClash_(D,G,2,1)_indicator_var
+1.000000 NoClash_(D,G,2,1)_t(D)
<= 0.0

c_u_NoClash_(D,G,2,1)_t(G)_hi_:
-92.000000 NoClash_(D,G,2,1)_indicator_var
+1.000000 NoClash_(D,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(D,G,4,0)_t(D)_hi_:
-92.000000 NoClash_(D,G,4,0)_indicator_var
+1.000000 NoClash_(D,G,4,0)_t(D)
<= 0.0

c_u_NoClash_(D,G,4,0)_t(G)_hi_:
-92.000000 NoClash_(D,G,4,0)_indicator_var
+1.000000 NoClash_(D,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(D,G,4,1)_t(D)_hi_:
-92.000000 NoClash_(D,G,4,1)_indicator_var
+1.000000 NoClash_(D,G,4,1)_t(D)
<= 0.0

c_u_NoClash_(D,G,4,1)_t(G)_hi_:
-92.000000 NoClash_(D,G,4,1)_indicator_var
+1.000000 NoClash_(D,G,4,1)_t(G)
<= 0.0

c_u_NoClash_(E,F,3,0)_t(E)_hi_:
-92.000000 NoClash_(E,F,3,0)_indicator_var
+1.000000 NoClash_(E,F,3,0)_t(E)
<= 0.0

c_u_NoClash_(E,F,3,0)_t(F)_hi_:
-92.000000 NoClash_(E,F,3,0)_indicator_var
+1.000000 NoClash_(E,F,3,0)_t(F)
<= 0.0

c_u_NoClash_(E,F,3,1)_t(E)_hi_:
-92.000000 NoClash_(E,F,3,1)_indicator_var
+1.000000 NoClash_(E,F,3,1)_t(E)
<= 0.0

c_u_NoClash_(E,F,3,1)_t(F)_hi_:
-92.000000 NoClash_(E,F,3,1)_indicator_var
+1.000000 NoClash_(E,F,3,1)_t(F)
<= 0.0

c_u_NoClash_(E,G,2,0)_t(E)_hi_:
-92.000000 NoClash_(E,G,2,0)_indicator_var
+1.000000 NoClash_(E,G,2,0)_t(E)
<= 0.0

c_u_NoClash_(E,G,2,0)_t(G)_hi_:
-92.000000 NoClash_(E,G,2,0)_indicator_var
+1.000000 NoClash_(E,G,2,0)_t(G)
<= 0.0

c_u_NoClash_(E,G,2,1)_t(E)_hi_:
-92.000000 NoClash_(E,G,2,1)_indicator_var
+1.000000 NoClash_(E,G,2,1)_t(E)
<= 0.0

c_u_NoClash_(E,G,2,1)_t(G)_hi_:
-92.000000 NoClash_(E,G,2,1)_indicator_var
+1.000000 NoClash_(E,G,2,1)_t(G)
<= 0.0

c_u_NoClash_(E,G,5,0)_t(E)_hi_:
-92.000000 NoClash_(E,G,5,0)_indicator_var
+1.000000 NoClash_(E,G,5,0)_t(E)
<= 0.0

c_u_NoClash_(E,G,5,0)_t(G)_hi_:
-92.000000 NoClash_(E,G,5,0)_indicator_var
+1.000000 NoClash_(E,G,5,0)_t(G)
<= 0.0

c_u_NoClash_(E,G,5,1)_t(E)_hi_:
-92.000000 NoClash_(E,G,5,1)_indicator_var
+1.000000 NoClash_(E,G,5,1)_t(E)
<= 0.0

c_u_NoClash_(E,G,5,1)_t(G)_hi_:
-92.000000 NoClash_(E,G,5,1)_indicator_var
+1.000000 NoClash_(E,G,5,1)_t(G)
<= 0.0

c_u_NoClash_(F,G,4,0)_t(F)_hi_:
-92.000000 NoClash_(F,G,4,0)_indicator_var
+1.000000 NoClash_(F,G,4,0)_t(F)
<= 0.0

c_u_NoClash_(F,G,4,0)_t(G)_hi_:
-92.000000 NoClash_(F,G,4,0)_indicator_var
+1.000000 NoClash_(F,G,4,0)_t(G)
<= 0.0

c_u_NoClash_(F,G,4,1)_t(F)_hi_:
-92.000000 NoClash_(F,G,4,1)_indicator_var
+1.000000 NoClash_(F,G,4,1)_t(F)
<= 0.0

c_u_NoClash_(F,G,4,1)_t(G)_hi_:
-92.000000 NoClash_(F,G,4,1)_indicator_var
+1.000000 NoClash_(F,G,4,1)_t(G)
<= 0.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    0 <=  NoClash_(A,B,3,0)_indicator_var  <= 1
    0 <=  NoClash_(A,B,3,0)_t(A)  <= 92
    0 <=  NoClash_(A,B,3,0)_t(B)  <= 92
    0 <=  NoClash_(A,B,3,1)_indicator_var  <= 1
    0 <=  NoClash_(A,B,3,1)_t(A)  <= 92
    0 <=  NoClash_(A,B,3,1)_t(B)  <= 92
    0 <=  NoClash_(A,B,5,0)_indicator_var  <= 1
    0 <=  NoClash_(A,B,5,0)_t(A)  <= 92
    0 <=  NoClash_(A,B,5,0)_t(B)  <= 92
    0 <=  NoClash_(A,B,5,1)_indicator_var  <= 1
    0 <=  NoClash_(A,B,5,1)_t(A)  <= 92
    0 <=  NoClash_(A,B,5,1)_t(B)  <= 92
    0 <=  NoClash_(A,C,1,0)_indicator_var  <= 1
    0 <=  NoClash_(A,C,1,0)_t(A)  <= 92
    0 <=  NoClash_(A,C,1,0)_t(C)  <= 92
    0 <=  NoClash_(A,C,1,1)_indicator_var  <= 1
    0 <=  NoClash_(A,C,1,1)_t(A)  <= 92
    0 <=  NoClash_(A,C,1,1)_t(C)  <= 92
    0 <=  NoClash_(A,D,3,0)_indicator_var  <= 1
    0 <=  NoClash_(A,D,3,0)_t(A)  <= 92
    0 <=  NoClash_(A,D,3,0)_t(D)  <= 92
    0 <=  NoClash_(A,D,3,1)_indicator_var  <= 1
    0 <=  NoClash_(A,D,3,1)_t(A)  <= 92
    0 <=  NoClash_(A,D,3,1)_t(D)  <= 92
    0 <=  NoClash_(A,E,3,0)_indicator_var  <= 1
    0 <=  NoClash_(A,E,3,0)_t(A)  <= 92
    0 <=  NoClash_(A,E,3,0)_t(E)  <= 92
    0 <=  NoClash_(A,E,3,1)_indicator_var  <= 1
    0 <=  NoClash_(A,E,3,1)_t(A)  <= 92
    0 <=  NoClash_(A,E,3,1)_t(E)  <= 92
    0 <=  NoClash_(A,E,5,0)_indicator_var  <= 1
    0 <=  NoClash_(A,E,5,0)_t(A)  <= 92
    0 <=  NoClash_(A,E,5,0)_t(E)  <= 92
    0 <=  NoClash_(A,E,5,1)_indicator_var  <= 1
    0 <=  NoClash_(A,E,5,1)_t(A)  <= 92
    0 <=  NoClash_(A,E,5,1)_t(E)  <= 92
    0 <=  NoClash_(A,F,1,0)_indicator_var  <= 1
    0 <=  NoClash_(A,F,1,0)_t(A)  <= 92
    0 <=  NoClash_(A,F,1,0)_t(F)  <= 92
    0 <=  NoClash_(A,F,1,1)_indicator_var  <= 1
    0 <=  NoClash_(A,F,1,1)_t(A)  <= 92
    0 <=  NoClash_(A,F,1,1)_t(F)  <= 92
    0 <=  NoClash_(A,F,3,0)_indicator_var  <= 1
    0 <=  NoClash_(A,F,3,0)_t(A)  <= 92
    0 <=  NoClash_(A,F,3,0)_t(F)  <= 92
    0 <=  NoClash_(A,F,3,1)_indicator_var  <= 1
    0 <=  NoClash_(A,F,3,1)_t(A)  <= 92
    0 <=  NoClash_(A,F,3,1)_t(F)  <= 92
    0 <=  NoClash_(A,G,5,0)_indicator_var  <= 1
    0 <=  NoClash_(A,G,5,0)_t(A)  <= 92
    0 <=  NoClash_(A,G,5,0)_t(G)  <= 92
    0 <=  NoClash_(A,G,5,1)_indicator_var  <= 1
    0 <=  NoClash_(A,G,5,1)_t(A)  <= 92
    0 <=  NoClash_(A,G,5,1)_t(G)  <= 92
    0 <=  NoClash_(B,C,2,0)_indicator_var  <= 1
    0 <=  NoClash_(B,C,2,0)_t(B)  <= 92
    0 <=  NoClash_(B,C,2,0)_t(C)  <= 92
    0 <=  NoClash_(B,C,2,1)_indicator_var  <= 1
    0 <=  NoClash_(B,C,2,1)_t(B)  <= 92
    0 <=  NoClash_(B,C,2,1)_t(C)  <= 92
    0 <=  NoClash_(B,D,2,0)_indicator_var  <= 1
    0 <=  NoClash_(B,D,2,0)_t(B)  <= 92
    0 <=  NoClash_(B,D,2,0)_t(D)  <= 92
    0 <=  NoClash_(B,D,2,1)_indicator_var  <= 1
    0 <=  NoClash_(B,D,2,1)_t(B)  <= 92
    0 <=  NoClash_(B,D,2,1)_t(D)  <= 92
    0 <=  NoClash_(B,D,3,0)_indicator_var  <= 1
    0 <=  NoClash_(B,D,3,0)_t(B)  <= 92
    0 <=  NoClash_(B,D,3,0)_t(D)  <= 92
    0 <=  NoClash_(B,D,3,1)_indicator_var  <= 1
    0 <=  NoClash_(B,D,3,1)_t(B)  <= 92
    0 <=  NoClash_(B,D,3,1)_t(D)  <= 92
    0 <=  NoClash_(B,E,2,0)_indicator_var  <= 1
    0 <=  NoClash_(B,E,2,0)_t(B)  <= 92
    0 <=  NoClash_(B,E,2,0)_t(E)  <= 92
    0 <=  NoClash_(B,E,2,1)_indicator_var  <= 1
    0 <=  NoClash_(B,E,2,1)_t(B)  <= 92
    0 <=  NoClash_(B,E,2,1)_t(E)  <= 92
    0 <=  NoClash_(B,E,3,0)_indicator_var  <= 1
    0 <=  NoClash_(B,E,3,0)_t(B)  <= 92
    0 <=  NoClash_(B,E,3,0)_t(E)  <= 92
    0 <=  NoClash_(B,E,3,1)_indicator_var  <= 1
    0 <=  NoClash_(B,E,3,1)_t(B)  <= 92
    0 <=  NoClash_(B,E,3,1)_t(E)  <= 92
    0 <=  NoClash_(B,E,5,0)_indicator_var  <= 1
    0 <=  NoClash_(B,E,5,0)_t(B)  <= 92
    0 <=  NoClash_(B,E,5,0)_t(E)  <= 92
    0 <=  NoClash_(B,E,5,1)_indicator_var  <= 1
    0 <=  NoClash_(B,E,5,1)_t(B)  <= 92
    0 <=  NoClash_(B,E,5,1)_t(E)  <= 92
    0 <=  NoClash_(B,F,3,0)_indicator_var  <= 1
    0 <=  NoClash_(B,F,3,0)_t(B)  <= 92
    0 <=  NoClash_(B,F,3,0)_t(F)  <= 92
    0 <=  NoClash_(B,F,3,1)_indicator_var  <= 1
    0 <=  NoClash_(B,F,3,1)_t(B)  <= 92
    0 <=  NoClash_(B,F,3,1)_t(F)  <= 92
    0 <=  NoClash_(B,G,2,0)_indicator_var  <= 1
    0 <=  NoClash_(B,G,2,0)_t(B)  <= 92
    0 <=  NoClash_(B,G,2,0)_t(G)  <= 92
    0 <=  NoClash_(B,G,2,1)_indicator_var  <= 1
    0 <=  NoClash_(B,G,2,1)_t(B)  <= 92
    0 <=  NoClash_(B,G,2,1)_t(G)  <= 92
    0 <=  NoClash_(B,G,5,0)_indicator_var  <= 1
    0 <=  NoClash_(B,G,5,0)_t(B)  <= 92
    0 <=  NoClash_(B,G,5,0)_t(G)  <= 92
    0 <=  NoClash_(B,G,5,1)_indicator_var  <= 1
    0 <=  NoClash_(B,G,5,1)_t(B)  <= 92
    0 <=  NoClash_(B,G,5,1)_t(G)  <= 92
    0 <=  NoClash_(C,D,2,0)_indicator_var  <= 1
    0 <=  NoClash_(C,D,2,0)_t(C)  <= 92
    0 <=  NoClash_(C,D,2,0)_t(D)  <= 92
    0 <=  NoClash_(C,D,2,1)_indicator_var  <= 1
    0 <=  NoClash_(C,D,2,1)_t(C)  <= 92
    0 <=  NoClash_(C,D,2,1)_t(D)  <= 92
    0 <=  NoClash_(C,D,4,0)_indicator_var  <= 1
    0 <=  NoClash_(C,D,4,0)_t(C)  <= 92
    0 <=  NoClash_(C,D,4,0)_t(D)  <= 92
    0 <=  NoClash_(C,D,4,1)_indicator_var  <= 1
    0 <=  NoClash_(C,D,4,1)_t(C)  <= 92
    0 <=  NoClash_(C,D,4,1)_t(D)  <= 92
    0 <=  NoClash_(C,E,2,0)_indicator_var  <= 1
    0 <=  NoClash_(C,E,2,0)_t(C)  <= 92
    0 <=  NoClash_(C,E,2,0)_t(E)  <= 92
    0 <=  NoClash_(C,E,2,1)_indicator_var  <= 1
    0 <=  NoClash_(C,E,2,1)_t(C)  <= 92
    0 <=  NoClash_(C,E,2,1)_t(E)  <= 92
    0 <=  NoClash_(C,F,1,0)_indicator_var  <= 1
    0 <=  NoClash_(C,F,1,0)_t(C)  <= 92
    0 <=  NoClash_(C,F,1,0)_t(F)  <= 92
    0 <=  NoClash_(C,F,1,1)_indicator_var  <= 1
    0 <=  NoClash_(C,F,1,1)_t(C)  <= 92
    0 <=  NoClash_(C,F,1,1)_t(F)  <= 92
    0 <=  NoClash_(C,F,4,0)_indicator_var  <= 1
    0 <=  NoClash_(C,F,4,0)_t(C)  <= 92
    0 <=  NoClash_(C,F,4,0)_t(F)  <= 92
    0 <=  NoClash_(C,F,4,1)_indicator_var  <= 1
    0 <=  NoClash_(C,F,4,1)_t(C)  <= 92
    0 <=  NoClash_(C,F,4,1)_t(F)  <= 92
    0 <=  NoClash_(C,G,2,0)_indicator_var  <= 1
    0 <=  NoClash_(C,G,2,0)_t(C)  <= 92
    0 <=  NoClash_(C,G,2,0)_t(G)  <= 92
    0 <=  NoClash_(C,G,2,1)_indicator_var  <= 1
    0 <=  NoClash_(C,G,2,1)_t(C)  <= 92
    0 <=  NoClash_(C,G,2,1)_t(G)  <= 92
    0 <=  NoClash_(C,G,4,0)_indicator_var  <= 1
    0 <=  NoClash_(C,G,4,0)_t(C)  <= 92
    0 <=  NoClash_(C,G,4,0)_t(G)  <= 92
    0 <=  NoClash_(C,G,4,1)_indicator_var  <= 1
    0 <=  NoClash_(C,G,4,1)_t(C)  <= 92
    0 <=  NoClash_(C,G,4,1)_t(G)  <= 92
    0 <=  NoClash_(D,E,2,0)_indicator_var  <= 1
    0 <=  NoClash_(D,E,2,0)_t(D)  <= 92
    0 <=  NoClash_(D,E,2,0)_t(E)  <= 92
    0 <=  NoClash_(D,E,2,1)_indicator_var  <= 1
    0 <=  NoClash_(D,E,2,1)_t(D)  <= 92
    0 <=  NoClash_(D,E,2,1)_t(E)  <= 92
    0 <=  NoClash_(D,E,3,0)_indicator_var  <= 1
    0 <=  NoClash_(D,E,3,0)_t(D)  <= 92
    0 <=  NoClash_(D,E,3,0)_t(E)  <= 92
    0 <=  NoClash_(D,E,3,1)_indicator_var  <= 1
    0 <=  NoClash_(D,E,3,1)_t(D)  <= 92
    0 <=  NoClash_(D,E,3,1)_t(E)  <= 92
    0 <=  NoClash_(D,F,3,0)_indicator_var  <= 1
    0 <=  NoClash_(D,F,3,0)_t(D)  <= 92
    0 <=  NoClash_(D,F,3,0)_t(F)  <= 92
    0 <=  NoClash_(D,F,3,1)_indicator_var  <= 1
    0 <=  NoClash_(D,F,3,1)_t(D)  <= 92
    0 <=  NoClash_(D,F,3,1)_t(F)  <= 92
    0 <=  NoClash_(D,F,4,0)_indicator_var  <= 1
    0 <=  NoClash_(D,F,4,0)_t(D)  <= 92
    0 <=  NoClash_(D,F,4,0)_t(F)  <= 92
    0 <=  NoClash_(D,F,4,1)_indicator_var  <= 1
    0 <=  NoClash_(D,F,4,1)_t(D)  <= 92
    0 <=  NoClash_(D,F,4,1)_t(F)  <= 92
    0 <=  NoClash_(D,G,2,0)_indicator_var  <= 1
    0 <=  NoClash_(D,G,2,0)_t(D)  <= 92
    0 <=  NoClash_(D,G,2,0)_t(G)  <= 92
    0 <=  NoClash_(D,G,2,1)_indicator_var  <= 1
    0 <=  NoClash_(D,G,2,1)_t(D)  <= 92
    0 <=  NoClash_(D,G,2,1)_t(G)  <= 92
    0 <=  NoClash_(D,G,4,0)_indicator_var  <= 1
    0 <=  NoClash_(D,G,4,0)_t(D)  <= 92
    0 <=  NoClash_(D,G,4,0)_t(G)  <= 92
    0 <=  NoClash_(D,G,4,1)_indicator_var  <= 1
    0 <=  NoClash_(D,G,4,1)_t(D)  <= 92
    0 <=  NoClash_(D,G,4,1)_t(G)  <= 92
    0 <=  NoClash_(E,F,3,0)_indicator_var  <= 1
    0 <=  NoClash_(E,F,3,0)_t(E)  <= 92
    0 <=  NoClash_(E,F,3,0)_t(F)  <= 92
    0 <=  NoClash_(E,F,3,1)_indicator_var  <= 1
    0 <=  NoClash_(E,F,3,1)_t(E)  <= 92
    0 <=  NoClash_(E,F,3,1)_t(F)  <= 92
    0 <=  NoClash_(E,G,2,0)_indicator_var  <= 1
    0 <=  NoClash_(E,G,2,0)_t(E)  <= 92
    0 <=  NoClash_(E,G,2,0)_t(G)  <= 92
    0 <=  NoClash_(E,G,2,1)_indicator_var  <= 1
    0 <=  NoClash_(E,G,2,1)_t(E)  <= 92
    0 <=  NoClash_(E,G,2,1)_t(G)  <= 92
    0 <=  NoClash_(E,G,5,0)_indicator_var  <= 1
    0 <=  NoClash_(E,G,5,0)_t(E)  <= 92
    0 <=  NoClash_(E,G,5,0)_t(G)  <= 92
    0 <=  NoClash_(E,G,5,1)_indicator_var  <= 1
    0 <=  NoClash_(E,G,5,1)_t(E)  <= 92
    0 <=  NoClash_(E,G,5,1)_t(G)  <= 92
    0 <=  NoClash_(F,G,4,0)_indicator_var  <= 1
    0 <=  NoClash_(F,G,4,0)_t(F)  <= 92
    0 <=  NoClash_(F,G,4,0)_t(G)  <= 92
    0 <=  NoClash_(F,G,4,1)_indicator_var  <= 1
    0 <=  NoClash_(F,G,4,1)_t(F)  <= 92
    0 <=  NoClash_(F,G,4,1)_t(G)  <= 92
     -inf <=  ms  <= +inf
    0 <=  t(A)  <= 92
    0 <=  t(B)  <= 92
    0 <=  t(C)  <= 92
    0 <=  t(D)  <= 92
    0 <=  t(E)  <= 92
    0 <=  t(F)  <= 92
    0 <=  t(G)  <= 92
binary
  NoClash_(A,B,3,0)_indicator_var
  NoClash_(A,B,3,1)_indicator_var
  NoClash_(A,B,5,0)_indicator_var
  NoClash_(A,B,5,1)_indicator_var
  NoClash_(A,C,1,0)_indicator_var
  NoClash_(A,C,1,1)_indicator_var
  NoClash_(A,D,3,0)_indicator_var
  NoClash_(A,D,3,1)_indicator_var
  NoClash_(A,E,3,0)_indicator_var
  NoClash_(A,E,3,1)_indicator_var
  NoClash_(A,E,5,0)_indicator_var
  NoClash_(A,E,5,1)_indicator_var
  NoClash_(A,F,1,0)_indicator_var
  NoClash_(A,F,1,1)_indicator_var
  NoClash_(A,F,3,0)_indicator_var
  NoClash_(A,F,3,1)_indicator_var
  NoClash_(A,G,5,0)_indicator_var
  NoClash_(A,G,5,1)_indicator_var
  NoClash_(B,C,2,0)_indicator_var
  NoClash_(B,C,2,1)_indicator_var
  NoClash_(B,D,2,0)_indicator_var
  NoClash_(B,D,2,1)_indicator_var
  NoClash_(B,D,3,0)_indicator_var
  NoClash_(B,D,3,1)_indicator_var
  NoClash_(B,E,2,0)_indicator_var
  NoClash_(B,E,2,1)_indicator_var
  NoClash_(B,E,3,0)_indicator_var
  NoClash_(B,E,3,1)_indicator_var
  NoClash_(B,E,5,0)_indicator_var
  NoClash_(B,E,5,1)_indicator_var
  NoClash_(B,F,3,0)_indicator_var
  NoClash_(B,F,3,1)_indicator_var
  NoClash_(B,G,2,0)_indicator_var
  NoClash_(B,G,2,1)_indicator_var
  NoClash_(B,G,5,0)_indicator_var
  NoClash_(B,G,5,1)_indicator_var
  NoClash_(C,D,2,0)_indicator_var
  NoClash_(C,D,2,1)_indicator_var
  NoClash_(C,D,4,0)_indicator_var
  NoClash_(C,D,4,1)_indicator_var
  NoClash_(C,E,2,0)_indicator_var
  NoClash_(C,E,2,1)_indicator_var
  NoClash_(C,F,1,0)_indicator_var
  NoClash_(C,F,1,1)_indicator_var
  NoClash_(C,F,4,0)_indicator_var
  NoClash_(C,F,4,1)_indicator_var
  NoClash_(C,G,2,0)_indicator_var
  NoClash_(C,G,2,1)_indicator_var
  NoClash_(C,G,4,0)_indicator_var
  NoClash_(C,G,4,1)_indicator_var
  NoClash_(D,E,2,0)_indicator_var
  NoClash_(D,E,2,1)_indicator_var
  NoClash_(D,E,3,0)_indicator_var
  NoClash_(D,E,3,1)_indicator_var
  NoClash_(D,F,3,0)_indicator_var
  NoClash_(D,F,3,1)_indicator_var
  NoClash_(D,F,4,0)_indicator_var
  NoClash_(D,F,4,1)_indicator_var
  NoClash_(D,G,2,0)_indicator_var
  NoClash_(D,G,2,1)_indicator_var
  NoClash_(D,G,4,0)_indicator_var
  NoClash_(D,G,4,1)_indicator_var
  NoClash_(E,F,3,0)_indicator_var
  NoClash_(E,F,3,1)_indicator_var
  NoClash_(E,G,2,0)_indicator_var
  NoClash_(E,G,2,1)_indicator_var
  NoClash_(E,G,5,0)_indicator_var
  NoClash_(E,G,5,1)_indicator_var
  NoClash_(F,G,4,0)_indicator_var
  NoClash_(F,G,4,1)_indicator_var
end 
