# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2021 Graz University of Technology.
#
# DataCite is free software; you can redistribute it and/or modify it
# under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""CLI wrapper for the DataCite Rest API."""

import csv
import json
import sys
from importlib import import_module

# import typing as t
from os.path import isfile

import click
from jsonschema import ValidationError

from .rest_client import DataCiteRESTClient


class JSON(click.ParamType):
    """JSON provides the ability to load a json from a string or a file."""

    name = "JSON"

    def convert(self, value, param, ctx):
        """This method converts the json-file to the dictionary representation."""
        if not isfile(value):
            click.secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        try:
            with open(value, "r") as fp:
                obj = json.load(fp)
            return obj
        except json.JSONDecodeError as e:
            click.secho("ERROR - Invalid JSON provided.", fg="red")
            click.secho(f"  error: {e.args[0]}", fg="red")
            sys.exit()


class CSV(click.ParamType):
    """CSV provides the ability to load a csv from a file."""

    name = "CSV"

    def convert(self, value, param, ctx) -> csv.DictReader:
        """This method opens the files as a DictReader object."""
        if not isfile(value):
            click.secho("ERROR - please look up if the file path is correct.", fg="red")
            sys.exit()

        csv_file = open(value)
        reader = csv.DictReader(csv_file)

        return reader


option_input_file_csv = click.option("--input-file-csv", required=True, type=CSV())
option_input_file_json = click.option("--input-file-json", required=True, type=JSON())
option_username = click.option("--username", type=click.STRING, default="")
option_password = click.option("--password", type=click.STRING, default="")
option_prefix = click.option("--prefix", type=click.STRING, default="")
option_mode = click.option("--test-mode/--production-mode", default=True, is_flag=True)
option_schema_version = click.option(
    "--schema-version", type=click.Choice(["3.1", "4.0", "4.1", "4.2", "4.3"])
)


@click.group()
def datacite():
    """ "Datacite CLI."""


@datacite.command()
@option_input_file_csv
@option_username
@option_password
@option_prefix
@option_mode
def update_urls(input_file_csv: csv.DictReader, **kwargs):
    d = DataCiteRESTClient(
        username=kwargs["username"],
        password=kwargs["password"],
        test_mode=kwargs["test_mode"],
        prefix=kwargs["prefix"],
    )

    for row in input_file_csv:
        d.update_url(row["doi"], row["url"])

    click.secho("successfully updated all urls", fg="green")


@datacite.command()
@option_input_file_json
@option_username
@option_password
@option_prefix
@option_mode
def public_dois(input_file_json: dict, **kwargs):
    d = DataCiteRESTClient(
        username=kwargs["username"],
        password=kwargs["password"],
        test_mode=kwargs["test_mode"],
        prefix=kwargs["prefix"],
    )

    with click.progressbar(input_file_json) as list_of_records:
        for record in list_of_records:
            d.public_doi(**record)


@datacite.command()
@option_input_file_json
@option_schema_version
def validate(input_file_json: dict, schema_version: str = "4.3"):
    module = f".schema{schema_version.replace('.', '')}"
    schema = import_module(module, package="datacite")

    for record in input_file_json:
        try:
            schema.validator.validate(record["metadata"])
        except ValidationError as e:
            print(e.args[0])
