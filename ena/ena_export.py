#!/usr/bin/env python3
from pathlib import Path
import argparse
from dataclasses import dataclass
import csv
import hashlib
from sys import stdout, stderr
import shutil
import ftplib
import os
try:
    from tqdm.auto import tqdm
except ImportError:
    def tqdm(iter, *args, **kwargs):
        yield from iter

def upload_with_md5sum(ftp, path: Path, upname: str) -> str:
    with path.open("rb") as fh:
        hash = hashlib.file_digest(fh, "md5")
        ftp.storbinary(f"STOR {upname}", fh, callback=hash.update)
        return hash.hexdigest()
    
def fastq_export(ftp,  libname: str, r1path: Path, r2path: Path):
    r1 = f"{libname}_R1.fastq.gz"
    r1md5 = upload_with_md5sum(ftp, r1path, r1)
    r2 = f"{libname}_R2.fastq.gz"
    r2md5 = upload_with_md5sum(ftp, r2path, r2)
    return {
        "forward_file_name": r1,
        "forward_file_md5": r1md5,
        "reverse_file_name": r2,
        "reverse_file_md5": r2md5,
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

    args.outdir.mkdir(exist_ok=True)

    user = os.environ["WEBIN_USER"]
    passwd = os.environ["WEBIN_PASS"]

    with args.tsv.open() as fh, ftplib.FTP(host="webin2.ebi.ac.uk", user=user, passwd=passwd) as ftp:
        ftp.login()
        icsv = csv.DictReader(fh, dialect="excel-tab")
        ofields = list(set(icsv.fieldnames) | set(("forward_file_md5", "reverse_file_md5")))
        ocsv = csv.DictWriter(stdout, fieldnames=ofields, dialect="excel-tab")
        ocsv.writeheader()
        for rec in tqdm(icsv):
            fwd_file = args.basedir / rec["forward_file_name"] 
            rev_file = args.basedir / rec["reverse_file_name"] 
            rec.update(fastq_export(ftp, rec["library_name"], fwd_file, rev_file))
            ocsv.writerow(rec)
            stdout.flush()

if __name__ == "__main__":
    main()
