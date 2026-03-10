#!/usr/bin/env python3
from pathlib import Path
import argparse
from dataclasses import dataclass
import csv
import hashlib
from sys import stdout, stderr
import shutil
try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iter, *args, **kwargs):
        yield from iter

def md5sum(path: Path):
    with path.open("rb") as fh:
        hash = hashlib.file_digest(fh, "md5")
        return hash.hexdigest()
    
def fastq_export(outdir: Path, libname: str, r1path: Path, r2path: Path):
    r1out = outdir/f"{libname}_R1.fastq.gz"
    shutil.copyfile(r1path, r1out)
    r2out = outdir/f"{libname}_R2.fastq.gz"
    shutil.copyfile(r2path, r2out)
    
    return {
        "forward_file_name": r1out.name,
        "forward_file_md5": md5sum(r1out),
        "reverse_file_name": r2out.name,
        "reverse_file_md5": md5sum(r2out),
    }


def main(argv=None):
    ap=argparse.ArgumentParser("ena_export")
    ap.add_argument("--outdir", "-o", type=Path, default=Path("ena"),
                    help="Output directory")
    ap.add_argument("--tsv", "-t", type=Path, required=True,
                    help="Table for ENA")
    ap.add_argument("--basedir", "-i", type=Path, required=True,
                    help="Basename for all inputs")
    args = ap.parse_args(argv)

    with args.tsv.open() as fh:
        icsv = csv.DictReader(fh, dialect="excel-tab")
        ofields = list(set(icsv.fieldnames) | set("forward_file_md5", "reverse_file_md5"))
        print(ofields, file=stderr)
        ocsv = csv.DictWriter(stdout, fieldnames=ofields, dialect="excel-tab")
        ocsv.writeheader()
        for rec in tqdm(icsv):
            fwd_file = args.basedir / rec["forward_file_name"] 
            rev_file = args.basedir / rec["reverse_file_name"] 
            rec.update(fastq_export(args.outdir, rec["library_name"], fwd_file, rev_file))
            ocsv.writerow(rec)
