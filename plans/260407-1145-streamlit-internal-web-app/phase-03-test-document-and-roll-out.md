# Phase 03: Test, Document, And Roll Out

## Context Links

- [Docs README](../../docs/README.md)
- [Project Roadmap](../../docs/project-roadmap.md)
- [Codebase Summary](../../docs/codebase-summary.md)
- [System Architecture](../../docs/system-architecture.md)
- [Phase 01](./phase-01-extract-shared-workflows.md)
- [Phase 02](./phase-02-build-streamlit-internal-web-app.md)

## Overview

Priority: Medium
Status: Completed
Goal: lock in shared-orchestration coverage, preserve CLI regression checks, and update docs/roadmap for the new internal web entrypoint.

## Key Insights

- The user explicitly wants tests on the shared orchestration layer, not only CLI smoke coverage.
- Existing tests already protect core compare and extract flows; they should remain as backward-compatibility guards.
- Current docs describe a CLI-only tool, so architecture and setup docs must be updated after the Streamlit entrypoint exists.

## Requirements

- Add automated tests for shared compare and extract workflows using real fixtures and temp output dirs.
- Keep existing CLI tests passing to prove CLI preservation.
- Update docs to cover setup, run commands, architecture, and roadmap impact for the internal Streamlit app.
- Keep release scope internal; no deployment or auth work implied by this plan.

## Architecture

Test matrix:
- Shared workflow tests: artifact creation, summary counts, selected-format behavior, extract-item export behavior
- CLI regression tests: existing `main.py compare` and `main.py extract-items` flows still pass
- Manual web smoke: upload fixtures, run both modes, verify downloads open

Docs impact:
- `docs/README.md`: add Streamlit setup/run flow
- `docs/codebase-summary.md`: add shared workflow and Streamlit entrypoint
- `docs/system-architecture.md`: add CLI + Streamlit -> workflow -> core modules flow
- `docs/project-roadmap.md`: move internal web app from planned to done/next as appropriate

## File Ownership

- Owns: `tests/test_workflows.py`
- Owns: `docs/README.md`
- Owns: `docs/README.vi.md`
- Owns: `docs/codebase-summary.md`
- Owns: `docs/design-guidelines.md`
- Owns: `docs/project-overview-pdr.md`
- Owns: `docs/system-architecture.md`
- Owns: `docs/project-roadmap.md`
- Owns: `docs/tech-stack.md`

## Related Code Files

- Create: `tests/test_workflows.py`
- Modify: `docs/README.md`
- Modify: `docs/README.vi.md`
- Modify: `docs/codebase-summary.md`
- Modify: `docs/design-guidelines.md`
- Modify: `docs/project-overview-pdr.md`
- Modify: `docs/system-architecture.md`
- Modify: `docs/project-roadmap.md`
- Modify: `docs/tech-stack.md`

## Implementation Steps

1. Add shared-workflow tests with real fixtures and temp output assertions.
2. Run `python -m unittest discover -s tests -v` and fix regressions before doc updates are considered done.
3. Update evergreen docs to describe the additive Streamlit architecture and usage.
4. Mark roadmap progress and close the plan when tests and docs are both complete.

## Todo List

- [x] Add shared workflow tests
- [x] Keep CLI regression tests green
- [x] Run full unittest suite
- [x] Update docs and roadmap

## Success Criteria

- `python -m unittest discover -s tests -v` passes
- Shared compare workflow test proves CSV/XLSX/PDF artifact creation and summary shape
- Shared extract workflow test proves CSV/XLSX item export behavior
- Docs show both `python main.py ...` and `streamlit run streamlit_app.py`

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Temp-dir assertions make tests brittle | Medium | Medium | Assert file existence and key contents, not exact timestamps |
| Docs drift from actual commands | Medium | Medium | Update docs only after final command names and entrypoint settle |
| Manual web smoke is skipped | Low | High | Make smoke-check part of phase done criteria, not optional |

## Security Considerations

- Avoid adding real personal data to docs or test assertions
- Keep tests fixture-driven and local only
- Do not weaken existing fail-fast behavior for bad inputs

## Rollback Plan

- Revert new workflow tests and doc changes if the UI work is backed out
- Keep CLI-only docs as the fallback baseline
- No persistent data cleanup required beyond temp artifacts

## Next Steps

- Result: done
