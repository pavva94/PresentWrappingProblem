from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import random
import math
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
from z3 import *


def read_txt(path):
    file = open(path,"r").readlines()
    w , h = tuple(map(int, file[0].rstrip("\n").split(" ")))
    n_papers = int(file[1].rstrip("\n"))
    papers = []
    for i in range(2, n_papers + 2):
        papers.append(list(map(int, file[i].rstrip("\n").split(" "))))
    return w, h, n_papers, papers


def draw_single_solution(h, w, n_papers, result, fig, fig_rows, i, colors):
    # Read the first line which contains the width and the height of the paper roll
    solution_in_line = str(result).strip().split("\n")

    width = w
    height = h

    # Read the second line which contains the number of necessary pieces of paper to cut off
    number_of_pieces = n_papers

    axs=fig.add_subplot(fig_rows, 2, i+1)

    for k,paper in enumerate(result):
        rot = paper[4]

        if rot:
            sq = Rectangle((paper[2], paper[3]), paper[1], paper[0], fill = True, color=colors[k], alpha=.3 )
        else:
            sq = Rectangle((paper[2], paper[3]), paper[0], paper[1], fill = True, color=colors[k], alpha=.3 )
        axs.add_patch(sq)

    axs.set(adjustable='box', aspect='equal')


def print_solution(h, w, n_papers, resultList, solutionCounter=1):
    fig_rows = math.ceil(solutionCounter/2)
    fig = plt.figure(figsize=(fig_rows, 2))
    fig.suptitle("Solutions")
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(50)]

    for i in range(len(resultList)):
        if i >= solutionCounter:
            break
        result = resultList[i]

        draw_single_solution(h, w, n_papers, result, fig, fig_rows, i, colors)

        plt.plot()

    plt.show()


def write_solution(instance, w, h, n_papers, papers, coords, rotations, path="SMT/out/"):
    output = open(path + "/" + instance, "w")
    output.write("{} {}\n".format(w, h))
    output.write("{}\n".format(n_papers))
    for i in range(n_papers):
            output.write("{} {} {} {} {}\n".format(int(papers[i][0]), int(papers[i][1]), coords[i][0], coords[i][1], rotations[i]))
    output.close()


def cumulative(solver, h, w, n_papers, coords, rotations, papers):
    for coord_y in range(h):
        listsum = []
        for i in range(n_papers):
            listsum.append(If(
                And(
                    coord_y >= coords[i][1],
                    coord_y < coords[i][1] + getdimension(i, 1, rotations, papers)
                ),
                getdimension(i, 0, rotations, papers),
                0
            ))
        solver.add(Sum(listsum) == w)

    for coord_x in range(w):
        listsum = []
        for i in range(n_papers):
            listsum.append(If(
                And(
                    coord_x >= coords[i][0],
                    coord_x < coords[i][0] + getdimension(i, 0, rotations, papers)
                ),
                getdimension(i, 1, rotations, papers),
                0
            ))
        solver.add(Sum(listsum) == h)


# Stay in limits constraints W and H
def stay_in_limits(solver, coords, n_papers, w, h, rotations, papers):
    for i in range(n_papers):
        solver.add(
            And(
                And(
                    (coords[i][0]+getdimension(i, 0, rotations, papers))<=w,
                    (coords[i][0]>=0)
                ),
                And(
                    (coords[i][1]+getdimension(i, 1, rotations, papers))<=h,
                    (coords[i][1]>=0)
                )
            )
            )


# coordinates of each paper cut all differents
def alldifferent(solver, coords, n_papers):
    for i in range(n_papers):
        for j in range(i+1, n_papers):
            solver.add(
                Distinct(
                    coords[i][0]*100+coords[i][1],
                    coords[j][0]*100+coords[j][1]
                )
            )


# no overlapping bewtween different pieces
def no_overlapping(solver, coords, n_papers, rotations, papers):
    for i in range(n_papers):
        for j in range(i+1, n_papers):
            solver.add(
                        Or(
                            Or(
                                coords[i][0]+getdimension(i, 0, rotations, papers)<=coords[j][0],
                                coords[i][1]+getdimension(i, 1, rotations, papers)<=coords[j][1]
                                ),
                            Or(
                                coords[j][0]+getdimension(j, 0, rotations, papers)<=coords[i][0],
                                coords[j][1]+getdimension(j, 1, rotations, papers)<=coords[i][1]
                                )
                        )
                      )


