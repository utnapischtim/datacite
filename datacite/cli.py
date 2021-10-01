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

# import typing as t
from os.path import isfile

import click

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


@click.group()
def datacite():
    """ "Datacite CLI."""


@datacite.command()
@click.option("--input-file-csv", required=True, type=CSV())
@click.option("--username", required=True, type=click.STRING)
@click.option("--password", required=True, type=click.STRING)
@click.option("--prefix", required=True, type=click.STRING)
@click.option("--test-mode/--production-mode", default=True, is_flag=True)
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
@click.option("--input-file-json", required=True, type=JSON())
@click.option("--username", required=True, type=click.STRING)
@click.option("--password", required=True, type=click.STRING)
@click.option("--prefix", required=True, type=click.STRING)
@click.option("--test-mode/--production-mode", default=True, is_flag=True)
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
