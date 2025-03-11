from collections import defaultdict

n, m = map(int, input().split())

group_A = defaultdict(list)

for i in range(1, n + 1):
    word = input().strip()
    group_A[word].append(str(i))

for _ in range(m):
    word = input().strip()
    if word in group_A:
        print(" ".join(group_A[word]))
    else:
        print(-1)