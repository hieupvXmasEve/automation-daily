# Code Standards

## Principles

- Keep modules small and single-purpose
- Prefer standard library before new dependencies
- Fail early on invalid input
- Keep parsing assumptions explicit

## Python Rules

- Use type hints
- Use dataclasses for normalized records
- Avoid side effects during import
- Keep CLI output concise

## Testing Rules

- Prefer integration-style tests for real sample files
- Assert counts and key fields, not only command exit status

## Export Rules

- CSV must use UTF-8 BOM
- Excel sheet names stay stable
- PDF remains summary-first, not visual label cloning
