#!/usr/bin/env python3
"""
Lightweight script to to create multiple copies of each file in the source directory
and place them in the destination.
"""

import os
import shutil
import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--source",
        type=Path,
        default=os.getenv("SOURCE_DIR", "./source"),
        help="Source directory of the files."
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=os.getenv("DESTINATION_DIR", "./output"),
        help="Destination directory for file copies."
    )
    parser.add_argument(
        "--copies",
        type=int,
        default=int(os.getenv("NUM_COPIES", "10")),
        help="Number of copies to generate."
    )

    return parser.parse_args()

def main():
    args = parse_args()

    source_path = args.source.resolve()
    destination_path = args.dest.resolve()
    num_copies = args.copies

    destination_path.mkdir(parents=True, exist_ok=True)

    if not source_path.exists():
        print(f"Source directory does not exist: {source_path}")
        return

    for file_path in source_path.iterdir():
        if file_path.is_file() and not file_path.name.startswith('.'):
            for i in range(1, num_copies + 1):
                new_filename = f"{file_path.stem}_{i}{file_path.suffix}"
                target_file = destination_path / new_filename
                shutil.copy2(file_path, target_file)

    print(f"Done creating {num_copies} copies of each file.")

if __name__ == "__main__":
    main()