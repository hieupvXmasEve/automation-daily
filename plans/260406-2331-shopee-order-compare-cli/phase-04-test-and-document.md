# Phase 04: Test And Document

## Context Links

- [Plan Overview](./plan.md)

## Overview

Priority: Medium
Status: Completed
Goal: validate the workflow with sample files and document setup/usage.

## Key Insights

- `pytest` is not installed; use `unittest`.
- Sample files are enough for meaningful integration checks.

## Requirements

- Add automated tests
- Verify CLI output files exist and are non-empty
- Write concise project docs under `docs/`

## Architecture

- `tests/test_compare.py` for parser and CLI integration
- `docs/README.md` for setup and usage
- Evergreen docs for architecture and standards

## Related Code Files

- Create: `tests/test_compare.py`
- Create: `docs/README.md`
- Create: `docs/codebase-summary.md`
- Create: `docs/project-overview-pdr.md`
- Create: `docs/code-standards.md`
- Create: `docs/system-architecture.md`
- Create: `docs/project-roadmap.md`

## Implementation Steps

1. Add tests around parser counts and exporter outputs
2. Run `unittest`
3. Write concise docs
4. Update plan status

## Todo List

- [x] Tests added
- [x] Tests passing
- [x] Docs written
- [x] Plan marked complete

## Success Criteria

- End-to-end run works on sample files
- Docs cover install, usage, output format, limitations

## Risk Assessment

- Future Shopee format changes may break tests
- Mitigation: document parser assumptions

## Security Considerations

- Sample files may contain personal data; docs should avoid echoing raw values

## Next Steps

- Final report and optional git commit
