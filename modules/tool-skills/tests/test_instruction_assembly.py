"""v1 context.instructions assembly integration for the skills catalog."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, cast

import pytest

from amplifier_module_tool_skills import mount
from amplifier_module_tool_skills.discovery import SkillMetadata
from amplifier_module_tool_skills.hooks import SkillsVisibilityHook


class _Lease:
    def __init__(self, assembly: "_Assembly") -> None:
        self._assembly = assembly
        self.closed = False

    @property
    def route(self) -> str:
        return self._assembly.route

    def close(self) -> None:
        self.closed = True


class _Assembly:
    def __init__(self) -> None:
        self.route = "pending"
        self.sources: list[tuple[str, Any]] = []
        self.lease = _Lease(self)

    def register(self, source_id: str, callback: Any) -> _Lease:
        self.sources.append((source_id, callback))
        return self.lease


class _Context:
    def __init__(self) -> None:
        async def base() -> str:
            return "BASE"

        self._system_prompt_factory = base

    async def set_system_prompt_factory(self, factory: Any) -> None:
        self._system_prompt_factory = factory


class _CurrentCatalog:
    """A production-shaped effective-catalog seam whose current value can change."""

    def __init__(self, current: dict[str, Any]) -> None:
        self.current = current

    def get_effective_skills(self) -> dict[str, Any]:
        return self.current


class _BrokenMetadata:
    """Metadata that proves refresh errors never reach the v1 snapshot."""

    disable_model_invocation = False
    context = None
    visibility = None

    @property
    def description(self) -> str:
        raise ValueError("unfiltered catalog failure detail")


class _Coordinator:
    def __init__(self, assembly: _Assembly, context: _Context | None = None) -> None:
        self.assembly = assembly
        self.context = context
        self.capabilities: dict[str, Any] = {}
        self.config: dict[str, Any] = {}
        self.hooks = _Hooks()
        self.mounted: dict[str, Any] = {}

    def get(self, name: str) -> Any:
        return self.context if name == "context" else None

    def get_capability(self, name: str) -> Any:
        if name == "context.instructions.v1":
            return self.assembly
        return self.capabilities.get(name)

    def register_capability(self, name: str, value: Any) -> None:
        self.capabilities[name] = value

    async def mount(self, _category: str, tool: Any, name: str) -> None:
        self.mounted[name] = tool


class _Hooks:
    def __init__(self) -> None:
        self.registered: list[dict[str, Any]] = []

    def register(self, event: str, handler: Any, priority: int = 10, name: str | None = None):
        self.registered.append(
            {"event": event, "handler": handler, "priority": priority, "name": name}
        )

        def unregister() -> None:
            return None

        return unregister

    async def emit(self, _event: str, _data: dict[str, Any]) -> None:
        return None


def _coordinator_arg(coordinator: _Coordinator) -> Any:
    """Keep deliberately duck-typed v1 seam doubles out of RustCoordinator typing."""
    return cast(Any, coordinator)


@pytest.fixture
def catalog() -> dict[str, SkillMetadata]:
    return {
        "catalog-skill": SkillMetadata(
            name="catalog-skill",
            description="Visible only as catalog metadata",
            path=Path("/skills/catalog-skill/SKILL.md"),
            source="/skills",
        )
    }


@pytest.mark.asyncio
async def test_pending_v1_legacy_transition_uses_one_current_catalog(catalog) -> None:
    """A pre-v1 legacy wrapper drops only its own block during a v1 request."""
    assembly = _Assembly()
    context = _Context()
    hook = SkillsVisibilityHook(
        catalog,
        {"placement": "prefix"},
        coordinator=_coordinator_arg(_Coordinator(assembly, context)),
    )
    lease = hook.register_instruction_source()
    assert lease is assembly.lease
    assert [source_id for source_id, _callback in assembly.sources] == ["skills-visibility"]

    # Request 1: mount-time route is pending, so pre-v1 prefix behavior remains.
    await hook.on_provider_request("provider:request", {})
    pending_prompt = await context._system_prompt_factory()
    assert pending_prompt.count("hooks-skills-visibility") == 1
    source_callback = assembly.sources[0][1]
    pending_snapshot = await asyncio.to_thread(source_callback, {"request_id": "pending"})
    assert pending_snapshot == [
        {
            "key": "catalog",
            "content": hook._prefix_rendered,
            "placement": "head",
        }
    ]

    # Request 2: the legacy factory was installed earlier, but v1 owns the
    # single head copy.  The worker-thread callback returns the saved render.
    assembly.route = "v1"
    await hook.on_provider_request("provider:request", {})
    assert await context._system_prompt_factory() == "BASE"
    v1_snapshot = await asyncio.to_thread(source_callback, {"request_id": "v1"})
    assert len(v1_snapshot) == 1
    assert "catalog-skill" in v1_snapshot[0]["content"]

    # Request 3: legacy routing resumes with its original single prefix block.
    assembly.route = "legacy"
    await hook.on_provider_request("provider:request", {})
    legacy_prompt = await context._system_prompt_factory()
    assert legacy_prompt.count("hooks-skills-visibility") == 1
    assert "catalog-skill" in legacy_prompt


@pytest.mark.asyncio
async def test_v1_snapshot_is_byte_stable_until_catalog_changes(catalog) -> None:
    """The worker source returns the same head bytes until normal refresh sees a change."""
    assembly = _Assembly()
    assembly.route = "v1"
    hook = SkillsVisibilityHook(
        catalog,
        {},
        coordinator=_coordinator_arg(_Coordinator(assembly)),
    )
    hook.register_instruction_source()
    source_callback = assembly.sources[0][1]

    # Before the normal hook has rendered a catalog, v1 contributes nothing.
    assert await asyncio.to_thread(source_callback, {"request_id": "before"}) == []
    await hook.on_provider_request("provider:request", {})
    first = await asyncio.to_thread(source_callback, {"request_id": "one"})
    await hook.on_provider_request("provider:request", {})
    second = await asyncio.to_thread(source_callback, {"request_id": "two"})
    assert first == second
    assert first[0]["content"] is hook._prefix_rendered

    catalog["new-skill"] = SkillMetadata(
        name="new-skill",
        description="A real catalog change",
        path=Path("/skills/new-skill/SKILL.md"),
        source="/skills",
    )
    await hook.on_provider_request("provider:request", {})
    changed = await asyncio.to_thread(source_callback, {"request_id": "three"})
    assert changed != first
    assert "new-skill" in changed[0]["content"]


@pytest.mark.asyncio
async def test_v1_snapshot_fails_closed_after_refresh_error_then_recovers() -> None:
    """A caught hook error cannot let v1 reuse a stale catalog snapshot."""
    assembly = _Assembly()
    assembly.route = "v1"
    catalog_a = {
        "catalog-a": SkillMetadata(
            name="catalog-a",
            description="Catalog A",
            path=Path("/skills/catalog-a/SKILL.md"),
            source="/skills-a",
        )
    }
    current_catalog = _CurrentCatalog(catalog_a)
    hook = SkillsVisibilityHook(
        catalog_a,
        {},
        coordinator=_coordinator_arg(_Coordinator(assembly)),
        tool=current_catalog,
    )
    hook.register_instruction_source()
    source_callback = assembly.sources[0][1]

    await hook.on_provider_request("provider:request", {})
    snapshot_a = await asyncio.to_thread(source_callback, {"request_id": "a"})
    assert "catalog-a" in snapshot_a[0]["content"]

    current_catalog.current = {"broken": _BrokenMetadata()}
    try:
        await hook.on_provider_request("provider:request", {})
    except ValueError as exc:
        assert str(exc) == "unfiltered catalog failure detail"
    else:
        pytest.fail("the simulated catalog refresh must fail")

    assert hook._prefix_rendered == ""
    with pytest.raises(RuntimeError, match="Current skills catalog refresh failed") as error:
        await asyncio.to_thread(source_callback, {"request_id": "failed"})
    assert "unfiltered catalog failure detail" not in str(error.value)

    current_catalog.current = {
        "catalog-b": SkillMetadata(
            name="catalog-b",
            description="Catalog B",
            path=Path("/skills/catalog-b/SKILL.md"),
            source="/skills-b",
        )
    }
    await hook.on_provider_request("provider:request", {})
    snapshot_b = await asyncio.to_thread(source_callback, {"request_id": "b"})
    assert "catalog-b" in snapshot_b[0]["content"]
    assert "catalog-a" not in snapshot_b[0]["content"]
    assert "unfiltered catalog failure detail" not in snapshot_b[0]["content"]

    current_catalog.current = {}
    await hook.on_provider_request("provider:request", {})
    assert await asyncio.to_thread(source_callback, {"request_id": "empty"}) == []


@pytest.mark.asyncio
async def test_fresh_mount_registers_and_cleanup_closes_v1_source(tmp_path) -> None:
    """A new mount publishes its optional source before any request and closes it."""
    assembly = _Assembly()
    coordinator = _Coordinator(assembly)
    skill_dir = tmp_path / "skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(
        "---\nname: catalog-skill\ndescription: Test catalog\n---\n# Test\n"
    )

    cleanup = await mount(_coordinator_arg(coordinator), {"skills_dir": str(tmp_path)})

    assert [source_id for source_id, _callback in assembly.sources] == ["skills-visibility"]
    assert assembly.lease.closed is False
    assert cleanup is not None
    await cleanup()
    assert assembly.lease.closed is True