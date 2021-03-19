from cyanobyte.codegen import gen
from cyanobyte.validator import click_valdiate

from click.testing import CliRunner

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    runner = CliRunner()
    # Validate
    result = runner.invoke(click_valdiate, [
        "test/peripherals/example.yaml"
    ])


    # Build
    '''
    result = runner.invoke(gen, [
        "-t",
        "generic.c",
        "-o",
        ".build",
        "example.yaml"
    ])'''
