import fileinput

data = [int(x) for x in fileinput.input()]


def first(data):
    for n in data:
        for m in data:
            if n + m == 2020:
                print(n, m, n * m)
                return


first(data)


def second(data):
    for n in data:
        for m in data:
            for k in data:
                if n + m + k == 2020:
                    print(n, m, k, n * m * k)


second(data)
