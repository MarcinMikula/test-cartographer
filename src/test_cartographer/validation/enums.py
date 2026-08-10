"""Closed vocabularies for external-validation evidence contract version 0.1."""

from enum import StrEnum


class ValidationTargetDifficulty(StrEnum):
    SIMPLE = "simple"
    DYNAMIC_ASYNC = "dynamic_async"
    MULTI_PAGE_STATEFUL = "multi_page_stateful"
    DIFFICULT = "difficult"
    ENTERPRISE_CONSTRAINED = "enterprise_constrained"


class ValidationTargetControl(StrEnum):
    PROJECT_CONTROLLED = "project_controlled"
    EXTERNAL_STABLE = "external_stable"
    EXTERNAL_LOW_CONTROL = "external_low_control"
    POLICY_CONSTRAINED = "policy_constrained"


class ValidationAuthenticationRequirement(StrEnum):
    NONE = "none"
    REQUIRED = "required"
    UNKNOWN = "unknown"


class ValidationWorkflowKind(StrEnum):
    TESTCARTOGRAPHER = "testcartographer"
    MANUAL_AUTOMATION_AIDS = "manual_automation_aids"
    CODEGEN_PLUS_GENERAL_LLM = "codegen_plus_general_llm"


class ValidationRunCompletion(StrEnum):
    COMPLETED = "completed"
    INCOMPLETE = "incomplete"
    STOPPED = "stopped"


class ValidationLifecycleStage(StrEnum):
    BOOTSTRAP = "bootstrap"
    INTAKE = "intake"
    BROWSER_DISCOVERY = "browser_discovery"
    CONTEXT_REVIEW = "context_review"
    SYNTHESIS = "synthesis"
    REPOSITORY_MAPPING = "repository_mapping"
    SOURCE_REVIEW = "source_review"
    DELIVERY = "delivery"
    EXECUTION = "execution"
    MAINTENANCE = "maintenance"
    EXPANSION = "expansion"
    GENERAL = "general"


class ValidationFindingKind(StrEnum):
    FAILURE = "failure"
    FRICTION = "friction"
    UNSUPPORTED_ASSUMPTION = "unsupported_assumption"
    SAFETY_STOP = "safety_stop"
    MEASUREMENT_ISSUE = "measurement_issue"


class ValidationStopCondition(StrEnum):
    AUTHENTICATION_NOT_APPROVED = "authentication_not_approved"
    DESTRUCTIVE_OR_IRREVERSIBLE_ACTION = "destructive_or_irreversible_action"
    SENSITIVE_DATA_BOUNDARY = "sensitive_data_boundary"
    OUTSIDE_APPROVED_TARGET = "outside_approved_target"
    RATE_LIMIT_OR_ANTI_ABUSE = "rate_limit_or_anti_abuse"
    POLICY_DECISION_REQUIRED = "policy_decision_required"
    UNRESTRICTED_CAPTURE_REQUIRED = "unrestricted_capture_required"
    COMPARABILITY_BROKEN = "comparability_broken"
    RETENTION_SAFETY_UNCERTAIN = "retention_safety_uncertain"


class ValidationOperatorDifficulty(StrEnum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    BLOCKED = "blocked"


class ValidationResultConfidence(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ValidationWorkflowReuseIntent(StrEnum):
    YES = "yes"
    UNCERTAIN = "uncertain"
    NO = "no"


class ValidationTargetFamiliarity(StrEnum):
    NEW_TO_OPERATOR = "new_to_operator"
    SEEN_BEFORE = "seen_before"
    AUTOMATED_BEFORE = "automated_before"


class ValidationArtefactKind(StrEnum):
    CONTEXT_BUNDLE = "context_bundle"
    INTAKE_SESSION = "intake_session"
    PROJECT_PROFILE_REFERENCE = "project_profile_reference"
    BROWSER_OBSERVATION = "browser_observation"
    SYNTHESIS_SUMMARY = "synthesis_summary"
    ADAPTATION_PLAN = "adaptation_plan"
    SOURCE_PATCH = "source_patch"
    EXECUTION_EVIDENCE = "execution_evidence"
    OPERATOR_SUMMARY = "operator_summary"


class ValidationArtefactProducer(StrEnum):
    TESTCARTOGRAPHER = "testcartographer"
    FRAMEWORK = "framework"
    OPERATOR = "operator"
    SYSTEM = "system"
