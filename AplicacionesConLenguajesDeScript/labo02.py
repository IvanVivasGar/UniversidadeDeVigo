import operator

def evaluate(tokens, is_prefix=True):
    ops = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv}

    def helper(index):
        token = tokens[index]
        if token in ops:
            if is_prefix:
                left, new_index = helper(index + 1)
                right, new_index = helper(new_index)
            else:
                right, new_index = helper(index - 1)
                left, new_index = helper(new_index)
            return ops[token](left, right), new_index
        else:
            return float(token), (index + 1 if is_prefix else index - 1)

    result, _ = helper(0 if is_prefix else len(tokens) - 1)
    return result

def main():
    expr = input("Ingrese una expresión prefija o postfija: ")
    tokens = expr.split()

    if tokens[0] in {'+', '-', '*', '/'}:
        print("Resultado (prefijo):", evaluate(tokens, is_prefix=True))
    elif tokens[-1] in {'+', '-', '*', '/'}:
        print("Resultado (postfijo):", evaluate(tokens, is_prefix=False))
    else:
        print("Expresión inválida")

if __name__ == "__main__":
    main()



### HACKERRANK ###

if __name__ == '__main__':
    N = int(input())
    lst = []

    for _ in range(N):
        command = input().split()

        if command[0] == "insert":
            lst.insert(int(command[1]), int(command[2]))
        elif command[0] == "print":
            print(lst)
        elif command[0] == "remove":
            lst.remove(int(command[1]))
        elif command[0] == "append":
            lst.append(int(command[1]))
        elif command[0] == "sort":
            lst.sort()
        elif command[0] == "pop":
            lst.pop()
        elif command[0] == "reverse":
            lst.reverse()

if __name__ == '__main__':
    x = int(input())
    y = int(input())
    z = int(input())
    n = int(input())

    result = [[i, j, k] for i in range(x + 1) for j in range(y + 1) for k in range(z + 1) if i + j + k != n]
    print(result)

if __name__ == '__main__':
    students = []
    for _ in range(int(input())):
        name = input()
        score = float(input())
        students.append([name, score])

    grades = sorted(set(student[1] for student in students))
    second_lowest = grades[1] if len(grades) > 1 else grades[0]
    second_lowest_students = [student[0] for student in students if student[1] == second_lowest]
    second_lowest_students.sort()
    for name in second_lowest_students:
        print(name)

if __name__ == '__main__':
    n = int(input())
    student_marks = {}
    for _ in range(n):
        name, *line = input().split()
        scores = list(map(float, line))
        student_marks[name] = scores
    query_name = input()

    avg_marks = sum(student_marks[query_name]) / len(student_marks[query_name])
    print(f"{avg_marks:.2f}")

if __name__ == '__main__':
    n = int(input())
    arr = map(int, input().split())

    scores = list(arr)
    max_score = max(scores)
    filtered_scores = [score for score in scores if score != max_score]
    runner_up = max(filtered_scores)
    print(runner_up)