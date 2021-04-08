# PresentWrappingProblem
This is the repository for the Present Wrapping Problem, 
This problem was the Exam of the first module of Combinatorial Decision Making.


## How to use
We have created a user-friendly interface to be used by the Terminal/Command-Prompt. 
Once the user is in the main folder it can use **python3** to launch the program.
```
python3 PresentWrapping.py
```

Once launched the program it will ask what kind of technique you want to use:
```
Welcome to the present wrapping problem! Make your choice:
1)Minizinc
2)Z3
```

Picked one of the choices the program will ask what instance do you want to use.

```
['08x08.txt', '09x09.txt', '10x10.txt', ...]

Choose an instance: [without the extension]
```

Lastly, one more question is asked about the use of the rotation:
```
Do you want to use rotation: [Y/N]
```

In the end, the program will plot the solution if find it as well as some useful statistics. 
The use of this interface as a main is optional, it's possible to launch the file associated to the chosen Program and run it:
```
python3 SMT/PWZ3.py
python3 CP/PWMinizinc.py
```
