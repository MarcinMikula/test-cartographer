"""Deterministic Sprint 6 templates for one accepted POM adaptation plan."""

from __future__ import annotations

import ast
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from test_cartographer.adaptation.enums import (
    AdaptationOperationKind,
    AdaptationPlanStatus,
    AdaptationTargetKind,
)
from test_cartographer.adaptation.models import (
    AdaptationOperation,
    AdaptationPlan,
    FrameworkSnapshot,
    RepositoryEntryKind,
    WorkspaceProfile,
)
from test_cartographer.adaptation.scanner import inspect_framework
from test_cartographer.context.enums import ActionKind, LocatorStrategy
from test_cartographer.delivery.enums import SourceChangeKind
from test_cartographer.delivery.framework_contract import validate_generation_framework_contract
from test_cartographer.delivery.models import (
    CodePatch,
    GenerationProfile,
    ReusedTarget,
    SourceChange,
)
from test_cartographer.synthesis.enums import ProposalOwnerKind, SynthesisRunStatus
from test_cartographer.synthesis.models import (
    AuthorizedElement,
    PomProposal,
    ProposedAction,
    ProposedMethod,
    SynthesisRun,
)

_FORBIDDEN_CALLS = {"eval", "exec", "compile", "open", "__import__"}
_FORBIDDEN_IMPORTS = {"subprocess", "socket", "requests", "httpx", "shutil"}


