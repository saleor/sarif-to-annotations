import pytest
from pathlib import Path

from sarif_to_annotations.converter import sarif_to_github_annotations
from sarif_to_annotations.models import SarifFile
from test.conftest import load_expected_results, load_sarif

ASSETS_DIR = Path(__file__).parent / "assets"


@pytest.mark.parametrize(
    ("_case", "sarif_input", "expected_results"),
    [
        (
            "When Semgrep finds nothing -> should output nothing",
            load_sarif("semgrep-no-results.json"),
            [],
        ),
        (
            "When Semgrep finds results -> should print them",
            load_sarif("semgrep-results-found.json"),
            load_expected_results("semgrep-results-found.expected-gh-output.txt"),
        ),
        (
            "When Semgrep Crashes -> should print it",
            load_sarif("semgrep-failed-execution.json"),
            load_expected_results("semgrep-failed-execution.expected-gh-output.txt"),
        ),
    ],
)
def test_converts_semgrep_results_to_error_annotations(
    _case: str, sarif_input: SarifFile, expected_results: list[str]
) -> None:
    commands = sarif_to_github_annotations(sarif_input)
    assert commands == expected_results


@pytest.mark.parametrize(
    ("user_input", "expected_output"),
    [
        # HTML should be escaped
        ("<details>", "::error::%3Cdetails%3E"),
        # GH commands should be escaped
        (
            "::error file=app.js,line=1::Missing semicolon",
            "::error::%3A%3Aerror file=app.js%2Cline=1%3A%3AMissing semicolon",
        ),
        (
            "::stop-commands::danger",
            "::error::%3A%3Astop-commands%3A%3Adanger",
        ),
        # C0 control characters should be removed entirely
        ("NUL '\x00'", "::error::NUL ''"),
        ("'\r or \n'", "::error::' or '"),
        ("\\", "::error::"),
        ("%20", "::error::%2520"),
        # C0 0x1F (31)
        ("\x1f", "::error::"),
        ("\x7f", "::error::"),  # C0 0x7F (127) - the last control character in C1
        # C1 control characters should also be removed
        ("\x80", "::error::"),  # C1 0x80 (128) - the 1st control character in C1
        ("\x9f", "::error::"),  # C1 0x9F (159) - the last control character in C1
    ],
)
def test_escape(user_input: str, expected_output: str):
    json = {
        "$schema": "https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/schemas/sarif-schema-2.1.0.json",
        "runs": [
            {
                "invocations": [
                    {
                        "executionSuccessful": True,
                        "toolExecutionNotifications": [
                            {
                                "level": "error",
                                "message": {
                                    "text": user_input,
                                },
                            }
                        ],
                    }
                ],
            }
        ],
        "version": "2.1.0",
    }
    sarif_input = SarifFile.model_validate(json)
    commands = sarif_to_github_annotations(sarif_input)

    assert len(commands) == 1
    assert commands[0] == expected_output
