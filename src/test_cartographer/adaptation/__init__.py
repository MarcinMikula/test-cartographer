"""Framework workspace inspection and adaptation planning."""

from test_cartographer.adaptation.models import AdaptationPlan, FrameworkSnapshot, WorkspaceProfile
from test_cartographer.adaptation.planner import build_adaptation_plan
from test_cartographer.adaptation.review import review_adaptation_plan
from test_cartographer.adaptation.scanner import inspect_framework

__all__ = [
    "AdaptationPlan",
    "FrameworkSnapshot",
    "WorkspaceProfile",
    "build_adaptation_plan",
    "inspect_framework",
    "review_adaptation_plan",
]
