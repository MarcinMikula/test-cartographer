from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    AdaptationTargetKind,
    RepositoryEntryKind,
)
from test_cartographer.adaptation.models import (
    AdaptationOperation,
    FrameworkSnapshot,
    RepositoryEntry,
    WorkspaceProfile,
)


def test_workspace_profile_rejects_parent_traversal():
    with pytest.raises(ValidationError, match="safe repository-relative"):
        WorkspaceProfile(
            id="workspace_invalid",
            repository_label="invalid",
            root_marker_files=("README.md",),
            allowed_roots=("../pages",),
        )


def test_workspace_profile_rejects_duplicate_roots():
    with pytest.raises(ValidationError, match="must be unique"):
        WorkspaceProfile(
            id="workspace_invalid",
            repository_label="invalid",
            root_marker_files=("README.md",),
            allowed_roots=("pages", "pages"),
        )


def test_directory_entry_rejects_file_metadata():
    with pytest.raises(ValidationError, match="directory entry"):
        RepositoryEntry(
            path="pages",
            kind=RepositoryEntryKind.DIRECTORY,
            size_bytes=1,
            sha256="0" * 64,
        )


def test_snapshot_privacy_flags_cannot_be_true(framework_snapshot):
    payload = framework_snapshot.model_dump(mode="json")
    payload["source_contents_persisted"] = True
    with pytest.raises(ValidationError):
        FrameworkSnapshot.model_validate(payload)


def test_operation_rejects_duplicate_dependencies():
    with pytest.raises(ValidationError, match="must be unique"):
        AdaptationOperation(
            id="adapt_duplicate",
            kind=AdaptationOperationKind.CREATE_FILE,
            target_kind=AdaptationTargetKind.PAGE,
            target_path="pages/catalog_page.py",
            symbol_name="CatalogPage",
            source_proposal_ids=("pom_page_catalog",),
            rationale="Map the accepted page.",
            depends_on=("adapt_other", "adapt_other"),
        )
