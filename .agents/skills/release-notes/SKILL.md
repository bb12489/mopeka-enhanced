---
name: release-notes
description: Cut a new release for the mopeka-enhanced Home Assistant integration — write CHANGELOG.md entries in the project's established style, bump the manifest version, and tag/push the release. Use when asked to "cut a release", "tag a new version", "write release notes", or "update the changelog" for this repo.
---

# Release Notes for mopeka-enhanced

This repo auto-generates GitHub Releases from `CHANGELOG.md` when a `vX.Y.Z` tag is
pushed (see `.github/workflows/release.yml` / `create-tag.yml`). The release body is
extracted verbatim from the `## [X.Y.Z]` section of `CHANGELOG.md` via an `awk` block
that matches the section header up to the next `## [`. **This means the changelog entry
IS the release note** — write it exactly as you want it to appear on GitHub.

## Style rules (match existing entries in CHANGELOG.md exactly)

- **Brief bullet points only.** No prose paragraphs, no per-file diff descriptions, no
  rationale essays. One line per change. Compress verbose session/commit descriptions
  down to the user-facing takeaway.
- **Group bullets under `###` category headers**, using the emoji already established in
  this file. Only include categories that actually apply this release:
  - `### 🚨 Action Required` (put this section **first**, above all others, when a change
    needs manual user action — e.g. reconfiguring an entry — for the fix/feature below to
    take effect. Bold the affected device/entity type and the action verb. Always state
    what happens if the user does nothing, and who is unaffected.)
  - `### 🎉 New Features!`
  - `### 🛠️Changed` (note: no space between the emoji and "Changed" — matches existing entries)
  - `### ✅ Tests`
  - `### ⚙️ CI`
  - `### 📚 Docs`
  - `### 🐛 Fixed` (used in older entries for bug fixes)
- Order categories roughly as above (Action Required, Features, Changed, Tests, CI, Docs,
  Fixed) but skip any that don't apply.
- **Check whether any change requires manual user action** (reconfiguring a config entry,
  renaming an entity that breaks existing automations, deleting/re-adding presets, etc.)
  before finalizing a release — don't rely on the original session/commit description to
  flag this; verify it yourself against what actually changed. If so, it must appear
  under `### 🚨 Action Required`. A past release (`0.2.5-Beta1`, ASME preset rewrite) needed
  this and it was only added ad hoc to the GitHub Release body, not to `CHANGELOG.md` —
  since `CHANGELOG.md` is now the verbatim source for release notes, this must always
  live there so it survives into the generated release automatically.
- Always include a `- Bumped integration version to \`X.Y.Z\`.` bullet under `### 🛠️Changed`.
- Reference PRs/contributors inline when relevant, e.g.
  `— thanks to [@user](https://github.com/user) for the contribution! (#12)`.
- Wrap code identifiers (file names, config keys, package names) in backticks.
- Version heading format: `## [X.Y.Z] - YYYY-MM-DD` (use the actual release date).

## Steps to cut a release

1. **Check for pending work across sessions/terminals first.** If other agent sessions
   in this repo have uncommitted changes, get those committed (and changelog-tracked)
   before starting the release — see the workflow used in past sessions of polling
   `orca terminal read`/`worktree ps` and committing centrally to avoid conflicts.
2. Read the current `[Unreleased]` (or most recent) section of `CHANGELOG.md` and the
   actual `git diff`/`git log` since the last tag to confirm what really shipped.
3. Rewrite/condense those entries into the brief bullet style above under
   `## [X.Y.Z] - YYYY-MM-DD` (get today's date with `date +%Y-%m-%d`), replacing the
   `[Unreleased]` heading.
4. Bump the version in `custom_components/mopeka/manifest.json` (`"version": "X.Y.Z"`).
5. `git fetch origin` and check `git status -sb` — if origin/main has moved, merge it in
   and resolve conflicts before proceeding (don't tag a branch that isn't in sync).
6. Run the test/lint suite to confirm nothing broke:
   ```
   python -m ruff check custom_components tests
   python -m pytest -q -p no:homeassistant tests
   ```
7. Commit: `git commit -m "Release vX.Y.Z"` (stage only `CHANGELOG.md` and
   `manifest.json` unless other release-relevant files changed).
8. Tag and push:
   ```
   git tag -a vX.Y.Z -m "Release vX.Y.Z"
   git push origin main
   git push origin vX.Y.Z
   ```
9. Verify the automated release workflow succeeded and the notes rendered correctly:
   ```
   gh run list --workflow=release.yml --limit 3
   gh release view vX.Y.Z
   ```

## Reference: what a good entry looks like

```markdown
## [0.2.7] - 2026-07-25

### 🛠️Changed

- Removed the "Tank level (kilograms)" / "Tank level (liters)" custom sensor name overrides so the volume sensor falls back to its default entity name.
- Added debug logging throughout integration setup/unload/reload, config flow discovery, and the empty-tank quality latch transitions to aid troubleshooting.
- Bumped integration version to `0.2.7`.

### ✅ Tests

- Added real end-to-end integration tests (`tests_integration/`) against a live Home Assistant instance, alongside the existing stub-based unit tests.

### ⚙️ CI

- Skip the `quality` job on scheduled runs.
- Added `mypy` static type checking to CI.

### 📚 Docs

- Added a "Code quality" section to the README.
```