def build_code_patch(
    run: SynthesisRun,
    plan: AdaptationPlan,
    workspace_profile: WorkspaceProfile,
    generation_profile: GenerationProfile,
    snapshot: FrameworkSnapshot,
    framework_root: str | Path,
    *,
    patch_id: str,
    created_at: datetime,
) -> CodePatch:
    """Build exact source changes without modifying the framework."""

    _validate_inputs(run, plan, workspace_profile, generation_profile, snapshot)
    root = Path(framework_root).resolve()
    current = inspect_framework(
        root,
        workspace_profile,
        snapshot_id=f"{snapshot.id}_delivery_preflight",
        captured_at=datetime.now(timezone.utc),
    )
    if current.root_fingerprint != snapshot.root_fingerprint:
        raise ValueError("framework fingerprint changed after adaptation planning")

    proposal = run.proposal
    assert proposal is not None
    operation_by_target = {
        operation.target_kind: operation for operation in plan.operations
        if operation.target_kind in {
            AdaptationTargetKind.FIXTURE,
            AdaptationTargetKind.TEST,
        }
    }
    operation_by_symbol = {operation.symbol_name: operation for operation in plan.operations}

    generated_sources: dict[str, str] = {}
    for page in proposal.pages:
        operation = operation_by_symbol.get(page.class_name)
        if operation is None:
            raise ValueError(f"accepted plan has no operation for page {page.class_name}")
        generated_sources[operation.id] = _render_page(proposal, page.id, run)

    for component in proposal.components:
        operation = operation_by_symbol.get(component.class_name)
        if operation is None:
            raise ValueError(f"accepted plan has no operation for component {component.class_name}")
        generated_sources[operation.id] = _render_component(proposal, component.id, run)

    fixture_operation = operation_by_target.get(AdaptationTargetKind.FIXTURE)
    if fixture_operation is None:
        raise ValueError("accepted plan has no fixture operation")
    generated_sources[fixture_operation.id] = _render_fixture(
        proposal,
        generation_profile,
        fixture_operation,
    )

    test_operation = operation_by_target.get(AdaptationTargetKind.TEST)
    if test_operation is None:
        raise ValueError("accepted plan has no test operation")
    generated_sources[test_operation.id] = _render_test(
        proposal,
        run,
        generation_profile,
    )

    changes: list[SourceChange] = []
    reused: list[ReusedTarget] = []
    snapshot_entries = {entry.path: entry for entry in snapshot.entries}

    for operation in plan.operations:
        if operation.kind is AdaptationOperationKind.REUSE_SYMBOL:
            reused.append(
                ReusedTarget(
                    operation_id=operation.id,
                    target_kind=operation.target_kind,
                    target_path=operation.target_path,
                    symbol_name=operation.symbol_name,
                )
            )
            continue
        if operation.kind is AdaptationOperationKind.EXTEND_SYMBOL:
            target = root / operation.target_path
            if not target.is_file():
                raise ValueError(f"extend_symbol target is missing: {operation.target_path}")
            entry = snapshot_entries.get(operation.target_path)
            if entry is None or entry.kind is not RepositoryEntryKind.FILE or entry.sha256 is None:
                raise ValueError(f"snapshot has no file hash for {operation.target_path}")
            before_bytes = target.read_bytes()
            before_hash = hashlib.sha256(before_bytes).hexdigest()
            if before_hash != entry.sha256:
                raise ValueError(f"target changed after snapshot: {operation.target_path}")
            before_text = before_bytes.decode("utf-8")
            replacement = _render_extended_object_file(
                proposal,
                run,
                operation,
                before_text,
            )
            _validate_combined_python(replacement, operation.target_path)
            changes.append(
                _source_change(
                    operation,
                    kind=SourceChangeKind.REPLACE_FILE,
                    content=replacement,
                    before=before_hash,
                    after_bytes=replacement.encode("utf-8"),
                )
            )
            continue

        source = generated_sources.get(operation.id)
        if source is None:
            raise ValueError(f"no deterministic template for operation {operation.id}")
        target = root / operation.target_path
        if target.is_symlink() or any(parent.is_symlink() for parent in target.parents if parent != root.parent):
            raise ValueError(f"symlinked delivery target is not supported: {operation.target_path}")

        if operation.kind is AdaptationOperationKind.CREATE_FILE:
            if target.exists():
                raise ValueError(f"create_file target already exists: {operation.target_path}")
            rendered = _normalize_new_file(source)
            _validate_generated_python(rendered, operation)
            changes.append(
                _source_change(
                    operation,
                    kind=SourceChangeKind.CREATE_FILE,
                    content=rendered,
                    before=None,
                    after_bytes=rendered.encode("utf-8"),
                )
            )
            continue

        if operation.kind is not AdaptationOperationKind.ADD_SYMBOL:
            raise ValueError(f"unsupported adaptation operation: {operation.kind.value}")
        if not target.is_file():
            raise ValueError(f"add_symbol target is missing: {operation.target_path}")
        entry = snapshot_entries.get(operation.target_path)
        if entry is None or entry.kind is not RepositoryEntryKind.FILE or entry.sha256 is None:
            raise ValueError(f"snapshot has no file hash for {operation.target_path}")
        before_bytes = target.read_bytes()
        before_hash = hashlib.sha256(before_bytes).hexdigest()
        if before_hash != entry.sha256:
            raise ValueError(f"target changed after snapshot: {operation.target_path}")
        before_text = before_bytes.decode("utf-8")
        newline = "\r\n" if "\r\n" in before_text else "\n"
        snippet = _append_snippet(source, before_text, newline)
        combined = before_text + snippet
        _validate_generated_python(source, operation)
        _validate_combined_python(combined, operation.target_path)
        changes.append(
            _source_change(
                operation,
                kind=SourceChangeKind.APPEND_SYMBOL,
                content=snippet,
                before=before_hash,
                after_bytes=combined.encode("utf-8"),
            )
        )

    expected_operation_ids = {operation.id for operation in plan.operations}
    represented_operation_ids = {item.operation_id for item in changes} | {
        item.operation_id for item in reused
    }
    if represented_operation_ids != expected_operation_ids:
        raise ValueError("code patch must represent every accepted adaptation operation")

    return CodePatch(
        id=patch_id,
        plan_id=plan.id,
        workspace_profile_id=workspace_profile.id,
        generation_profile_id=generation_profile.id,
        snapshot_id=snapshot.id,
        snapshot_fingerprint=snapshot.root_fingerprint,
        synthesis_run_id=run.id,
        proposal_id=proposal.id,
        context_id=proposal.context_id,
        created_at=created_at,
        changes=tuple(changes),
        reused_targets=tuple(reused),
        verification_commands=(
            "python -m compileall -q pages components tests testdata",
            f"python -m pytest --collect-only -q {test_operation.target_path}",
            f"python -m pytest -q {test_operation.target_path}",
        ),
    )


