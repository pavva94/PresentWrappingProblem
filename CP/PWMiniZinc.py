from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import random
import math
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
from minizinc import Instance, Model, Solver


path_dzn = "CP/in/"
path_solution = "CP/out/"
path_solution_rot = "CP/out-rot/"


def read_txt(path):
    file = open(path,"r").readlines()
    w , h = tuple(map(int, file[0].rstrip("\n").split(" ")))
    n_papers = int(file[1].rstrip("\n"))
    papers = []
    for i in range(2, n_papers + 2):
        papers.append(list(map(int, file[i].rstrip("\n").split(" "))))
    return w, h, n_papers, papers


def draw_single_solution_rotation(result, fig, fig_rows, i, colors):
	# Read the first line which contains the width and the height of the paper roll
	solution_in_line = str(result).strip().split("\n")

	width = int(solution_in_line[0].split(" ")[0])
	height = int(solution_in_line[0].split(" ")[1])

	# Read the second line which contains the number of necessary pieces of paper to cut off

	number_of_pieces = int(solution_in_line[1].strip())

	papers = []

	for line in solution_in_line[2:]:
		line = line.split()
		papers.append([int(line[0]),int(line[1]),int(line[2]),int(line[3]), True if line[4]=="true" else False])

	print("Width: {}, Height: {}, N: {}, Paper:{}".format(width, height, number_of_pieces, papers))
	axs=fig.add_subplot(fig_rows, 2, i+1)

	for k,paper in enumerate(papers):
		rot = paper[4]
		print(rot)
		if rot:
			sq = Rectangle((paper[2],paper[3]),paper[1],paper[0],fill = True,color=colors[k], alpha=.3 )
		else:
			sq = Rectangle((paper[2],paper[3]),paper[0],paper[1],fill = True,color=colors[k], alpha=.3 )
		axs.add_patch(sq)

	axs.set(adjustable='box', aspect='equal')

def draw_single_solution(result, fig, fig_rows, i, colors):
	# Read the first line which contains the width and the height of the paper roll
	solution_in_line = str(result).strip().split("\n")

	width = int(solution_in_line[0].split(" ")[0])
	height = int(solution_in_line[0].split(" ")[1])

	# Read the second line which contains the number of necessary pieces of paper to cut off

	number_of_pieces = int(solution_in_line[1].strip())

	papers = []

	for line in solution_in_line[2:]:
		line = line.split()
		papers.append([int(line[0]),int(line[1]),int(line[2]),int(line[3])])

	print("Width: {}, Height: {}, N: {}, Paper:{}".format(width, height, number_of_pieces, papers))
	axs=fig.add_subplot(fig_rows, 2, i+1)

	for k,paper in enumerate(papers):
		sq = Rectangle((paper[2],paper[3]),paper[0],paper[1],fill = True,color=colors[k], alpha=.3 )
		axs.add_patch(sq)

	axs.set(adjustable='box', aspect='equal')

def print_solution(resultList, solutionCounter=6, user_rotation=False):
    fig_rows = math.ceil(solutionCounter/2)
    fig = plt.figure(figsize=(fig_rows, 2))
    fig.suptitle("Solutions")
    colors = ["#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)]) for k in range(50)]

    if type(resultList.solution) is not list:
        if user_rotation:
            draw_single_solution_rotation(str(resultList.solution), fig, fig_rows, 0, colors)
        else:
            draw_single_solution(str(resultList.solution), fig, fig_rows, 0, colors)
        plt.plot()

    else:
        print(len(resultList.solution))
        for i in range(len(resultList.solution)):
            if i < solutionCounter:
                r = resultList.solution[i]
                if user_rotation:
                    draw_single_solution_rotation(r, fig, fig_rows, i, colors)
                else:
                    draw_single_solution(r, fig, fig_rows, i, colors)
                    plt.plot()

    plt.show()


def write_solution(path_solution, instance_choose, result):

    filename = instance_choose + "-out" + ".txt"
    solution_file = path_solution + filename

    file = open(solution_file,"w+")
    file.write(result)
    file.close()
    return filename


def main():
    file_instances = [f for f in listdir(path_dzn) if isfile(join(path_dzn, f)) and f.endswith(".dzn")]
    print(sorted(file_instances))
    instance_choose_name = str(input("\n\nChoose an instance: [without the extension]\n"))
    instance_choose = instance_choose_name + ".dzn"

    while instance_choose not in file_instances:
        instance_choose_name = str(input("\nWrong choice.\nChoose an instance: [without the extension]\n"))  #"08x08"
        instance_choose = instance_choose_name + ".dzn"

    user_rotation = str(input("\n\nDo yo want to use rotation: [Y/N]\n")).upper()
    while user_rotation not in ["Y", "N"]:
        user_rotation = str(input("\nWrong choice.\nDo yo want to use rotation: [Y/N]\n")).upper()

    print("Building the Model...")
    gecode = Solver.lookup("gecode")

    model = Model()
    if user_rotation == "Y":
        model.add_file("CP/OptimizationProjectRotation.mzn")
        path_solution_choosen = path_solution_rot
        user_rotation = True
    else:
        model.add_file("CP/OptimizationProject.mzn")
        path_solution_choosen = path_solution
        user_rotation = False

    model.add_file(path_dzn + instance_choose)

    instance = Instance(gecode, model)

    print("Solving...")
    all_sol = False
    counter_solutions = 10
    if all_sol:
            result = instance.solve(nr_solutions=counter_solutions)
            print("Stats")
            print(result.statistics)
            print_solution(result, user_rotation=user_rotation)

    else:
            result = instance.solve(all_solutions=False)
            write_solution(path_solution_choosen, instance_choose_name, str(result.solution))
            print_solution(result, 1, user_rotation=user_rotation)
            print("Stats")
            print(result.statistics)

if __name__ == "__main__":
    main()
