import random 
import sys 

with open(sys.argv[1], "r") as file:
    for line in file:
        if random.random() < 0.01:
            print(line)