def _validate_inputs(
    run: SynthesisRun,
    plan: AdaptationPlan,
    workspace_profile: WorkspaceProfile,
    generation_profile: GenerationProfile,
    snapshot: FrameworkSnapshot,
) -> None:
    if run.status is not SynthesisRunStatus.ACCEPTED or run.proposal is None:
        raise ValueError("source generation requires an accepted synthesis run")
    if plan.status is not AdaptationPlanStatus.ACCEPTED:
        raise ValueError("source generation requires a human-accepted adaptation plan")
    if plan.open_questions:
        raise ValueError("source generation requires an adaptation plan without open questions")
    if plan.synthesis_run_id != run.id or plan.proposal_id != run.proposal.id:
        raise ValueError("adaptation plan does not belong to the supplied synthesis run")
    if plan.context_id != run.proposal.context_id:
        raise ValueError("adaptation plan context does not match the proposal")
    if plan.workspace_profile_id != workspace_profile.id:
        raise ValueError("adaptation plan does not belong to the workspace profile")
    if plan.snapshot_id != snapshot.id or plan.snapshot_fingerprint != snapshot.root_fingerprint:
        raise ValueError("adaptation plan does not match the supplied snapshot")
    if snapshot.profile_id != workspace_profile.id:
        raise ValueError("framework snapshot does not belong to the workspace profile")
    if generation_profile.workspace_profile_id != workspace_profile.id:
        raise ValueError("generation profile does not belong to the workspace profile")

    validate_generation_framework_contract(snapshot, generation_profile)

    required_data = {
        action.test_data_id
        for method in run.proposal.methods
        for action in method.actions
        if action.test_data_id is not None
    }
    bound_data = {item.test_data_id for item in generation_profile.test_data_bindings}
    missing = sorted(required_data - bound_data)
    if missing:
        raise ValueError(f"generation profile is missing test-data bindings: {missing}")


def _source_change(
    operation: AdaptationOperation,
    *,
    kind: SourceChangeKind,
    content: str,
    before: str | None,
    after_bytes: bytes,
) -> SourceChange:
    content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()
    return SourceChange(
        operation_id=operation.id,
        kind=kind,
        target_kind=operation.target_kind,
        target_path=operation.target_path,
        symbol_name=operation.symbol_name,
        source_proposal_ids=operation.source_proposal_ids,
        expected_before_sha256=before,
        content=content,
        content_sha256=content_hash,
        expected_after_sha256=hashlib.sha256(after_bytes).hexdigest(),
    )



