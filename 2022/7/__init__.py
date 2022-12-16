from typing import *
from lark import Lark, Transformer
from pprint import pformat, pprint
import pathlib


def parse(input: str, *args, **kwargs):
    return [x.split() for x in input.strip().split("\n")]


class FakeFS:
    def __init__(self):
        self.head = {}
        self.fs = {"/": self.head}
        self.cwd = pathlib.Path("/")

    def cd(self, dir: str):
        new_dir = (self.cwd / dir).resolve()
        self.head = self.fs
        for part in new_dir.parts:
            self.head = self.head[part]

        self.cwd = new_dir
        return self.head

    def mkdir(self, dir):
        self.head[dir] = {}

    def file(self, file, size):
        self.head[file] = size

    def sizes(self):
        accum = []

        def size(p, f):
            if type(f) == dict:
                total = 0
                for path, content in f.items():
                    total += size(p / path, content)
                accum.append((p, total, "d"))
                return total
            else:
                accum.append((p, f, "f"))
                return f

        size(pathlib.Path("/"), self.fs)

        return set(accum)

    def load_data(self, data):
        try:
            for line in data:
                if line[0] == "$":
                    # input
                    if line[1] == "cd":
                        arg = line[2]
                        self.cd(arg)

                    elif line[1] == "ls":
                        # expect output next
                        pass
                else:
                    if line[0] == "dir":
                        # mkdir
                        self.mkdir(line[1])
                    else:
                        self.file(line[1], int(line[0]))
        except IndexError as e:
            print(f"Line: {line}")
            raise e

    def __repr__(self):
        return pformat(self.fs, indent=2, sort_dicts=True)


def solve_1(data, *args, debug=False, test=False, **kwargs) -> int:
    fs = FakeFS()
    fs.load_data(data)

    sizes = fs.sizes()

    total = 0
    DIR_SIZE_LIMIT = 100000
    for (path, size, type_) in sizes:
        if type_ == "d" and size <= DIR_SIZE_LIMIT:
            total += size

    return total


def solve_2(data, *args, debug=False, test=False, **kwargs) -> int:
    fs = FakeFS()
    fs.load_data(data)
    sizes = fs.sizes()

    DISK_SIZE = 70000000
    SIZE_NEEDED = 30000000

    root = next(x for x in sizes if x[0] == pathlib.Path("/"))
    disk_used = root[1]
    FREE_SPACE = DISK_SIZE - disk_used
    GAINS_NEEDED = SIZE_NEEDED - FREE_SPACE

    print(f"{disk_used=}")
    print(f"{FREE_SPACE=}")
    print(f"{GAINS_NEEDED=}")

    options_to_delete = sorted((x for x in sizes if x[2] == "d"), key=lambda x: x[1])

    chyba_to = next(x for x in options_to_delete if GAINS_NEEDED - x[1] <= 0)
    print(f"{chyba_to=}")
    return chyba_to[1]

    # print(options_to_delete)

    # net_size_gains = [(GAINS_NEEDED - x[1], x) for x in options_to_delete]

    # print(net_size_gains)

    # return min((x for x in net_size_gains if x[0] >= 0), key=lambda y: y[0])[1][1]


def test(*args, debug=False, test=False, **kwargs):
    fs = FakeFS()

    fs.file("boot", 1337)
    fs.mkdir("home")
    fs.cd("home")
    fs.mkdir("rado")
    fs.cd("rado")
    fs.file("hello.png", 69)
    # print(fs.sizes())


TEST_INPUT = """
$ cd /
$ ls
dir a
14848514 b.txt
8504156 c.dat
dir d
$ cd a
$ ls
dir e
29116 f
2557 g
62596 h.lst
$ cd e
$ ls
584 i
$ cd ..
$ cd ..
$ cd d
$ ls
4060174 j
8033020 d.log
5626152 d.ext
7214296 k
"""

TEST_RESULT_1 = 95437
TEST_RESULT_2 = 24933642
