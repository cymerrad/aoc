#!/usr/bin/python3

fuel_sum = 0

def fuel_for_mass(mass):
    fuel = mass//3 - 2
    if fuel < 0:
        return 0
    return fuel


def true_fuel_for_mass(mass):
    if mass <= 0:
        return 0
    req = fuel_for_mass(mass)
    return req + true_fuel_for_mass(req)

with open("input1") as fr:
    for line in fr:
        fuel_sum += true_fuel_for_mass(int(line.strip()))


print(fuel_sum)

# tests
cases = [(14,2), (1969,966), (100756, 50346)]
for n, exp in cases:
    print(f"For {n} we got {true_fuel_for_mass(n)} and should be {exp}")
