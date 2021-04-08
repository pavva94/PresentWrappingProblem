from os import listdir
from os.path import isfile, join
import matplotlib.pyplot as plt
import random
import math
from matplotlib.patches import Rectangle
from matplotlib.ticker import MultipleLocator
from z3 import *

from PWZ3 import solve_z3, read_txt


def main():
    path_instances = "SMT/in/"
    instances = sorted([f for f in listdir(path_instances) if isfile(join(path_instances, f)) and f.endswith(".txt")])
    print(sorted(instances))

    user_rotation_str = str(input("\n\nDo yo want to use rotation: [Y/N]\n")).upper()
    while user_rotation_str not in ["Y", "N"]:
        user_rotation_str = str(input("\nWrong choice.\nDo yo want to use rotation: [Y/N]\n")).upper()

    if user_rotation_str == "Y":
        user_rotation  = True
    else:
        user_rotation = False

    print("Building the Model...")
    count_iter = 0
    solv_times = []
    solv_propagations = []
    solv_restarts = []
    while count_iter < len(instances):
        instance_choose = instances[count_iter]
        print("Instance: {}".format(instance_choose))
        w, h, n_papers, papers = read_txt(path_instances + instance_choose)
        _, statistics = solve_z3(w, h, n_papers, papers, instance_choose.split('.')[0], user_rotation, print_solutions=False)
        solv_times.append(statistics.time)
        solv_propagations.append(statistics.propagations)
        try:
            rest = statistics.restarts
        except AttributeError as e:
            rest = 0
        solv_restarts.append(rest)
        count_iter += 1

    fig = plt.figure()
    plt.plot(range(8, len(solv_times)+8), solv_times, 'bo')
    plt.yscale('log')
    # beautify the x-labels
    plt.xlabel("Instances")
    plt.ylabel("Solve Time (sec)")

    plt.show()

    plt.figure()
    plt.plot(range(8, len(solv_propagations)+8), solv_propagations, 'bo')
    plt.yscale('log')
    # beautify the x-labels
    plt.xlabel("Instances")
    plt.ylabel("Propagations")

    plt.show()

    fig = plt.figure()
    plt.plot(range(8, len(solv_times)+8), solv_times, 'bo')
    plt.yscale('log')
    # beautify the x-labels
    plt.xlabel("Instances")
    plt.ylabel("Restarts")

    plt.show()

if __name__ == "__main__":
    main()
