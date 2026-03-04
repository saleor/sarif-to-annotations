from pathlib import Path

from sarif_to_annotations.models import SarifFile

ASSETS_DIR = Path(__file__).parent / "assets"


def load_sarif(filename: str) -> SarifFile:
    return SarifFile.model_validate_json((ASSETS_DIR / filename).read_text())


def load_expected_results(filename: str) -> list[str]:
    return (ASSETS_DIR / filename).read_text().splitlines(keepends=False)
