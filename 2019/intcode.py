from collections import UserList
from queue import Queue, Empty
from threading import Thread

class Memory(UserList):
    def __init__(self, iterable):
        self.extra_items = {}
        return UserList.__init__(self, iterable)

    def __getitem__(self, i, *args, **kwargs):
        length = len(self)
        if type(i) == int and i >= length:
            try:
                return self.extra_items[i]
            except KeyError:
                return 0
        elif type(i) == slice and i.stop and i.stop >= length:
            the_rest = i.indices(i.stop - length)
            return UserList.__getitem__(self, slice(i.start, length, i.step), *args, **kwargs) + [0 for _ in range(*the_rest)]
        else:
            # slice(1, 2, None)
            return UserList.__getitem__(self, i, *args, **kwargs)

    def __setitem__(self, *args, **kwargs):
        if args[0] >= len(self):
            self.extra_items[args[0]] = args[1]
            return
        return UserList.__setitem__(self, *args, **kwargs)


_test_mem = Memory([1, 2, 3])
assert _test_mem[2] == 3
assert _test_mem[3] == 0
_test_mem[2**64] = 42
assert len(_test_mem) == 3  # sucks but yeah
assert _test_mem[2**64] == 42
assert _test_mem[:5] == [1, 2, 3, 0, 0]
assert _test_mem[0:2] == [1, 2]


class Intcode(Thread):
    @staticmethod
    def parse_program(program: str):
        return [int(x) for x in program.split(",")]

    def __init__(self, program):
        super().__init__()
        self.daemon = True

        self.memory = []
        self.nonstdin = Queue()
        self.nonstdout = Queue()

        if type(program) == str:
            self.memory = Memory(Intcode.parse_program(program))
        elif type(program) == list:
            assert all((type(x) == int for x in program)), "Invalid program"
            self.memory = Memory(program)
        else:
            raise Exception("Dunno how to handle that.")

        self.ip = 0  # instruction base
        self.ip_dirty = False  # did we jump?
        self.rb = 0  # relative base
        self.running = False

        self.ops = {
            1: (lambda a, b, r: self._save_at(a + b, r), "add", 3, 1),
            2: (lambda a, b, r: self._save_at(a * b, r), "mul", 3, 1),
            3: (lambda r: self._save_at(self._get_char(), r), "read", 1, 1),
            4: (lambda a: self._put_char(a), "write", 1, 0),
            5: (lambda a, b: self._modify_ip(b) if a != 0 else None, "jmp-t", 2, 0),
            6: (lambda a, b: self._modify_ip(b) if a == 0 else None, "jmp-f", 2, 0),
            7: (lambda a, b, r: self._save_at(1, r) if a < b else self._save_at(0, r), "lt", 3, 1),
            8: (lambda a, b, r: self._save_at(1, r) if a == b else self._save_at(0, r), "eq", 3, 1),
            9: (lambda a: self._modify_rb(a), "rb-off", 1, 0),
            99: (lambda: self._end(), "eof", 0, 0),
        }

        self.done = Queue(1)
        self.done.put(True)
        self.start()

    def run(self):
        self.done.get()

        self.running = True
        self._run()
        self.running = False

        self.done.task_done()

    def put(self, *inputs):
        if len(inputs) == 1 and type(inputs[0]) == list:
            # can pass in list
            [self.nonstdin.put(n) for n in inputs[0] if type(n) == int]
        else:
            # or a lot of nums
            [self.nonstdin.put(n) for n in inputs if type(n) == int]

    def get(self):
        return self.nonstdout.get()

    def wait_for_result(self):
        self.done.join()

        result = []
        try:
            while True:
                result.append(self.nonstdout.get(block=False))
        except:
            Empty

        return result


    def _read_code(self, ip: int):
        val = self.memory[ip]
        if val < 100:
            return (val, (0, 0, 0))
        full = "{:05d}".format(val)
        op_c = int(full[3:])
        op_pars = list(full[:3])
        op_pars.reverse()
        return (op_c, tuple([int(x) for x in op_pars]))

    def _get_op_with_code(self, code: int):
        try:
            return self.ops[code]
        except KeyError:
            if code == 99:
                raise ProgramEnd
            else:
                raise

    def _put_char(self, ch):
        self.nonstdout.put(ch)

    def _get_char(self, ):
        "Blocking"
        return self.nonstdin.get()

    def _save_at(self, val, r):
        assert r >= 0, "Invalid memory access."
        self.memory[r] = val

    def _read_at(self, r):
        assert r >= 0, "Invalid memory access."
        return self.memory[r]

    def _deref_param(self, val, param, ptr=False):
        if param == 0:
            # position mode
            if ptr:
                return val
            return self._read_at(val)
        elif param == 1:
            # immediate mode
            # "Parameters that an instruction writes to will never be in immediate mode."
            return val
        elif param == 2:
            # relative mode
            if ptr:
                return self.rb+val
            return self._read_at(self.rb+val)
        else:
            raise Exception("Unknown parameter mode.")

    def _deref(self, mem_slice: list, params: tuple, ptr=False):
        return [self._deref_param(v, p, ptr) for v, p in zip(mem_slice, params)]

    def _modify_ip(self, ip_jmp):
        self.ip = ip_jmp
        self.ip_dirty = True

    def _modify_rb(self, rb_change):
        self.rb += rb_change

    def _run(self):
        while self.ip < len(self.memory) and self.running:
            pre_op = self._read_at(self.ip)
            op_code, params = self._read_code(
                self.ip)  # TODO: explicit self.ip
            op_fun, op_name, op_argc, op_ptrs = self._get_op_with_code(op_code)
            mem_slice = self.memory[self.ip+1:self.ip+op_argc+1]
            ptrs_start = op_argc-op_ptrs
            arguments = mem_slice[:ptrs_start]
            pointers = mem_slice[ptrs_start:]
            args_deref = self._deref(arguments, params)
            ptrs_deref = self._deref(pointers, params[ptrs_start:], True)
            op_fun(*args_deref, *ptrs_deref)

            if not self.ip_dirty:
                self.ip += op_argc + 1
            self.ip_dirty = False

    def _end(self):
        self.running = False


def prog_test(input_prog, input_data=[], expected=[]):
    machine = Intcode(input_prog)
    machine.put(input_data)
    result = machine.wait_for_result()
    assert result == expected, f"Got {result}; expected {expected}"

# TODO: make a test suite

# prog_test("3,9,8,9,10,9,4,9,99,-1,8", [8], [1])  # eq8
# prog_test("3,9,7,9,10,9,4,9,99,-1,8", [7], [1])  # lt8
# prog_test("3,3,1108,-1,8,3,4,3,99", [8], [1])  # eq8
# prog_test("3,3,1107,-1,8,3,4,3,99", [7], [1])  # lt8
# prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [1], [1])
# prog_test("3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9", [0], [0])
# prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [1], [1])
# prog_test("3,3,1105,-1,9,1101,0,0,12,4,12,99,1", [0], [0])

# test_data = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
# prog_test(test_data, [], Intcode.parse_program(test_data))

# prog_test("1102,34915192,34915192,7,4,7,99,0", [], [1219070632396864])

# test_data_2 = "104,1125899906842624,99"
# prog_test(test_data_2, [], [int(test_data_2.split(",")[1])])