def _render_extended_object_file(
    proposal: PomProposal,
    run: SynthesisRun,
    operation: AdaptationOperation,
    before_text: str,
) -> str:
    """Return the complete existing file with only reviewed missing class members inserted."""

    tree = ast.parse(before_text, filename=operation.target_path)
    class_node = next(
        (
            node
            for node in tree.body
            if isinstance(node, ast.ClassDef) and node.name == operation.symbol_name
        ),
        None,
    )
    if class_node is None or class_node.end_lineno is None:
        raise ValueError(f"extend_symbol class is missing: {operation.symbol_name}")
    existing_methods, existing_properties = _class_member_names(class_node)
    duplicate_methods = sorted(set(operation.method_names) & existing_methods)
    duplicate_properties = sorted(set(operation.property_names) & existing_properties)
    wrong_kind_methods = sorted(set(operation.method_names) & existing_properties)
    wrong_kind_properties = sorted(set(operation.property_names) & existing_methods)
    if duplicate_methods or duplicate_properties:
        raise ValueError(
            "planned class members already exist in "
            f"{operation.target_path}: methods={duplicate_methods}, properties={duplicate_properties}"
        )
    if wrong_kind_methods or wrong_kind_properties:
        raise ValueError(
            "existing class member kind conflicts with planned extension in "
            f"{operation.target_path}: methods_as_properties={wrong_kind_methods}, "
            f"properties_as_methods={wrong_kind_properties}"
        )

    if operation.target_kind is AdaptationTargetKind.PAGE:
        owner = next(item for item in proposal.pages if item.class_name == operation.symbol_name)
        methods = [_method(proposal, method_id) for method_id in owner.method_ids]
        owner_source_id = owner.source_page_id
    elif operation.target_kind is AdaptationTargetKind.COMPONENT:
        owner = next(item for item in proposal.components if item.class_name == operation.symbol_name)
        methods = [_method(proposal, method_id) for method_id in owner.method_ids]
        owner_source_id = owner.source_component_id
    else:
        raise ValueError("extend_symbol is supported only for page/component classes")

    method_by_name = {method.name: method for method in methods}
    request_elements = {
        item.id: item
        for item in run.request.elements
        if item.owner_id == owner_source_id
    }
    property_by_name = {
        _element_attribute(element.id): element for element in request_elements.values()
    }
    missing_method_templates = sorted(set(operation.method_names) - set(method_by_name))
    missing_property_templates = sorted(set(operation.property_names) - set(property_by_name))
    if missing_method_templates or missing_property_templates:
        raise ValueError(
            "no deterministic class-member template for planned extension: "
            f"methods={missing_method_templates}, properties={missing_property_templates}"
        )

    lines: list[str] = [
        "",
        f"    # TestCartographer expansion trace: {', '.join(operation.source_proposal_ids)}",
    ]
    for property_name in operation.property_names:
        lines.extend(_render_locator_property(property_by_name[property_name], indent="    "))
    for method_name in operation.method_names:
        lines.extend(_render_method(method_by_name[method_name], run, indent="    "))

    snippet = "\n".join(lines).rstrip() + "\n"
    replacement = _insert_after_class_body(before_text, class_node, snippet)
    if operation.property_names:
        replacement = _ensure_locator_import(replacement)
    parsed = ast.parse(replacement, filename=operation.target_path)
    updated_class = next(
        node for node in parsed.body if isinstance(node, ast.ClassDef) and node.name == operation.symbol_name
    )
    updated_methods, updated_properties = _class_member_names(updated_class)
    missing_methods = sorted(set(operation.method_names) - updated_methods)
    missing_properties = sorted(set(operation.property_names) - updated_properties)
    if missing_methods or missing_properties:
        raise ValueError(
            f"extended class is missing planned members: methods={missing_methods}, "
            f"properties={missing_properties}"
        )
    _validate_safe_ast(parsed, operation.target_path)
    return replacement


def _class_member_names(class_node: ast.ClassDef) -> tuple[set[str], set[str]]:
    methods: set[str] = set()
    properties: set[str] = set()
    for node in class_node.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if any(_ast_name(item) == "property" for item in node.decorator_list):
            properties.add(node.name)
        else:
            methods.add(node.name)
    return methods, properties
def _insert_after_class_body(before_text: str, class_node: ast.ClassDef, snippet: str) -> str:
    newline = "\r\n" if "\r\n" in before_text else "\n"
    normalized_snippet = snippet.replace("\r\n", "\n").replace("\n", newline)
    lines = before_text.splitlines(keepends=True)
    insertion_index = class_node.end_lineno
    if insertion_index > len(lines):
        raise ValueError("class end position is outside source file")
    if insertion_index and not lines[insertion_index - 1].endswith(("\n", "\r")):
        lines[insertion_index - 1] += newline
    lines.insert(insertion_index, normalized_snippet)
    return "".join(lines)


