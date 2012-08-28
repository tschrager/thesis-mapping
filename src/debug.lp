\* test123 *\
Minimize
OBJ: - 0.9 None_elastic_SubProblem_neg_penalty_var
 + 0.9 None_elastic_SubProblem_pos_penalty_var + w + 9 z + x + 4 y
Subject To
None_elastic_SubProblem_Constraint: None_elastic_SubProblem_neg_penalty_var
 + None_elastic_SubProblem_pos_penalty_var
 + None_elastic_SubProblem_free_bound + w >= -1
c1: x + y <= 5
c2: z + x >= 10
c3: z - y = 7
Bounds
-inf <= None_elastic_SubProblem_neg_penalty_var <= 0
None_elastic_SubProblem_free_bound = 0
w free
x <= 4
-1 <= y <= 1
End
