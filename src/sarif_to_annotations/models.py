from __future__ import annotations

from pydantic import BaseModel, Field


class Message(BaseModel):
    text: str = ""


class Descriptor(BaseModel):
    id: str | None = None


class Notification(BaseModel):
    descriptor: Descriptor | None = None
    level: str | None = None
    message: Message


class Region(BaseModel):
    startLine: int | None = None


class ArtifactLocation(BaseModel):
    uri: str | None = None


class PhysicalLocation(BaseModel):
    artifactLocation: ArtifactLocation | None = None
    region: Region | None = None


class Location(BaseModel):
    physicalLocation: PhysicalLocation | None = None


class Result(BaseModel):
    ruleId: str | None = None
    level: str | None = None
    message: Message
    locations: list[Location] = Field(default_factory=list)


class RuleDefaultConfiguration(BaseModel):
    level: str | None = None


class Rule(BaseModel):
    id: str
    defaultConfiguration: RuleDefaultConfiguration | None = None


class Driver(BaseModel):
    rules: list[Rule] = Field(default_factory=list)


class Tool(BaseModel):
    driver: Driver


class Invocation(BaseModel):
    toolExecutionNotifications: list[Notification] = Field(default_factory=list)


class Run(BaseModel):
    results: list[Result] = Field(default_factory=list)
    invocations: list[Invocation] = Field(default_factory=list)
    tool: Tool | None = None


class SarifFile(BaseModel):
    runs: list[Run] = Field(default_factory=list)
