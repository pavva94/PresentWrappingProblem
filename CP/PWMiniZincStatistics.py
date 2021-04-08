from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
from minizinc import Instance, Model, Solver


path_dzn = "CP/in/"
path_solution = "CP/out/"
path_solution_rot = "CP/out-rot/"


def main():
    file_instances = sorted([f for f in listdir(path_dzn) if isfile(join(path_dzn, f)) and f.endswith(".dzn")])
    user_rotation_str = str(input("\n\nDo yo want to use rotation: [Y/N]\n")).upper()
    while user_rotation_str not in ["Y", "N"]:
        user_rotation_str = str(input("\nWrong choice.\nDo yo want to use rotation: [Y/N]\n")).upper()

    print("Building the Model...")
    gecode = Solver.lookup("gecode")

    count_iter = 0
    solv_times = []
    while (count_iter < len(file_instances)):
        model = Model()
        if user_rotation_str == "Y":
            model.add_file("CP/OptimizationProjectRotation.mzn")
            path_solution_choosen = path_solution_rot
            user_rotation = True
        else:
            model.add_file("CP/OptimizationProject.mzn")
            path_solution_choosen = path_solution
            user_rotation = False

        instance_choose = file_instances[count_iter]
        model.add_file(path_dzn + instance_choose)

        instance = Instance(gecode, model)

        print("Solving instance: {}".format(instance_choose))
        result = instance.solve(all_solutions=False)
        #write_solution(path_solution_choosen, instance_choose.split('.')[0], str(result.solution))
        #print_solution(result, 1, user_rotation=user_rotation)
        print("Solving Time")
        print(result.solution)
        print(result.statistics)
        print(result.statistics['solveTime'])
        solv_times.append(result.statistics['solveTime'].total_seconds())
        count_iter += 1


    fig = plt.figure()
    plt.plot(range(8, len(solv_times)+8), solv_times, 'bo')
    plt.yscale('log')
    # beautify the x-labels
    plt.xlabel("Instances")
    plt.ylabel("Solve Time (sec)")

    plt.show()


if __name__ == "__main__":
    main()
