min 
makespan:
+1.000000 ms

s.t.

c_u_Feas(A)_:
-1.000000 ms
+1.000000 t(A)
<= -8.0

c_u_Feas(B)_:
-1.000000 ms
+1.000000 t(B)
<= -5.0

c_u_Feas(C)_:
-1.000000 ms
+1.000000 t(C)
<= -6.0

c_u_NoClash_(A_C_1_0)_c_hi_:
+2.000000 NoClash_(A_C_1_0)_indicator_var
-1.000000 NoClash_(A_C_1_0)_t(A)
+1.000000 NoClash_(A_C_1_0)_t(C)
<= 0.0

c_u_NoClash_(B_C_2_0)_c_hi_:
+6.000000 NoClash_(B_C_2_0)_indicator_var
-1.000000 NoClash_(B_C_2_0)_t(B)
+1.000000 NoClash_(B_C_2_0)_t(C)
<= 0.0

c_u_NoClash_(A_B_3_1)_c_hi_:
+5.000000 NoClash_(A_B_3_1)_indicator_var
+1.000000 NoClash_(A_B_3_1)_t(A)
-1.000000 NoClash_(A_B_3_1)_t(B)
<= 0.0

c_u_NoClash_(A_C_1_1)_c_hi_:
+5.000000 NoClash_(A_C_1_1)_indicator_var
+1.000000 NoClash_(A_C_1_1)_t(A)
-1.000000 NoClash_(A_C_1_1)_t(C)
<= 0.0

c_u_NoClash_(B_C_2_1)_c_hi_:
+1.000000 NoClash_(B_C_2_1)_indicator_var
+1.000000 NoClash_(B_C_2_1)_t(B)
-1.000000 NoClash_(B_C_2_1)_t(C)
<= 0.0

c_u_NoClash_(A_B_3_0)_c_hi_:
-1.000000 NoClash_(A_B_3_0)_t(A)
+1.000000 NoClash_(A_B_3_0)_t(B)
<= 0.0

c_e_disj(_A___B__3)_:
+1.000000 NoClash_(A_B_3_0)_indicator_var
+1.000000 NoClash_(A_B_3_1)_indicator_var
= 1.0

c_e_disj(_A___C__1)_:
+1.000000 NoClash_(A_C_1_0)_indicator_var
+1.000000 NoClash_(A_C_1_1)_indicator_var
= 1.0

c_e_disj(_B___C__2)_:
+1.000000 NoClash_(B_C_2_0)_indicator_var
+1.000000 NoClash_(B_C_2_1)_indicator_var
= 1.0

