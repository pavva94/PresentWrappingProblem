%Project
include "globals.mzn";

%Datas
int: w; %width of container
int: h; %height of container
int: n; %number of pieces to cut off

set of int: N_PAPERS = 1..n;

array[N_PAPERS, 1..2] of int: papers;  % dimensions (width, height)

%Results
array[N_PAPERS, 1..2] of var 1..h: coords;

% Define rotation property for the pieces of paper
array[N_PAPERS] of var bool: rotations;

% get dimension based on axis and rotation
% i: index of paper, axis: 0 for X, 1 for Y
function var int: get_dimension(int: i, int: axis) = 
    if axis == 1 then 
        if rotations[i] then papers[i, 2] 
        else papers[i, 1] endif
    else
        if rotations[i] then papers[i, 1] 
        else papers[i, 2] endif
    endif;

% cumulative constraint we look at the problem as a resource/time task problem
constraint cumulative(coords[.., 1], [get_dimension(i,1) | i in N_PAPERS], [get_dimension(i,2) | i in N_PAPERS], h);
constraint cumulative(coords[.., 2], [get_dimension(i,2) | i in N_PAPERS], [get_dimension(i,1) | i in N_PAPERS], w);


% stay in the limits W and H
constraint forall(i in N_PAPERS)
              ((coords[i,1]+get_dimension(i,1))<=w+1)/\
           forall(i in N_PAPERS)
               ((coords[i,2]+get_dimension(i,2))<=h+1);

% no overlapping between different pieces
constraint diffn(coords[.., 1],
                 coords[..,2],
                 [get_dimension(i,1) | i in N_PAPERS],
                 [get_dimension(i,2) | i in N_PAPERS]);
   
% remove simmetry: wrt x, y and diagonal axis
constraint lex_lesseq([coords[i,1]*100+coords[i,2] | i in N_PAPERS], [coords[i,2]*100+coords[i,1] | i in N_PAPERS]);
constraint lex_lesseq([coords[i,1] | i in N_PAPERS], [w - get_dimension(p,1) - coords[p,1] | p in N_PAPERS]);
constraint lex_lesseq([coords[i,2] | i in N_PAPERS], [h - get_dimension(p,2) - coords[p,2] | p in N_PAPERS]);

% remove rotation from squared papers  
constraint forall(i in N_PAPERS where get_dimension(i,1) == get_dimension(i,2)) (rotations[i]=0);

solve satisfy;
%Programmed search
%ann: search_ann;
%search_ann = int_search(coords, input_order, indomain_min);
%search_ann = int_search(coords, first_fail, indomain_min);
%search_ann = int_search(coords, dom_w_deg, indomain_min); 
%search_ann = int_search(coords, input_order, indomain_random);
%search_ann = int_search(coords, dom_w_deg, indomain_random); 
%solve :: search_ann  satisfy;

output [
show(w) ++ " " ++ show(h) ++ "\n" ++
show(n) ++ "\n"];
output [
show(papers[i,1]) ++  " " ++ show(papers[i,2]) ++ "\t" ++ show(coords[i,1]) ++ " " ++ show(coords[i,2]) ++ " " ++ show(rotations[i]) ++ "\n" | i in N_PAPERS
];