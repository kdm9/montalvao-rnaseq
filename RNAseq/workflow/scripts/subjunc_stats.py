#!/usr/bin/env python3
import re
import argparse
import json
from sys import stdout

from tqdm import tqdm

def parse_stats(logfile):
    res = {}
    with open(logfile) as fh:
        in_summary = False
        for line in fh:
            line = line.strip().strip("|").strip()
            if "Input file 1" in line:
                res["input_r1"] = line.split(":")[-1].strip()
            if "Input file 2" in line:
                res["input_r2"] = line.split(":")[-1].strip()
            if re.match(r"//=+ *Summary *=+\\", line):
                in_summary = True
                continue
            if in_summary and ":" in line:
                k, v = line.split(" : ")
                k = k.strip().replace(" ", "_").lower()
                v = v.strip().split(" ")[0].replace(",", "").strip()
                if "." in v:
                    res[k]=float(v)
                else:
                    res[k]=int(v)
    return res

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument(
            "-o", "--output", default=stdout, type=argparse.FileType("wt"),
            help="Output jsonl file")
    ap.add_argument(
            "logfiles", nargs="+",
            help="subread/subjunc log files")
    args = ap.parse_args(argv)

    for file in tqdm(args.logfiles, unit="files"):
        dat = parse_stats(file)
        dat["file"] = file
        json.dump(dat, args.output)
        args.output.write("\n")

if __name__ == "__main__":
    main()
