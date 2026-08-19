#!/usr/bin/env python
"""Line-ending-normalised SHA-256 for cross-platform stream verification.

Raw-byte hashing of CSVs is NOT portable: pandas writes the platform line
terminator, so a Windows-built stream (CRLF) and a Linux-built one (LF) differ
by exactly one byte per row while carrying identical content. Verifying the
instance against the laptop therefore requires hashing the CONTENT, with line
endings normalised to LF.
"""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path


def normalized_sha256(path, chunk=1 << 20) -> str:
    h = hashlib.sha256()
    tail_cr = False
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            if tail_cr:
                b = b"\r" + b
                tail_cr = False
            if b.endswith(b"\r"):
                b = b[:-1]
                tail_cr = True
            h.update(b.replace(b"\r\n", b"\n"))
    if tail_cr:
        h.update(b"\r")
    return h.hexdigest()


if __name__ == "__main__":
    for p in sorted(sys.argv[1:]):
        print(f"{normalized_sha256(p)}  {Path(p).name}")
