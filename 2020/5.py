import sys

data = open(sys.argv[1]).read().strip().split("\n")

def first():
    seats = []
    for line in data:
        row = line[:7]
        col = line[7:]
        row_num = int(row.replace("F","0").replace("B","1"), 2)
        col_num = int(col.replace("L", "0").replace("R", "1"), 2)

        seat_id = row_num * 8 + col_num

        seats.append(seat_id)

    return seats, max(seats)


def second():
    seats, _ = first()
    seats.sort()

    for i in range(1,len(seats)):
        lo = seats[i-1]
        hi = seats[i]

        if hi - lo != 1:
            print(hi,lo,i)