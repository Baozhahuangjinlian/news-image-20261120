"""Hand the finished front page over to the judging harness.

The newspaper image itself is built ahead of time and lives next to this
file as entry.png. All this script does is carry that file into the output
folder the harness points at, then prove the delivered copy is whole:
same size, a genuine PNG signature, and the expected 1024 by 1024 canvas.
"""

import os
import shutil
import struct
import sys
from pathlib import Path


# Every PNG file opens with these eight bytes.
PNG_OPENING = b"\x89PNG\r\n\x1a\n"

# The front page is rendered at this size, and we refuse anything else.
EXPECTED_SIDE = 1024

PICTURE_NAME = "entry.png"


def picture_beside_script() -> Path:
    """Point at the entry.png sitting in the same folder as this script."""
    here = Path(__file__).resolve().parent
    return here / PICTURE_NAME


def harness_folder() -> Path:
    """Where the harness wants the finished file.

    MAKEFUN_OUTPUT_DIR names the folder when the harness sets it;
    otherwise we fall back to the plain /output directory.
    """
    chosen = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    return Path(chosen)


def canvas_size(png_bytes: bytes) -> tuple[int, int]:
    """Pull width and height out of a PNG's IHDR chunk.

    Layout: 8 signature bytes, then a 4-byte length, the 4 letters IHDR,
    then width and height as 4-byte big-endian numbers.
    """
    if len(png_bytes) < 24:
        raise ValueError("file is too short to hold a PNG header")
    if png_bytes[:8] != PNG_OPENING:
        raise ValueError("file does not start with the PNG signature")
    if png_bytes[12:16] != b"IHDR":
        raise ValueError("first PNG chunk is not IHDR")
    wide, tall = struct.unpack(">II", png_bytes[16:24])
    return wide, tall


def check_delivered(original: Path, delivered: Path) -> None:
    """Confirm the delivered copy matches the source in every way we can."""
    source_bytes = original.read_bytes()
    delivered_bytes = delivered.read_bytes()
    if delivered_bytes[:8] != PNG_OPENING:
        raise ValueError("delivered copy does not open with the PNG signature")
    if len(delivered_bytes) != len(source_bytes):
        raise ValueError(
            f"delivered copy is {len(delivered_bytes)} bytes, "
            f"but the source is {len(source_bytes)} bytes"
        )
    if delivered_bytes != source_bytes:
        raise ValueError("delivered copy differs from the source byte for byte")
    wide, tall = canvas_size(delivered_bytes)
    if (wide, tall) != (EXPECTED_SIDE, EXPECTED_SIDE):
        raise ValueError(
            f"front page is {wide}x{tall}, expected "
            f"{EXPECTED_SIDE}x{EXPECTED_SIDE}"
        )


def run() -> int:
    """Copy entry.png into the harness folder and verify the result."""
    source = picture_beside_script()
    if not source.is_file():
        print(f"cannot find {PICTURE_NAME} next to this script", file=sys.stderr)
        return 1

    target_dir = harness_folder()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / PICTURE_NAME
    shutil.copyfile(source, target)

    try:
        check_delivered(source, target)
    except ValueError as problem:
        print(f"verification failed: {problem}", file=sys.stderr)
        return 1

    print(f"delivered {PICTURE_NAME} ({target.stat().st_size} bytes) to {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
