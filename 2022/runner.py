#!python3
import click
import shutil
import pathlib
import importlib
import importlib.resources
import yaml
import subprocess
from pprint import pprint
from termcolor import colored
from typing import *


@click.group()
@click.option("--debug/--no-debug", default=False)
@click.pass_context
def cli(ctx, debug):
    # ensure that ctx.obj exists and is a dict (in case `cli()` is called
    # by means other than the `if` block below)
    ctx.ensure_object(dict)
    ctx.obj["DEBUG"] = debug

    this_file = pathlib.Path(__file__)
    ctx.obj["ROOT"] = this_file.parent


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=False))
def new(ctx, module):
    # pprint(ctx.obj)

    src = ctx.obj["ROOT"] / "0"
    dest: pathlib.Path = ctx.obj["ROOT"] / module
    shutil.copytree(src, dest)

    for file in dest.iterdir():
        subprocess.run(["code", "-r", file])


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=True))
@click.option("-t", "--test", default=False, is_flag=True)
@click.option("-n", "--no-test", default=False, is_flag=True)
def run(ctx, module, test, no_test):
    debug = ctx.obj["DEBUG"]
    mod = get_module(module)

    if test:
        print(colored("Running test suite", "yellow"))
        if mod.test(debug=debug):
            print(colored("Success", "green"))
        else:
            print(colored("Fail", "red"))

    parsed_test_data = mod.parse(mod.TEST_INPUT, debug=debug)

    if debug:
        print("TEST_INPUT\n", mod.TEST_INPUT)
        print("\nPARSED\n", parsed_test_data)

    test_result_1 = mod.solve_1(parsed_test_data, debug=debug, test=True)
    success_1 = test_result_1 == mod.TEST_RESULT_1
    if not success_1 and not no_test:
        print(colored("First test failed", "red"))
        return
    print(colored("First test correct", "green"))

    parsed = mod.parse(mod.INPUT, debug=debug)

    if debug:
        print(parsed)

    result_1 = mod.solve_1(parsed, debug=debug)
    print(f"First:\t" + colored(result_1, "yellow"))

    test_result_2 = mod.solve_2(parsed_test_data, debug=debug, test=True)
    success_2 = test_result_2 == mod.TEST_RESULT_2
    if not success_2 and not no_test:
        print(colored("Second test failed", "red"))
        return
    print(colored("Second test correct", "green"))

    result_2 = mod.solve_2(parsed, debug=debug)
    print(f"Second:\t" + colored(result_2, "yellow"))


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=True))
def solve_1(ctx, module):
    mod = importlib.import_module(module)
    input_file = ctx.obj["ROOT"] / module / "input.yaml"
    (input_raw,) = get_input(input_file)
    data = mod.parse(input_raw)

    result_1 = mod.solve_1(data, debug=ctx.obj["DEBUG"])

    print(colored("Results", "yellow"))
    print(f"First:\t{result_1}")

    try:
        result_2 = mod.solve_2(data, debug=ctx.obj["DEBUG"])
        print(f"Second:\t{result_2}")
    except NotImplementedError:
        pass


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=True))
def test(ctx, module):
    mod = importlib.import_module(module)
    input_file = ctx.obj["ROOT"] / module / "test.yaml"
    input_tuple = get_input(input_file)

    expected_1, expected_2 = None, None
    (input_data, expected_1, expected_2) = input_tuple

    data = mod.parse(input_data, debug=ctx.obj["DEBUG"])

    if ctx.obj["DEBUG"]:
        print("\nRaw input:")
        pprint(input_tuple)

        print("\nParsed data:")
        pprint(data)

    result_1 = mod.solve_1(data, debug=ctx.obj["DEBUG"])
    if result_1 == expected_1:
        print(colored("First part correct", "green"))
        # print(f"{result_1} is correct")
    else:
        print(colored("First part wrong", "red"))
        print(f"Expected: {expected_1}\nGot: {result_1} instead.")

    if expected_2 is None:
        return

    result_2 = mod.solve_2(data, debug=ctx.obj["DEBUG"])
    if result_2 == expected_2:
        print(colored("Second part correct", "green"))
        # print(f"{result_2} is correct")
    else:
        print(colored("Second part wrong", "red"))
        print(f"Expected: {expected_2}\nGot: {result_2} instead.")


def get_input(file):
    with open(file) as fr:
        res = list(yaml.safe_load_all(fr.read()))

        if len(res) == 1:
            return (res[0],)

        if len(res) == 2:
            return (res[1], res[0], None)

        if len(res) == 3:
            return (res[2], res[0], res[1])


def get_module(module):
    mod = importlib.import_module(module)

    resources = list(
        resource
        for resource in importlib.resources.files(module).iterdir()
        if resource.is_file()
    )

    input_file = next(r.read_text() for r in resources if r.name.startswith("input"))
    # test_file = next((r.read_text() for r in resources if r.name.startswith("test")), None)

    # class Mod:
    #     parse: Callable = mod.parse
    #     solve_1: Callable = mod.solve_1
    #     solve_2: Callable = mod.solve_2
    #     INPUT: str = input_file
    #     TEST_INPUT: str = mod.TEST_INPUT
    #     TEST_RESULT_1: str = mod.TEST_RESULT_1
    #     TEST_RESULT_2: str = mod.TEST_RESULT_2

    setattr(mod, "INPUT", input_file)

    return mod


if __name__ == "__main__":
    cli(obj={})
