import traceback
import sys
import unittest
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


class ChillError(Exception):
    pass


class Intcode(Thread):
    '''Creates a 2019 AoC Intcode machine, initialized with a program.
    Program can be either a list of ints or a string.'''

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
        self.status = "Operational."

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

        self._done = Queue(1)
        self._done.put(True)
        self.start()

    def run(self):
        "Thread overload."
        self._done.get()

        self.running = True
        self._run()

        self._done.task_done()

    def put(self, *inputs):
        "Pipe in inputs into the machine."
        if len(inputs) == 1 and type(inputs[0]) == list:
            # can pass in list
            [self.nonstdin.put(int(n)) for n in inputs[0]]
        else:
            # or a lot of nums
            [self.nonstdin.put(int(n)) for n in inputs]

    def get(self):
        "Read outputs from machine. Blocking."
        return self.nonstdout.get()

    def wait_for_result(self):
        '''Function returns when the machine stops.
        Returns what's gathered in the output pipe.'''
        self._done.join()

        result = []
        try:
            while True:
                result.append(self.nonstdout.get(block=False))
        except:
            Empty

        return result

    def _read_params(self, val: int):
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
            raise ChillError(f"Invalid code encountered at {self.ip}")

    def _op_at_ip(self):
        pre_op = self._read_at(self.ip)
        op_code, params = self._read_params(pre_op)
        return op_code, params

    def _put_char(self, ch):
        "Writes thingy on \"stdout\""
        self.nonstdout.put(ch)

    def _get_char(self):
        "Read thingy from \"stdin\". Blocking."
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

    def _progress(self, op_argc):
        if not self.ip_dirty:
            self.ip += op_argc + 1
        self.ip_dirty = False

    def _run(self):
        try:
            while self.running:
                op_code, params = self._op_at_ip()
                op_fun, op_name, op_argc, op_ptrs = self._get_op_with_code(
                    op_code)
                mem_slice = self.memory[self.ip+1:self.ip+op_argc+1]
                ptrs_start = op_argc-op_ptrs
                arguments = mem_slice[:ptrs_start]
                pointers = mem_slice[ptrs_start:]
                args_deref = self._deref(arguments, params)
                ptrs_deref = self._deref(pointers, params[ptrs_start:], True)
                op_fun(*args_deref, *ptrs_deref)

                self._progress(op_argc)

        except ChillError as e:
            self._end(e)
        except AssertionError as e:
            self._end(e)
        except Exception as e:
            try:
                _, _, trace = sys.exc_info()
                self._end(f"Unexpected error at line {trace.tb_lineno} : {e}")
            except Exception:
                self._end("You goofed up, mate.")
                print(traceback.format_exc())

    def _end(self, msg=None):
        self.running = False
        self.status = "Finished."
        if msg:
            self.status = msg


class _test_intcode(unittest.TestCase):
    def prog_test(self, input_prog, expected=[], input_data=[]):
        machine = Intcode(input_prog)
        machine.put(input_data)
        result = machine.wait_for_result()
        self.assertSequenceEqual(
            result, expected, f"Possible error: {machine.status}")

    def test_1(self):
        self.prog_test(
            "99",
            [], []
        )

    def test_2(self):
        self.prog_test(
            "3,9,8,9,10,9,4,9,99,-1,8",
            [1], [8]
        )  # eq8

    def test_3(self):
        self.prog_test(
            "3,9,7,9,10,9,4,9,99,-1,8",
            [1], [7]
        )  # lt8

    def test_4(self):
        self.prog_test(
            "3,3,1108,-1,8,3,4,3,99",
            [1], [8]
        )  # eq8

    def test_5(self):
        self.prog_test(
            "3,3,1107,-1,8,3,4,3,99",
            [1], [7]
        )  # lt8

    def test_6(self):
        self.prog_test(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9",
            [1], [1]
        )

    def test_7(self):
        self.prog_test(
            "3,12,6,12,15,1,13,14,13,4,13,99,-1,0,1,9",
            [0], [0]
        )

    def test_8(self):
        self.prog_test(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1",
            [1], [1]
        )

    def test_9(self):
        self.prog_test(
            "3,3,1105,-1,9,1101,0,0,12,4,12,99,1",
            [0], [0]
        )

    def test_10(self):
        test_data = "109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99"
        self.prog_test(test_data, Intcode.parse_program(test_data))

    def test_11(self):
        self.prog_test("1102,34915192,34915192,7,4,7,99,0", [1219070632396864])

    def test_12(self):
        test_data_2 = "104,1125899906842624,99"
        self.prog_test(test_data_2, [int(test_data_2.split(",")[1])])


class _test_memory(unittest.TestCase):
    def setUp(self):
        self.test_mem = Memory([1, 2, 3])

    def test_reads(self):
        self.assertEqual(self.test_mem[2], 3)
        self.assertEqual(self.test_mem[3], 0)
        self.assertSequenceEqual(self.test_mem[:5], [1, 2, 3, 0, 0])
        self.assertSequenceEqual(self.test_mem[0:2], [1, 2])

    def test_writes(self):
        self.test_mem[2**64] = 42
        self.assertEqual(len(self.test_mem), 3)  # sucks but yeah
        self.assertEqual(self.test_mem[2**64], 42)


def _run_test_class(test_case):
    case = unittest.TestLoader().loadTestsFromTestCase(test_case)
    result = unittest.TestResult()
    case(result)
    if result.wasSuccessful():
        return True
    else:
        print("Some tests failed!")
        for test, err in result.failures + result.errors:
            print(test)
            print(err)
        return False


def test_module():
    _run_test_class(_test_intcode)
    _run_test_class(_test_memory)
