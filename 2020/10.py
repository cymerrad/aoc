from itertools import groupby

data = open("input10").read().strip().split()
data = [int(x) for x in data]

adapters = sorted(data)
# adapters = [0] + adapters + [adapters[-1]]
diffs = [hi-lo for lo,hi in zip([0] + adapters, adapters + [adapters[-1] + 3])]

c1=len(list(filter(lambda x: x == 1, diffs)))
c3=len(list(filter(lambda x: x == 3, diffs)))
print(f"{c1=} {c3=} {c1*c3}")

groups = [(k,list(g)) for k,g in groupby(diffs)]

weights = {1: 1, 2: 2, 3: 4, 4: 7}
product = 1
for val, g in groups:
    if val == 1:
        l = len(g)
        product *= weights[l]

print(f"{product=}")
