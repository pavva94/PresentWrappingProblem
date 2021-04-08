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

array[1..2] of int: lower_bounds = [0, 0];
array[1..2] of int: upper_bounds = [w, h];

int: index_of_largest_paper = ordered_index_array[n];
set of int: X_COORDS = lower_bounds[x]..upper_bounds[x]-1;
set of int: Y_COORDS = lower_bounds[y]..upper_bounds[y]-1;

int: min_w = min(papers[.., x]);
int: min_h = min(papers[.., y]);

int: min_dim = min(min_w, min_h);
%Results
array[N_PAPERS, 1..2] of var 0..h-1: coords;

%constraint alldifferent([coords[i,1]*100+coords[i,2] | i in N_PAPERS]);

% cumulative constraint we look at the problem as a resource/time task problem
%constraint cumulative(coords[.., x], papers[.., x], papers[.., y], h);
%constraint cumulative(coords[.., y], papers[.., y], papers[.., x], w);

%cumulative constraint
constraint forall (x_coord in X_COORDS) (
                  sum(i in N_PAPERS) 
                  (if x_coord >= coords[i, x] /\ x_coord < coords[i, x] + papers[i, x] 
                  then papers[i, y] 
                  else 0 endif) = h) 
           /\         
           forall (y_coord in Y_COORDS) (
                  sum(i in N_PAPERS) 
                  (if y_coord >= coords[i, y] /\ y_coord < coords[i, y] + papers[i, y] 
                  then papers[i, x] 
                  else 0 endif) = w);



% stay in the limits W and H
constraint forall(i in N_PAPERS)
              (coords[i,x] <= (w - papers[i,x]));
constraint forall(i in N_PAPERS)
              (coords[i,y] <= (h - papers[i,y]));

% no overlapping between different pieces
constraint diffn_k(coords, papers);

%constraint coords[index_of_largest_paper, 1] <= w+1 - papers[index_of_largest_paper, 1];%w-papers[index_of_largest_paper, 1]+1;
%constraint coords[index_of_largest_paper, 2] <= h+1 - papers[index_of_largest_paper, 2];%w-papers[index_of_largest_paper, 2]+1;

constraint forall(i in N_PAPERS) 
            (lex_greatereq(coords[i, x..y], coords[index_of_largest_paper, x..y]));

%constraint lex_lesseq(coords[.., 1], [w - papers[p, 1] - coords[p, 1] | p in N_PAPERS]);
%constraint lex_lesseq(coords[.., 2], [h - papers[p, 2] - coords[p, 2] | p in N_PAPERS]);


% remove simmetry: wrt x, y and diagonal axis
%constraint lex_lesseq([coords[i,1]*100+coords[i,2] | i in N_PAPERS], [coords[i,2]*100+coords[i,1] | i in N_PAPERS]);
%constraint lex_greatereq([coords[i,1] | i in N_PAPERS], [w - papers[p,1] - coords[p,1] | p in N_PAPERS]);
%constraint lex_greatereq([coords[i,2] | i in N_PAPERS], [h - papers[p,2] - coords[p,2] | p in N_PAPERS]);

% search strategy
ann: search_ann = int_search([coords[i, x] | i in ordered_index_array], dom_w_deg, indomain_random, complete); 
ann: restart_annotation = restart_luby(2000);
solve :: search_ann :: restart_annotation satisfy;

output [
show(w) ++ " " ++ show(h) ++ "\n" ++
show(n) ++ "\n"];
output [
show(papers[i,x]) ++  " " ++ show(papers[i,y]) ++ "\t" ++ show(coords[i,x]) ++ " " ++ show(coords[i,y]) ++ "\n" | i in N_PAPERS
];

%output[show([coords[i,1]*100+coords[i,2] | i in N_PAPERS]) ++"\n"++ show([coords[i,2]*100+coords[i,1] | i in N_PAPERS])];