def _ensure_locator_import(source: str) -> str:
    if re.search(r"from playwright\.sync_api import .*\bLocator\b", source):
        return source
    pattern = re.compile(r"^from playwright\.sync_api import ([^\n]+)$", re.MULTILINE)
    match = pattern.search(source)
    if match is None:
        raise ValueError("existing POM file lacks playwright.sync_api import required for locator extension")
    imported = [item.strip() for item in match.group(1).split(",")]
    imported = list(dict.fromkeys(["Locator", *imported]))
    return source[: match.start(1)] + ", ".join(imported) + source[match.end(1) :]

def _render_component(proposal: PomProposal, component_id: str, run: SynthesisRun) -> str:
    component = next(item for item in proposal.components if item.id == component_id)
    methods = [
        _method(proposal, method_id)
        for method_id in component.method_ids
    ]
    elements = _elements_for_methods(methods, run)
    lines = [
        f'"""Generated from accepted proposal {proposal.id}; review before production use."""',
        "",
        "from __future__ import annotations",
        "",
        "from playwright.sync_api import Locator, Page",
        "",
        "from components.base_component import BaseComponent",
        "",
        f"TRACEABILITY = {tuple([component.id, component.source_component_id, *component.method_ids])!r}",
        "",
        "",
        f"class {component.class_name}(BaseComponent):",
        "    \"\"\"Application-facing actions for the mapped UI component.\"\"\"",
        "",
        "    def __init__(self, page: Page) -> None:",
        "        super().__init__(page)",
    ]
    for element in elements:
        lines.extend(_render_locator_property(element, indent="    "))
    for method in methods:
        lines.extend(_render_method(method, run, indent="    "))
    return "\n".join(lines).rstrip() + "\n"


def _render_page(proposal: PomProposal, page_id: str, run: SynthesisRun) -> str:
    page = next(item for item in proposal.pages if item.id == page_id)
    methods = [_method(proposal, method_id) for method_id in page.method_ids]
    method_elements = _elements_for_methods(methods, run)
    assertion_element_ids = {
        element_id
        for assertion in proposal.test.assertions
        if assertion.page_id == page.source_page_id
        for element_id in assertion.related_element_ids
    }
    request_element_by_id = {item.id: item for item in run.request.elements}
    elements_by_id = {item.id: item for item in method_elements}
    for element_id in assertion_element_ids:
        element = request_element_by_id[element_id]
        if element.owner_id == page.source_page_id:
            elements_by_id[element.id] = element
    elements = [elements_by_id[element_id] for element_id in sorted(elements_by_id)]
    component_objects = [
        next(item for item in proposal.components if item.id == component_id)
        for component_id in page.component_object_ids
    ]
    lines = [
        f'"""Generated from accepted proposal {proposal.id}; review before production use."""',
        "",
        "from __future__ import annotations",
        "",
        "from playwright.sync_api import Locator, Page",
        "",
    ]
    for component in component_objects:
        lines.append(
            f"from components.{_snake_case(component.class_name)} import {component.class_name}"
        )
    lines.extend(
        [
            "from pages.base_page import BasePage",
            "",
            f"TRACEABILITY = {tuple([page.id, page.source_page_id, *page.method_ids, *page.component_object_ids])!r}",
            "",
            "",
            f"class {page.class_name}(BasePage):",
            "    \"\"\"Application-facing actions and state for the mapped page.\"\"\"",
            "",
            "    def __init__(self, page: Page, base_url: str = \"\") -> None:",
            "        super().__init__(page, base_url=base_url)",
        ]
    )
    for component in component_objects:
        attribute = _component_attribute(component.source_component_id)
        lines.append(f"        self.{attribute} = {component.class_name}(page)")
    for element in elements:
        lines.extend(_render_locator_property(element, indent="    "))
    for method in methods:
        lines.extend(_render_method(method, run, indent="    "))
    return "\n".join(lines).rstrip() + "\n"


