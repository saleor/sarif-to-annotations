from __future__ import annotations

import argparse
from pathlib import Path

from sarif_to_annotations.converter import sarif_to_github_annotations
from sarif_to_annotations.models import SarifFile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sarif-to-annotations",
        description="Convert SARIF to GitHub workflow annotation commands.",
    )
    parser.add_argument("sarif_path", type=Path, help="Path to SARIF JSON file")
    args = parser.parse_args(argv)

    sarif = SarifFile.model_validate_json(args.sarif_path.read_text(encoding="utf-8"))

    for command in sarif_to_github_annotations(sarif):
        print(command)

    return 0
