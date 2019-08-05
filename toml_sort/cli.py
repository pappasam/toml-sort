"""Toml Sort CLI"""

import click

from . import sort_toml


@click.command()
@click.argument("filename")
def cli(filename):
    """Simple command line interface, work in progress"""
    with open(filename, "r") as infile:
        toml_content = infile.read()
    click.echo(sort_toml(toml_content))