def _render_fixture(
    proposal: PomProposal,
    profile: GenerationProfile,
    operation: AdaptationOperation,
) -> str:
    fixture = next(item for item in proposal.fixtures if item.name == operation.symbol_name)
    bindings = [
        f"            {item.fixture_key!r}: {item.value!r},"
        for item in profile.test_data_bindings
    ]
    return "\n".join(
        [
            f"# TestCartographer trace: {fixture.id}, {proposal.id}",
            "import os",
            "from collections.abc import Generator",
            "",
            "import pytest",
            "from playwright.sync_api import sync_playwright",
            "",
            "",
            "@pytest.fixture",
            f"def {fixture.name}() -> Generator[dict[str, object], None, None]:",
            "    \"\"\"Provide one bounded browser session and optional non-secret test data.\"\"\"",
            f"    base_url = os.environ.get({profile.environment_url_variable!r})",
            "    if not base_url:",
            f"        pytest.fail({('Missing required environment variable: ' + profile.environment_url_variable)!r})",
            "",
            "    with sync_playwright() as playwright:",
            f"        browser = playwright.chromium.launch(headless={profile.browser_headless!r})",
            "        page = browser.new_page()",
            "        yield {",
            "            \"page\": page,",
            "            \"base_url\": base_url,",
            *bindings,
            "        }",
            "        browser.close()",
            "",
        ]
    )


def _render_test(
    proposal: PomProposal,
    run: SynthesisRun,
    profile: GenerationProfile,
) -> str:
    if len(proposal.pages) != 1:
        raise ValueError("Sprint 6 template supports exactly one proposed page")
    page = proposal.pages[0]
    page_variable = _snake_case(page.class_name)
    method_by_id = {item.id: item for item in proposal.methods}
    component_by_source = {item.source_component_id: item for item in proposal.components}
    binding_by_data = {item.test_data_id: item for item in profile.test_data_bindings}
    read_variables: list[str] = []
    lines = [
        f'"""Generated executable test from accepted proposal {proposal.id}."""',
        "",
        "from __future__ import annotations",
        "",
        "import pytest",
        "from playwright.sync_api import expect",
        "",
        f"from pages.{_snake_case(page.class_name)} import {page.class_name}",
        "",
        f"TRACEABILITY = {tuple([proposal.test.id, *proposal.test.method_ids, *(item.id for item in proposal.test.assertions)])!r}",
        "",
        "",
        "@pytest.mark.e2e",
        f"def {proposal.test.name}({proposal.fixtures[0].name}) -> None:",
        f"    page = {proposal.fixtures[0].name}[\"page\"]",
        f"    {page_variable} = {page.class_name}(page, base_url={proposal.fixtures[0].name}[\"base_url\"])",
    ]
    for method_id in proposal.test.method_ids:
        method = method_by_id[method_id]
        if len(method.actions) != 1:
            raise ValueError("Sprint 6 template supports one action per proposed method")
        action = method.actions[0]
        if method.owner_kind is ProposalOwnerKind.PAGE:
            owner = page_variable
        else:
            component = component_by_source[method.owner_source_id]
            owner = f"{page_variable}.{_component_attribute(component.source_component_id)}"
        arguments = ""
        if action.test_data_id is not None:
            binding = binding_by_data[action.test_data_id]
            arguments = f"{proposal.fixtures[0].name}[{binding.fixture_key!r}]"
        call = f"{owner}.{method.name}({arguments})"
        if action.kind is ActionKind.READ:
            variable = f"{method.name}_value"
            read_variables.append(variable)
            lines.append(f"    {variable} = {call}")
        else:
            lines.append(f"    {call}")

    related_ids = {
        element_id
        for assertion in proposal.test.assertions
        for element_id in assertion.related_element_ids
    }
    request_elements = {item.id: item for item in run.request.elements}
    asserted_elements = []
    for element_id in sorted(related_ids):
        element = request_elements[element_id]
        if element.owner_id == page.source_page_id:
            lines.append(
                f"    expect({page_variable}.{_element_attribute(element.id)}).to_be_visible()"
            )
            asserted_elements.append(element)

    if read_variables and profile.test_data_bindings:
        query_key = profile.test_data_bindings[0].fixture_key
        lines.extend(
            [
                f"    expected_fragment = str({proposal.fixtures[0].name}[{query_key!r}]).casefold()",
                f"    assert expected_fragment in str({read_variables[0]}).casefold(), (",
                "        \"The visible results do not contain the explicitly supplied expected result.\"",
                "    )",
                "",
            ]
        )
    elif read_variables:
        if len(read_variables) != 1 or len(asserted_elements) != 1:
            raise ValueError(
                "read-only generated test requires exactly one read result and one asserted element"
            )
        expected_value = asserted_elements[0].name.value
        lines.extend(
            [
                f"    expected_value = {expected_value!r}",
                f"    assert str({read_variables[0]}).strip() == expected_value, (",
                "        \"The visible read result does not equal the accepted observed element name.\"",
                "    )",
                "",
            ]
        )
    elif not asserted_elements:
        raise ValueError("generated test requires at least one executable assertion")
    return "\n".join(lines)


