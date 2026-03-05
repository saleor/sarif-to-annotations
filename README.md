# sarif-to-annotations

Python CLI that converts SARIF files into annotations that GitHub can understand.

## Installation

Either:

- Use the container image from GHCR (`ghcr.io/saleor/sarif-to-annotations`)
<!-- - Use the action.yaml (later on) -->
- Install from PyPI: `pip install sarif-to-annotations`

## Usage

```
$ sarif-to-annotations <PATH_TO_SARIF>
```

For example, if using GHCR, you can do the following:

```
$ docker run \
    -v ./:/work:ro \
    -w /work \
    --rm \
    ghcr.io/saleor/sarif-to-annotations \
    ./test/assets/semgrep-results-found.json
```

Example output:

```
::error file=.github/workflows/create-tag-with-release-pr.yml,line=83::Potential script injection through string interpolation%2C use an intermediate environment variable instead of ${{ ... }}.
::error file=.github/workflows/publish-load-test.yml,line=17::Potential script injection through string interpolation%2C use an intermediate environment variable instead of ${{ ... }}.
::error file=.github/workflows/publish-load-test.yml,line=43::Potential script injection through string interpolation%2C use an intermediate environment variable instead of ${{ ... }}.
::error file=.github/workflows/test-env-deploy.yml,line=40::Potential script injection through string interpolation%2C use an intermediate environment variable instead of ${{ ... }}.
::error file=.github/workflows/tests-and-linters.yml,line=80::Potential script injection through string interpolation%2C use an intermediate environment variable instead of ${{ ... }}.
```
