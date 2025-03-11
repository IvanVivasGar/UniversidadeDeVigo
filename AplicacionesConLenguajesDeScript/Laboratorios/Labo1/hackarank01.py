import math

def weird(n):
    if n % 2 != 0:
        print("Weird")
    elif n >= 2 and n < 6:
        print("Not Weird")
    elif n > 20:
        print("Not Weird")
    else:
        print("Weird")

weird(int(input()))

def loop():
    n = int(input())
    for i in range(n):
        print(int(math.pow(i, 2)))

def write_function():
    def is_leap(year):
        leap = False

        if year % 4 == 0:
            if year % 100 == 0:
                if year % 400 == 0:
                    leap = True
            else:
                leap = True

        return leap

    year = int(input())
    print(is_leap(year))