from CP.PWMiniZinc import main as minizinc_execute
from SMT.PWZ3 import main as z3_execute




def main():
    print("\n\nWelcome to the present wrapping problem! Make your choice:\n1)Minizinc\n2)Z3")
    choice = int(input());

    while(choice not in [1,2]):
        print("Invalid choice, please select 1 for MiniZinc or 2 for Z3")
        choice = int(input());

    #Choice == MiniZinc
    if choice==1:
        minizinc_execute()

    #Choice == Z3
    elif choice==2:
        z3_execute()


if __name__ == "__main__":
    main()
