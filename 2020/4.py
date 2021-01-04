from dataclasses import dataclass
from typing import *
import sys
import re

data = open(sys.argv[1]).read()

id_re = re.compile(
    r"""(?mx)
(?:
    byr:(?P<byr>\S+)| # (Birth Year)
    iyr:(?P<iyr>\S+)| # (Issue Year)
    eyr:(?P<eyr>\S+)| # (Expiration Year)
    hgt:(?P<hgt>\S+)| # (Height)
    hcl:(?P<hcl>\S+)| # (Hair Color)
    ecl:(?P<ecl>\S+)| # (Eye Color)
    pid:(?P<pid>\S+)| # (Passport ID)
    cid:(?P<cid>\S+)  # (Country ID)
)
"""
)


@dataclass
class ID:
    byr: str
    iyr: str
    eyr: str
    hgt: str
    hcl: str
    ecl: str
    pid: str
    cid: str = None

    def validate(self):
        # byr (Birth Year) - four digits; at least 1920 and at most 2002.
        # iyr (Issue Year) - four digits; at least 2010 and at most 2020.
        # eyr (Expiration Year) - four digits; at least 2020 and at most 2030.
        # hgt (Height) - a number followed by either cm or in:
        #     If cm, the number must be at least 150 and at most 193.
        #     If in, the number must be at least 59 and at most 76.
        # hcl (Hair Color) - a # followed by exactly six characters 0-9 or a-f.
        # ecl (Eye Color) - exactly one of: amb blu brn gry grn hzl oth.
        # pid (Passport ID) - a nine-digit number, including leading zeroes.
        # cid (Country ID) - ignored, missing or not.

        self.byr = int(self.byr)
        assert 1920 <= self.byr <= 2002

        self.iyr = int(self.iyr)
        assert 2010 <= self.iyr <= 2020

        self.eyr = int(self.eyr)
        assert 2020 <= self.eyr <= 2030

        m = re.fullmatch(r"(\d+)(cm|in)", self.hgt)
        assert m is not None
        num, units = m.groups()
        if units == "cm":
            assert 150 <= int(num) <= 193
        elif units == "in":
            assert 59 <= int(num) <= 76

        assert re.fullmatch(r"#[\da-f]{6}", self.hcl)

        assert re.fullmatch(r"amb|blu|brn|gry|grn|hzl|oth", self.ecl)

        assert re.fullmatch(r"\d{9}", self.pid)



def parse_id(text: str) -> ID:
    struct = {}
    fields_no = 0
    for match in id_re.finditer(text):
        term, value = [(t, v) for t, v in match.groupdict().items() if v][0]
        if struct.get(term, False):
            assert False, "Duplicated entry"
        else:
            struct[term] = value
            if term != "cid":
                fields_no += 1

    assert fields_no >= 7, "Not enough fields found"

    return ID(**struct)


def parse(text: str) -> List[ID]:
    parts = text.split("\n\n")
    valid = []
    for part in parts:
        try:
            parsed = parse_id(part)
            valid.append(parsed)
        except AssertionError:
            continue

    print(f"Valid {len(valid)} out of {len(parts)}")
    return valid

def first():
    parse(data)

def second():
    valid = []
    invalid = []
    parsed = parse(data)
    for p in parsed:
        try:
            p.validate()
            valid.append(p)
        except AssertionError:
            invalid.append(p)
            continue

    print(f"Valid {len(valid)} out of {len(parsed)}")
    return valid, invalid