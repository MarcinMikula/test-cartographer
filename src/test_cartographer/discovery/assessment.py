"""Deterministic readiness report for a discovery run."""

from __future__ import annotations

from pydantic import computed_field

from test_cartographer.context.models import ContractModel, Identifier
from test_cartographer.discovery.enums import DiscoveryDecision, DiscoveryTargetState
from test_cartographer.discovery.models import ProcessDiscoveryRun


class DiscoveryReadinessReport(ContractModel):
    run_id: Identifier
    target_count: int
    selected_target_count: int
    ambiguity_count: int
    unresolved_ambiguity_count: int
    missing_target_count: int
    human_selection_count: int
    live_provider_used: bool
    accepted: bool

    @computed_field
    @property
    def ready_for_context_application(self) -> bool:
        return (
            self.accepted
            and self.selected_target_count == self.target_count
            and self.unresolved_ambiguity_count == 0
            and self.missing_target_count == 0
        )


def assess_discovery(run: ProcessDiscoveryRun) -> DiscoveryReadinessReport:
    return DiscoveryReadinessReport(
        run_id=run.id,
        target_count=len(run.targets),
        selected_target_count=sum(
            item.state is DiscoveryTargetState.SELECTED for item in run.targets
        ),
        ambiguity_count=len(run.ambiguities),
        unresolved_ambiguity_count=sum(
            item.selected_candidate_id is None for item in run.ambiguities
        ),
        missing_target_count=sum(
            item.state is DiscoveryTargetState.MISSING for item in run.targets
        ),
        human_selection_count=sum(
            item.selection_authority is not None and item.selection_authority.value == "human"
            for item in run.targets
        ),
        live_provider_used=run.live_provider_used,
        accepted=run.decision is DiscoveryDecision.ACCEPTED,
    )
