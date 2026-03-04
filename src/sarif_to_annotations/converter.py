from __future__ import annotations
import itertools

from string.templatelib import Interpolation, Template
from sarif_to_annotations.models import Run, SarifFile


# Maps SARIF levels into GitHub commands/levels
# (https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands)
#
# SARIF levels specs: https://docs.oasis-open.org/sarif/sarif/v2.1.0/csprd01/sarif-v2.1.0-csprd01.html#_Toc10541293
LEVEL_MAP = {
    "error": "error",
    "warning": "warning",
    "note": "notice",
    "none": "notice",
}

# Based on https://github.com/actions/toolkit/blob/85466c0f54d41d862e6e00e9b66e15a0ef70e562/packages/core/src/command.ts#L103-L117
ESCAPES = {
    ord("%"): "%25",
    ord("\r"): "%0D",
    ord("\n"): "%0A",
    ord(":"): "%3A",
    ord(","): "%2C",
    # Additional preventions (not from the actions toolkit)
    ord("<"): "%3C",
    ord(">"): "%3E",
    ord("\\"): "",
}

# Removes all control characters (C0: 0-31, and C1: 127-159)
# https://en.wikipedia.org/wiki/C0_and_C1_control_codes
ESCAPES.update((dec_val, "") for dec_val in itertools.chain(range(32), range(127, 160)))


def _escape(s: str) -> str:
    return s.translate(ESCAPES)


def _to_gh_level(level: str | None) -> str:
    if not level:
        return "error"
    return LEVEL_MAP.get(level.lower(), "notice")


def _rule_levels(run: Run) -> dict[str, str | None]:
    if not run.tool:
        return {}
    return {
        rule.id: (
            rule.defaultConfiguration.level if rule.defaultConfiguration else None
        )
        for rule in run.tool.driver.rules
    }


def _create_annotation(
    *, level: str, message: str, file: str | None = None, line: int | None = None
) -> Template:
    """
    Creates a GH command to create an annotation.

    Docs: https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-commands#setting-a-notice-message
    """

    tpl = t"::{level}"

    # Keeps track of whether we need to append a comma
    metadata_counter = 0

    def _append_metadata(meta: Template) -> Template:
        """
        Appends to metadata with a comma-separator.

        Example:
            >>> s = t"::error"
            >>> metadata_counter = 0
            >>> s = _append_metadata(t"foo=1") # Value is now: '::error foo=1'
            >>> s = _append_metadata(t"bar=1") # Value is now: '::error foo=1,bar=1'
        """
        nonlocal metadata_counter

        part = t""
        if metadata_counter > 0:
            part = t","
        else:
            part += t" "

        metadata_counter += 1
        part += meta
        return part

    if file:
        tpl += _append_metadata(t"file={file}")
    if line:
        tpl += _append_metadata(t"line={line}")

    tpl += t"::{message}"
    return tpl


def command_to_string(tpl: Template) -> str:
    s = ""
    for item in tpl:
        if isinstance(item, Interpolation):
            if item.conversion:
                raise TypeError(
                    f"Conversions not supported, got: {{{item.expression}!{item.conversion}}}"
                )
            if isinstance(item.value, Template):
                s += command_to_string(item.value)
            elif isinstance(item.value, str):
                s += _escape(item.value)
            elif isinstance(item.value, (int, float)):
                s += str(item.value)
            else:
                raise TypeError(
                    f"Got an unsupported value type for expression {{{item.expression}}}: {type(item.value)}"
                )
        elif isinstance(item, str):
            s += item
        else:
            raise TypeError(f"Unexpected type: {type(item)}")
    return s


def _sarif_to_github_annotations(sarif: SarifFile) -> list[Template]:
    commands: list[Template] = []

    for run in sarif.runs:
        rules_levels = _rule_levels(run)

        for result in run.results:
            # Attempt to retrieve the level for the finding inside SARIF
            sarif_level: str | None = result.level
            if not sarif_level and result.ruleId:
                sarif_level = rules_levels.get(result.ruleId)

            # Convert the SARIF level into a value GH understands
            gh_level_command = _to_gh_level(sarif_level)

            # Retrieve the location of the finding
            file: str | None = None
            line: int | None = None
            if result.locations:
                physical_location = result.locations[0].physicalLocation
                if physical_location and physical_location.artifactLocation:
                    file = physical_location.artifactLocation.uri
                if physical_location and physical_location.region:
                    line = physical_location.region.startLine

            commands.append(
                _create_annotation(
                    level=gh_level_command,
                    message=result.message.text,
                    file=file,
                    line=line,
                )
            )

        for invocation in run.invocations:
            for notification in invocation.toolExecutionNotifications:
                level = _to_gh_level(notification.level)
                message = notification.message.text
                if notification.descriptor and notification.descriptor.id:
                    message = f"{notification.descriptor.id}: {message}"
                commands.append(_create_annotation(level=level, message=message))

    return commands


def sarif_to_github_annotations(sarif: SarifFile) -> list[str]:
    return [command_to_string(cmd) for cmd in _sarif_to_github_annotations(sarif)]
