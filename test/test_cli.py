from __future__ import annotations

from pathlib import Path

from sarif_to_annotations.cli import main
from test.conftest import load_expected_results


ASSETS_DIR = Path(__file__).parent / "assets"


def test_cli_prints_annotations(capsys) -> None:
    exit_code = main([str(ASSETS_DIR / "semgrep-failed-execution.json")])

    out = capsys.readouterr().out.strip().splitlines()

    assert exit_code == 0
    assert out == load_expected_results(
        "semgrep-failed-execution.expected-gh-output.txt"
    )
