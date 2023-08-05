min 
makespan:
+1.000000 ms

s.t.

c_u_Feas(A)_:
-1.000000 ms
+1.000000 t(A)
<= -8

c_u_Feas(B)_:
-1.000000 ms
+1.000000 t(B)
<= -5

c_u_Feas(C)_:
-1.000000 ms
+1.000000 t(C)
<= -6

c_u_NoClash_(A,C,1,0)_c_hi_:
+2.000000 NoClash_(A,C,1,0)_indicator_var
-1.000000 NoClash_(A,C,1,0)_t(A)
+1.000000 NoClash_(A,C,1,0)_t(C)
<= 0.0

c_u_NoClash_(B,C,2,0)_c_hi_:
+6.000000 NoClash_(B,C,2,0)_indicator_var
-1.000000 NoClash_(B,C,2,0)_t(B)
+1.000000 NoClash_(B,C,2,0)_t(C)
<= 0.0

c_u_NoClash_(A,B,3,1)_c_hi_:
+5.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(A)
-1.000000 NoClash_(A,B,3,1)_t(B)
<= 0.0

c_u_NoClash_(A,C,1,1)_c_hi_:
+5.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(A)
-1.000000 NoClash_(A,C,1,1)_t(C)
<= 0.0

c_u_NoClash_(B,C,2,1)_c_hi_:
+1.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(B)
-1.000000 NoClash_(B,C,2,1)_t(C)
<= 0.0

c_u_NoClash_(A,B,3,0)_c_hi_:
-1.000000 NoClash_(A,B,3,0)_t(A)
+1.000000 NoClash_(A,B,3,0)_t(B)
<= 0.0

c_e_disj(_A_,_B_,3)_:
+1.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,1)_indicator_var
= 1.0

c_e_disj(_A_,_C_,1)_:
+1.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,1)_indicator_var
= 1.0

c_e_disj(_B_,_C_,2)_:
+1.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,1)_indicator_var
= 1.0

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

c_u_NoClash_(A,B,3,0)_t(A)_hi_:
-19.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,0)_t(A)
<= 0.0

c_u_NoClash_(A,B,3,0)_t(B)_hi_:
-19.000000 NoClash_(A,B,3,0)_indicator_var
+1.000000 NoClash_(A,B,3,0)_t(B)
<= 0.0

c_u_NoClash_(A,B,3,1)_t(A)_hi_:
-19.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(A)
<= 0.0

c_u_NoClash_(A,B,3,1)_t(B)_hi_:
-19.000000 NoClash_(A,B,3,1)_indicator_var
+1.000000 NoClash_(A,B,3,1)_t(B)
<= 0.0

c_u_NoClash_(A,C,1,0)_t(A)_hi_:
-19.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,0)_t(A)
<= 0.0

c_u_NoClash_(A,C,1,0)_t(C)_hi_:
-19.000000 NoClash_(A,C,1,0)_indicator_var
+1.000000 NoClash_(A,C,1,0)_t(C)
<= 0.0

c_u_NoClash_(A,C,1,1)_t(A)_hi_:
-19.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(A)
<= 0.0

c_u_NoClash_(A,C,1,1)_t(C)_hi_:
-19.000000 NoClash_(A,C,1,1)_indicator_var
+1.000000 NoClash_(A,C,1,1)_t(C)
<= 0.0

c_u_NoClash_(B,C,2,0)_t(B)_hi_:
-19.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,0)_t(B)
<= 0.0

c_u_NoClash_(B,C,2,0)_t(C)_hi_:
-19.000000 NoClash_(B,C,2,0)_indicator_var
+1.000000 NoClash_(B,C,2,0)_t(C)
<= 0.0

c_u_NoClash_(B,C,2,1)_t(B)_hi_:
-19.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(B)
<= 0.0

c_u_NoClash_(B,C,2,1)_t(C)_hi_:
-19.000000 NoClash_(B,C,2,1)_indicator_var
+1.000000 NoClash_(B,C,2,1)_t(C)
<= 0.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    0 <=  NoClash_(A,B,3,0)_indicator_var  <= 1
    0 <=  NoClash_(A,B,3,0)_t(A)  <= 19
    0 <=  NoClash_(A,B,3,0)_t(B)  <= 19
    0 <=  NoClash_(A,B,3,1)_indicator_var  <= 1
    0 <=  NoClash_(A,B,3,1)_t(A)  <= 19
    0 <=  NoClash_(A,B,3,1)_t(B)  <= 19
    0 <=  NoClash_(A,C,1,0)_indicator_var  <= 1
    0 <=  NoClash_(A,C,1,0)_t(A)  <= 19
    0 <=  NoClash_(A,C,1,0)_t(C)  <= 19
    0 <=  NoClash_(A,C,1,1)_indicator_var  <= 1
    0 <=  NoClash_(A,C,1,1)_t(A)  <= 19
    0 <=  NoClash_(A,C,1,1)_t(C)  <= 19
    0 <=  NoClash_(B,C,2,0)_indicator_var  <= 1
    0 <=  NoClash_(B,C,2,0)_t(B)  <= 19
    0 <=  NoClash_(B,C,2,0)_t(C)  <= 19
    0 <=  NoClash_(B,C,2,1)_indicator_var  <= 1
    0 <=  NoClash_(B,C,2,1)_t(B)  <= 19
    0 <=  NoClash_(B,C,2,1)_t(C)  <= 19
     -inf <=  ms  <= +inf
    0 <=  t(A)  <= 19
    0 <=  t(B)  <= 19
    0 <=  t(C)  <= 19
binary
  NoClash_(A,B,3,0)_indicator_var
  NoClash_(A,B,3,1)_indicator_var
  NoClash_(A,C,1,0)_indicator_var
  NoClash_(A,C,1,1)_indicator_var
  NoClash_(B,C,2,0)_indicator_var
  NoClash_(B,C,2,1)_indicator_var
end 
