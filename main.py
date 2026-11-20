#!/usr/bin/env python3
"""Entry program for news-image-20261120: copy entry.png to the output dir.

Runs with no network, Python 3.13 stdlib only. Writes the same bytes on
every run: it copies the repository's entry.png to $MAKEFUN_OUTPUT_DIR
(or /output when unset).
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "entry.png")
OUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, "entry.png")
    shutil.copyfile(SRC, dst)
    # Sanity check: the copy must be byte-identical to the source.
    assert os.path.getsize(dst) == os.path.getsize(SRC), "copy size mismatch"


if __name__ == "__main__":
    main()