def _render_locator_property(element: AuthorizedElement, *, indent: str) -> list[str]:
    attribute = _element_attribute(element.id)
    expression = _locator_expression(element)
    return [
        "",
        f"{indent}@property",
        f"{indent}def {attribute}(self) -> Locator:",
        f"{indent}    \"\"\"Return the observed locator {element.primary_locator.id}.\"\"\"",
        f"{indent}    return {expression}",
    ]


def _render_method(method: ProposedMethod, run: SynthesisRun, *, indent: str) -> list[str]:
    if len(method.actions) != 1:
        raise ValueError("Sprint 6 template supports one action per proposed method")
    action = method.actions[0]
    lines = ["", f"{indent}def {method.name}"]
    if action.kind is ActionKind.FILL:
        signature = "(self, value: str) -> None:"
    elif action.kind is ActionKind.READ:
        signature = "(self) -> str:"
    else:
        signature = "(self) -> None:"
    lines[-1] += signature
    docstring = (
        "Open the mapped page through the framework navigation boundary."
        if action.kind is ActionKind.NAVIGATE
        else _safe_docstring(method.intent)
    )
    lines.append(f"{indent}    \"\"\"{docstring}\"\"\"")
    if action.kind is ActionKind.NAVIGATE:
        lines.append(f"{indent}    self.open()")
    else:
        if action.target_element_id is None:
            raise ValueError(f"method {method.id} requires a target element")
        attribute = _element_attribute(action.target_element_id)
        if action.kind is ActionKind.FILL:
            lines.append(f"{indent}    self.{attribute}.fill(value)")
        elif action.kind is ActionKind.CLICK:
            lines.append(f"{indent}    self.{attribute}.click()")
        elif action.kind is ActionKind.READ:
            lines.append(f"{indent}    return self.{attribute}.inner_text()")
        else:
            raise ValueError(f"unsupported Sprint 6 action: {action.kind.value}")
    return lines


def _locator_expression(element: AuthorizedElement) -> str:
    locator = element.primary_locator
    value = locator.value.value
    if locator.strategy is LocatorStrategy.ROLE:
        if ":" not in value:
            raise ValueError(f"role locator must use role:name form: {locator.id}")
        role, name = value.split(":", 1)
        return f"self.page.get_by_role({role!r}, name={name!r})"
    if locator.strategy is LocatorStrategy.LABEL:
        return f"self.page.get_by_label({value!r})"
    if locator.strategy is LocatorStrategy.TEST_ID:
        return f"self.page.get_by_test_id({value!r})"
    if locator.strategy is LocatorStrategy.PLACEHOLDER:
        return f"self.page.get_by_placeholder({value!r})"
    if locator.strategy is LocatorStrategy.TEXT:
        return f"self.page.get_by_text({value!r})"
    if locator.strategy is LocatorStrategy.CSS:
        return f"self.page.locator({value!r})"
    if locator.strategy is LocatorStrategy.XPATH:
        return f"self.page.locator({('xpath=' + value)!r})"
    raise ValueError(f"unsupported locator strategy: {locator.strategy.value}")


