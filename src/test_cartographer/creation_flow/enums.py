"""Closed vocabularies for the integrated Creation Flow."""

from enum import StrEnum


class CreationFlowStatus(StrEnum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"


class CreationStageKind(StrEnum):
    GUIDED_INTAKE = "guided_intake"
    BROWSER_DISCOVERY = "browser_discovery"
    SYNTHESIS_HANDOFF = "synthesis_handoff"
    POM_SYNTHESIS = "pom_synthesis"
    ADAPTATION_PLANNING = "adaptation_planning"
    SOURCE_DELIVERY = "source_delivery"
    FRAMEWORK_EXECUTION = "framework_execution"


class CreationStageStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
