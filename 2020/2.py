import re
import fileinput
from collections import Counter

data = [line for line in fileinput.input()]

line_re = re.compile(r"(\d+)-(\d+) (\w): (\w+)")

def is_valid(lo, hi, letter, passw):
    lo, hi = int(lo), int(hi)
    c = Counter(passw)
    return lo <= c[letter] <= hi

def is_valid_2(lo, hi, letter, passw):
    lo, hi = int(lo), int(hi)
    return (passw[lo-1] == letter) ^ (passw[hi-1] == letter)

counter = 0
counter_2 = 0
for line in data:
    match = line_re.findall(line)
    lo, hi, letter, passw = match[0]

    if is_valid(lo, hi, letter, passw):
        print(match)
        counter += 1

    if is_valid_2(lo, hi, letter, passw):
        print(match)
        counter_2 += 1


print(counter)
print(counter_2)