# remove rotation from squared papers
def no_rotation_on_squared(solver, n_papers, rotations, papers):
    for i in range(n_papers):
        if getdimension(i, 0, rotations, papers)==getdimension(i, 1, rotations, papers):
            solver.add(Not(rotations[i]))

def append_or(i, list1, list2):
    if i == 1:
        return Or(Not(list1[i-1]==list2[i-1]), list1[i]<=list2[i])
    else:
        and_conds = And(list1[0]==list2[0], list1[1]==list2[1])
        for j in range(2, i-1):
            and_conds = And(and_conds, list1[j]==list2[j])
        return Or(Not(and_conds), list1[i]<=list2[i])


def lex_lesseq(solver, list1, list2):
    # temp = list1[0] < list2[0]
    # constr = None
    # for i in range(len(list1)):
    #     constr = Or(list1[i] < list2[i], And(list1[i] == list2[i], temp))
    #     temp = constr
    # solver.add(constr)
    temp = list1[0] <= list2[0]
    for i in range(1, len(list1)):
        temp = And(temp, append_or(i, list1, list2))

    # print(temp)
    solver.add(temp)
    # temp = list1[-1] < list2[-1]
    # constr = None
    # for i in range(len(list1)-2, -1, -1):
    #     constr = Or(list1[i] < list2[i], And(list1[i] == list2[i], temp))
    #     temp = constr
    # solver.add(constr)
    # print(constr)


def getdimension(i, axis, rotations, papers):
    if axis == 0:
        return If(rotations[i], papers[i][1], papers[i][0])
    else:
        return If(rotations[i], papers[i][0], papers[i][1])


def solve_z3(w, h, n_papers, papers, instance):

    coords = [[Int("c_{}_{}".format(i, j)) for j in range(2)]
               for i in range(n_papers)]

    rotations = [Bool("r_{}".format(i)) for i in range(n_papers)]

    solver = Solver()

    # adding the constraints
    cumulative(solver, h, w, n_papers, coords, rotations, papers)
    stay_in_limits(solver, coords, n_papers, w, h, rotations, papers)
    alldifferent(solver, coords, n_papers)
    no_overlapping(solver, coords, n_papers, rotations, papers)
    no_rotation_on_squared(solver, n_papers, rotations, papers)
    lex_lesseq(solver, [coords[i][0]*100+coords[i][1] for i in range(n_papers)], [coords[i][1]*100+coords[i][0] for i in range(n_papers)])
    lex_lesseq(solver, [coords[i][0] for i in range(n_papers)], [w - getdimension(p, 0, rotations, papers) - coords[p][0] for p in range(n_papers)])
    lex_lesseq(solver, [coords[i][1] for i in range(n_papers)], [h - getdimension(p, 1, rotations, papers) - coords[p][1] for p in range(n_papers)])

    max_solution = 6
    max_step = 100
    results = []
    write_sol = True
    counter_solutions = 0
    counter_step = 0


    while solver.check() == sat:
    print("Solving...")
        model = solver.model()
        result = [[papers[i][0], papers[i][1], model.evaluate(coords[i][0]).as_long(),    model.evaluate(coords[i][1]).as_long(), model.evaluate(rotations[i])] for i in range(n_papers) ]

        if result not in results:  # or counter_solution >= max_solution:
            results.append(result)
            counter_solutions += 1

        print(result)
        if counter_step >= max_step:
            break
        counter_step += 1

        if write_sol:
            write_solution(
                instance + "-out.txt", w, h, n_papers, papers,
                [ [model.evaluate(coords[i][0]),    model.evaluate(coords[i][1]), model.evaluate(rotations[i])] for i in range(n_papers) ],
                [ model.evaluate(rotations[i]) for i in range(n_papers) ])
            write_sol = False
            print(solver.statistics())

    else:
        print("UNSAT")


    print("number of solutions: " + str(counter_solutions))

    if results:
        print_solution(w, h, n_papers, results)

    return results



def main():
    path_instances = "SMT/in/"
    instances = sorted([f for f in listdir(path_instances) if isfile(join(path_instances, f)) and f.endswith(".txt")])
    print(sorted(instances))
    instance_choose = str(input("\n\nChoose an instance: [without the extension]\n"))  #"08x08"
    instance_choose += ".txt"

    while instance_choose not in instances:
        instance_choose = str(input("\nWrong choice.\nChoose an instance: [without the extension]\n"))  #"08x08"
        instance_choose += ".txt"

    w, h, n_papers, papers = read_txt(path_instances + instance_choose)
    results = solve_z3(w, h, n_papers, papers, instance_choose.split('.')[0])



if __name__ == "__main__":
    main()
