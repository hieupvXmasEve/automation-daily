# Phase 01: Project Setup

## Context Links

- [Tech Stack](../../docs/tech-stack.md)
- [CLI Design Guidelines](../../docs/design-guidelines.md)

## Overview

Priority: High
Status: Completed
Goal: scaffold the repo, pin Python with `pyenv`, define package layout, and prepare sample-data-driven execution.

## Key Insights

- Repo is effectively empty besides sample Shopee files.
- `pyenv 2.5.4` is installed and `3.11.10` is available locally.
- Network-free setup matters; avoid dependency churn.

## Requirements

- Add `.python-version`
- Add dependency manifest
- Add package directories and entrypoint
- Add `.gitignore`

## Architecture

- Root `main.py` for simple terminal invocation
- Package `shopee_compare/` for implementation modules
- `tests/` for integration-style checks with sample data

## Related Code Files

- Create: `.python-version`
- Create: `.gitignore`
- Create: `requirements.txt`
- Create: `main.py`
- Create: `shopee_compare/`

## Implementation Steps

1. Pin Python runtime to `3.11.10`
2. Create package skeleton and CLI entrypoint
3. Add reproducible dependency manifest
4. Document setup/run commands

## Todo List

- [x] Pin Python
- [x] Add skeleton files
- [x] Verify `python main.py --help`

## Success Criteria

- Repo has runnable package skeleton
- Setup instructions are explicit

## Risk Assessment

- Hidden global-package reliance can make setup brittle
- Mitigation: keep requirements minimal and explicit

## Security Considerations

- No secrets
- Local file processing only

## Next Steps

- Proceed to parser implementation
