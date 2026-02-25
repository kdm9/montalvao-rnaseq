#!/usr/bin/env python3

from sys import stdout, argv
from pyarrow import json, csv


tbl = json.read_json(argv[1])
with open("/dev/stdout", "wb") as hf:
    csv.write_csv(tbl, hf)