def _elements_for_methods(methods: list[ProposedMethod], run: SynthesisRun) -> list[AuthorizedElement]:
    required = {
        action.target_element_id
        for method in methods
        for action in method.actions
        if action.target_element_id is not None
    }
    element_by_id = {item.id: item for item in run.request.elements}
    return [element_by_id[element_id] for element_id in sorted(required)]


def _method(proposal: PomProposal, method_id: str) -> ProposedMethod:
    return next(item for item in proposal.methods if item.id == method_id)


def _element_attribute(element_id: str) -> str:
    return _snake_case(re.sub(r"^el_", "", element_id))


def _component_attribute(component_source_id: str) -> str:
    return _snake_case(re.sub(r"^cmp_", "", component_source_id))


def _snake_case(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9]+", "_", value).strip("_")
    first = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", cleaned)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", first).lower()


def _safe_docstring(value: str) -> str:
    return value.replace('"""', "'''").strip()


def _normalize_new_file(source: str) -> str:
    return source.replace("\r\n", "\n").rstrip() + "\n"


def _append_snippet(source: str, before_text: str, newline: str) -> str:
    normalized = source.replace("\r\n", "\n").rstrip("\n").replace("\n", newline)
    separator = newline * (1 if before_text.endswith(("\n", "\r")) else 2)
    return f"{separator}{normalized}{newline}"


def _validate_generated_python(source: str, operation: AdaptationOperation) -> None:
    try:
        tree = ast.parse(source, filename=operation.target_path)
    except SyntaxError as exc:
        raise ValueError(f"generated Python is invalid for {operation.target_path}") from exc
    _validate_safe_ast(tree, operation.target_path)
    symbol = next(
        (
            node
            for node in tree.body
            if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == operation.symbol_name
        ),
        None,
    )
    if symbol is None:
        raise ValueError(
            f"generated source does not define planned symbol {operation.symbol_name}"
        )
    if operation.target_kind in {AdaptationTargetKind.PAGE, AdaptationTargetKind.COMPONENT}:
        if not isinstance(symbol, ast.ClassDef):
            raise ValueError("page and component operations must generate classes")
    else:
        if not isinstance(symbol, (ast.FunctionDef, ast.AsyncFunctionDef)):
            raise ValueError("fixture and test operations must generate functions")
    if operation.target_kind is AdaptationTargetKind.FIXTURE:
        decorator_names = {_ast_name(item) for item in symbol.decorator_list}
        if "fixture" not in decorator_names:
            raise ValueError("generated fixture function requires pytest.fixture")
    if operation.target_kind is AdaptationTargetKind.TEST:
        if not operation.symbol_name.startswith("test_"):
            raise ValueError("generated test function must start with test_")
        if not any(isinstance(node, ast.Assert) for node in ast.walk(symbol)):
            raise ValueError("generated test must contain a test-owned assertion")


def _validate_combined_python(source: str, path: str) -> None:
    try:
        ast.parse(source, filename=path)
    except SyntaxError as exc:
        raise ValueError(f"generated append would make Python invalid: {path}") from exc


def _validate_safe_ast(tree: ast.AST, path: str) -> None:
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".", 1)[0] in _FORBIDDEN_IMPORTS:
                    raise ValueError(f"generated source imports forbidden module in {path}: {alias.name}")
        elif isinstance(node, ast.ImportFrom) and node.module:
            if node.module.split(".", 1)[0] in _FORBIDDEN_IMPORTS:
                raise ValueError(f"generated source imports forbidden module in {path}: {node.module}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            name = node.func.id
            if name in _FORBIDDEN_CALLS:
                raise ValueError(f"generated source calls forbidden function in {path}: {name}")


def _ast_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None
