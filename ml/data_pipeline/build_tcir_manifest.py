"""CLI for converting TCIR metadata CSV into CycloneAI satellite JSONL."""

from __future__ import annotations

import argparse
from pathlib import Path

from ml.data_pipeline.tcir_adapter import load_tcir_metadata, write_manifest


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert TCIR metadata CSV to CycloneAI JSONL")
    parser.add_argument("metadata", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    frames = load_tcir_metadata(args.metadata)
    write_manifest(frames, args.output)
    print(f"frames={len(frames)} output={args.output}")


if __name__ == "__main__":
    main()