c_e_disj_(A_B_3)_t(A)_:
-1.000000 NoClash_(A_B_3_0)_t(A)
-1.000000 NoClash_(A_B_3_1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A_B_3)_t(B)_:
-1.000000 NoClash_(A_B_3_0)_t(B)
-1.000000 NoClash_(A_B_3_1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(A_C_1)_t(A)_:
-1.000000 NoClash_(A_C_1_0)_t(A)
-1.000000 NoClash_(A_C_1_1)_t(A)
+1.000000 t(A)
= 0.0

c_e_disj_(A_C_1)_t(C)_:
-1.000000 NoClash_(A_C_1_0)_t(C)
-1.000000 NoClash_(A_C_1_1)_t(C)
+1.000000 t(C)
= 0.0

c_e_disj_(B_C_2)_t(B)_:
-1.000000 NoClash_(B_C_2_0)_t(B)
-1.000000 NoClash_(B_C_2_1)_t(B)
+1.000000 t(B)
= 0.0

c_e_disj_(B_C_2)_t(C)_:
-1.000000 NoClash_(B_C_2_0)_t(C)
-1.000000 NoClash_(B_C_2_1)_t(C)
+1.000000 t(C)
= 0.0

c_u_NoClash_(A_B_3_0)_t(A)_hi_:
-19.000000 NoClash_(A_B_3_0)_indicator_var
+1.000000 NoClash_(A_B_3_0)_t(A)
<= 0.0

c_u_NoClash_(A_B_3_0)_t(B)_hi_:
-19.000000 NoClash_(A_B_3_0)_indicator_var
+1.000000 NoClash_(A_B_3_0)_t(B)
<= 0.0

c_u_NoClash_(A_B_3_1)_t(A)_hi_:
-19.000000 NoClash_(A_B_3_1)_indicator_var
+1.000000 NoClash_(A_B_3_1)_t(A)
<= 0.0

c_u_NoClash_(A_B_3_1)_t(B)_hi_:
-19.000000 NoClash_(A_B_3_1)_indicator_var
+1.000000 NoClash_(A_B_3_1)_t(B)
<= 0.0

c_u_NoClash_(A_C_1_0)_t(A)_hi_:
-19.000000 NoClash_(A_C_1_0)_indicator_var
+1.000000 NoClash_(A_C_1_0)_t(A)
<= 0.0

c_u_NoClash_(A_C_1_0)_t(C)_hi_:
-19.000000 NoClash_(A_C_1_0)_indicator_var
+1.000000 NoClash_(A_C_1_0)_t(C)
<= 0.0

c_u_NoClash_(A_C_1_1)_t(A)_hi_:
-19.000000 NoClash_(A_C_1_1)_indicator_var
+1.000000 NoClash_(A_C_1_1)_t(A)
<= 0.0

c_u_NoClash_(A_C_1_1)_t(C)_hi_:
-19.000000 NoClash_(A_C_1_1)_indicator_var
+1.000000 NoClash_(A_C_1_1)_t(C)
<= 0.0

c_u_NoClash_(B_C_2_0)_t(B)_hi_:
-19.000000 NoClash_(B_C_2_0)_indicator_var
+1.000000 NoClash_(B_C_2_0)_t(B)
<= 0.0

c_u_NoClash_(B_C_2_0)_t(C)_hi_:
-19.000000 NoClash_(B_C_2_0)_indicator_var
+1.000000 NoClash_(B_C_2_0)_t(C)
<= 0.0

c_u_NoClash_(B_C_2_1)_t(B)_hi_:
-19.000000 NoClash_(B_C_2_1)_indicator_var
+1.000000 NoClash_(B_C_2_1)_t(B)
<= 0.0

c_u_NoClash_(B_C_2_1)_t(C)_hi_:
-19.000000 NoClash_(B_C_2_1)_indicator_var
+1.000000 NoClash_(B_C_2_1)_t(C)
<= 0.0

c_e_ONE_VAR_CONSTANT: 
ONE_VAR_CONSTANT = 1.0

bounds 
    0.0 <=  NoClash_(A_B_3_0)_indicator_var  <= 1.0
    0.0 <=  NoClash_(A_B_3_0)_t(A)  <= 19.0
    0.0 <=  NoClash_(A_B_3_0)_t(B)  <= 19.0
    0.0 <=  NoClash_(A_B_3_1)_indicator_var  <= 1.0
    0.0 <=  NoClash_(A_B_3_1)_t(A)  <= 19.0
    0.0 <=  NoClash_(A_B_3_1)_t(B)  <= 19.0
    0.0 <=  NoClash_(A_C_1_0)_indicator_var  <= 1.0
    0.0 <=  NoClash_(A_C_1_0)_t(A)  <= 19.0
    0.0 <=  NoClash_(A_C_1_0)_t(C)  <= 19.0
    0.0 <=  NoClash_(A_C_1_1)_indicator_var  <= 1.0
    0.0 <=  NoClash_(A_C_1_1)_t(A)  <= 19.0
    0.0 <=  NoClash_(A_C_1_1)_t(C)  <= 19.0
    0.0 <=  NoClash_(B_C_2_0)_indicator_var  <= 1.0
    0.0 <=  NoClash_(B_C_2_0)_t(B)  <= 19.0
    0.0 <=  NoClash_(B_C_2_0)_t(C)  <= 19.0
    0.0 <=  NoClash_(B_C_2_1)_indicator_var  <= 1.0
    0.0 <=  NoClash_(B_C_2_1)_t(B)  <= 19.0
    0.0 <=  NoClash_(B_C_2_1)_t(C)  <= 19.0
     -inf <=  ms  <= +inf
    0.0 <=  t(A)  <= 19.0
    0.0 <=  t(B)  <= 19.0
    0.0 <=  t(C)  <= 19.0
binary
  NoClash_(A_B_3_0)_indicator_var
  NoClash_(A_B_3_1)_indicator_var
  NoClash_(A_C_1_0)_indicator_var
  NoClash_(A_C_1_1)_indicator_var
  NoClash_(B_C_2_0)_indicator_var
  NoClash_(B_C_2_1)_indicator_var
end 
