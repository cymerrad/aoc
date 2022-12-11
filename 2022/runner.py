#!python3
import click
import shutil
import pathlib
import importlib
import yaml
from pprint import pprint


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
    pprint(ctx.obj)

    shutil.copytree(ctx.obj["ROOT"] / "0", ctx.obj["ROOT"] / module)


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=True))
def run(ctx, module):
    mod = importlib.import_module(module)
    input_file = ctx.obj["ROOT"] / module / "input.yaml"
    (input_raw,) = get_input(input_file)
    data = mod.parse(input_raw)
    result = mod.solve(data)

    print(f"Result: {result}")


@cli.command()
@click.pass_context
@click.argument("module", type=click.Path(exists=True))
def test(ctx, module):
    mod = importlib.import_module(module)
    input_file = ctx.obj["ROOT"] / module / "test.yaml"
    (input_raw, expected) = get_input(input_file)
    data = mod.parse(input_raw)
    result = mod.solve(data)

    if result == expected:
        print(f"{result} is correct")
    else:
        print(f"Expected: {expected}\nGot: {result} instead.")


def get_input(file):
    with open(file) as fr:
        res = list(yaml.safe_load_all(fr.read()))

        if len(res) == 1:
            return (res[0],)

        [expected_result, data] = res
        return (data, expected_result)


if __name__ == "__main__":
    cli(obj={})
