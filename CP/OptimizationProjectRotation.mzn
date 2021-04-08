%Project
include "globals.mzn";

%Datas
int: w; %width of container
int: h; %height of container
int: n; %number of pieces to cut off

int: x=1;
int: y=2;

set of int: N_PAPERS = 1..n;

array[N_PAPERS, x..y] of int: papers;  % dimensions (width, height)

array[N_PAPERS] of int: ordered_index_array = sort_by(N_PAPERS, [papers[i,x] + papers[i,y] | i in N_PAPERS]);

array[1..2] of int: coords_domain_lower = [0, 0];
array[1..2] of int: coords_domain_upper = [w, h];

int: index_of_largest_paper = ordered_index_array[n];
set of int: X_COORDS = coords_domain_lower[x]..coords_domain_upper[x]-1;
set of int: Y_COORDS = coords_domain_lower[y]..coords_domain_upper[y]-1;

%Results
array[N_PAPERS, x..y] of var 0..h-1: coords;

% Define rotation property for the pieces of paper
array[N_PAPERS] of var bool: rotations;

% get dimension based on axis and rotation
% i: index of paper, axis: X or Y


function var int: get_dimension(int: i, int: axis) = 
    if axis == x then 
        if rotations[i] then papers[i, y] 
        else papers[i, x] endif
    else
        if rotations[i] then papers[i, x] 
        else papers[i, y] endif
    endif;

% cumulative constraint we look at the problem as a resource/time task problem
constraint forall (x_coord in X_COORDS) (
                sum(i in N_PAPERS) 
                    (if x_coord >= coords[i, x] /\ x_coord < coords[i, x] + get_dimension(i, x) 
                     then get_dimension(i, y) 
                     else 0 endif) = h) 
           /\         
           forall (y_coord in Y_COORDS) (
                sum(i in N_PAPERS) 
                    (if y_coord >= coords[i, y] /\ y_coord < coords[i, y] + get_dimension(i, y) 
                    then get_dimension(i, x) 
                    else 0 endif) = w);

%constraint alldifferent([coords[i,1]*100+coords[i,2] | i in N_PAPERS]);

% stay in the limits W and H
constraint forall(i in N_PAPERS)
              (coords[i, x] <= (w - get_dimension(i,x)))/\
           forall(i in N_PAPERS)
               (coords[i, y] <= (h - get_dimension(i,y)));

% no overlapping between different pieces
constraint diffn(coords[.., x],
                 coords[..,y],
                 [get_dimension(i,x) | i in N_PAPERS],
                 [get_dimension(i,y) | i in N_PAPERS]);
 
 
constraint forall(i in N_PAPERS) 
            (lex_greatereq(coords[i, x..y], coords[index_of_largest_paper, x..y]));

 
% remove simmetry: wrt x, y and diagonal axis
%constraint lex_lesseq([coords[i,1]*100+coords[i,2] | i in N_PAPERS], [coords[i,2]*100+coords[i,1] | i in N_PAPERS]);
%constraint lex_greatereq([coords[i,1] | i in N_PAPERS], [w - papers[p,1] - coords[p,1] | p in N_PAPERS]);
%constraint lex_greatereq([coords[i,2] | i in N_PAPERS], [h - papers[p,2] - coords[p,2] | p in N_PAPERS]);

% remove rotation from squared papers  
constraint forall(i in N_PAPERS where get_dimension(i,x) == get_dimension(i,y)) (rotations[i]=0);

% force to rotate at least one of the pieces
constraint sum([rotations[i] | i in N_PAPERS]) >= 1;

% search strategy
ann: search_ann = int_search([coords[i, x] | i in ordered_index_array], dom_w_deg, indomain_min, complete); 
ann: restart_annotation = restart_luby(5000);
solve :: search_ann :: restart_annotation satisfy;

% print results
output [
show(w) ++ " " ++ show(h) ++ "\n" ++
show(n) ++ "\n"];
output [
show(papers[i,x]) ++  " " ++ show(papers[i,y]) ++ "\t" ++ show(coords[i,1]) ++ " " ++ show(coords[i,2]) ++ " " ++ show(rotations[i]) ++ "\n" | i in N_PAPERS
];