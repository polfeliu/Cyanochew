from click.testing import CliRunner
from cyanobyte.validator import click_valdiate

# Press the green button in the gutter to run the script.
if __name__ == "__main__":
    runner = CliRunner()
    # Validate
    result = runner.invoke(click_valdiate, ["test/peripherals/example.yaml"])

    # Build
    """
    result = runner.invoke(gen, [
        "-t",
        "generic.c",
        "-o",
        ".build",
        "example.yaml"
    ])"""
