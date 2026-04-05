#!/usr/bin/env python3
"""Validate a tank-preset pull request against the PR submission guidelines.

Compares the PR branch against its base branch, finds any new TankSize enum
entries added to const.py, and verifies that every required code change listed
in the PR template has been made.

Exit codes:
  0 – all checks passed (or no new tank presets were detected)
  1 – one or more guideline checks failed

Outputs written to /tmp/:
  validation_report.md  – Markdown summary suitable for a PR comment
  validation_passed.txt – "true" or "false"
"""

import ast
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# Paths relative to the repository root
CONST_PY = "custom_components/mopeka/const.py"
STRINGS_JSON = "custom_components/mopeka/strings.json"
TRANSLATIONS_EN = "custom_components/mopeka/translations/en.json"
CHANGELOG_MD = "CHANGELOG.md"
MANIFEST_JSON = "custom_components/mopeka/manifest.json"
CONFIG_FLOW_PY = "custom_components/mopeka/config_flow.py"

# HTML comment marker so we can find and update the bot comment on re-push
COMMENT_MARKER = "<!-- tank-preset-validation -->"

# Output directory for files read by the workflow step that posts the comment
_OUT_DIR = Path("/tmp")


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, cwd=str(REPO_ROOT)
    )
    return result.stdout.strip()


def _base_ref() -> str:
    return os.environ.get("GITHUB_BASE_REF", "main")


def _fetch_base() -> None:
    _git("fetch", "origin", _base_ref())


def _changed_files() -> set[str]:
    out = _git("diff", "--name-only", f"origin/{_base_ref()}...HEAD")
    return {f for f in out.splitlines() if f}


def _base_content(rel_path: str) -> str:
    """Return the content of *rel_path* on the base branch (empty string on error)."""
    return _git("show", f"origin/{_base_ref()}:{rel_path}")


def _diff_added_lines(rel_path: str) -> list[str]:
    """Return the lines *added* (not deleted) for *rel_path* in this PR."""
    diff = _git("diff", f"origin/{_base_ref()}...HEAD", "--", rel_path)
    return [
        line[1:]  # strip leading '+'
        for line in diff.splitlines()
        if line.startswith("+") and not line.startswith("+++")
    ]


# ---------------------------------------------------------------------------
# const.py parser (uses ast – no import of the module itself)
# ---------------------------------------------------------------------------

def _tanksize_refs(node: ast.AST) -> set[str]:
    """Return TankSize attribute names referenced anywhere inside *node*."""
    refs: set[str] = set()
    for n in ast.walk(node):
        if (
            isinstance(n, ast.Attribute)
            and isinstance(n.value, ast.Name)
            and n.value.id == "TankSize"
        ):
            refs.add(n.attr)
    return refs


def _parse_const_py(source: str) -> dict:
    """Parse const.py source and return sets/dicts of tank data."""
    tree = ast.parse(source)
    data: dict = {
        "tank_size_enum": {},       # attr_name -> string_value
        "propane_tank_sizes": set(),
        "ibc_tank_sizes": set(),
        "tank_size_ranges": set(),
        "ibc_tank_size_ranges": set(),
        "horizontal_tank_sizes": set(),
        "tank_size_capacities": set(),
    }

    for node in ast.walk(tree):
        # ── TankSize enum members ──────────────────────────────────────────
        if isinstance(node, ast.ClassDef) and node.name == "TankSize":
            for item in node.body:
                if isinstance(item, ast.Assign):
                    for tgt in item.targets:
                        if isinstance(tgt, ast.Name) and isinstance(
                            item.value, ast.Constant
                        ):
                            data["tank_size_enum"][tgt.id] = item.value.value

        # ── Module-level annotated assignments  (Final[…] = …) ────────────
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            var = node.target.id
            val = node.value
            if val is None:
                continue

            if var == "PROPANE_TANK_SIZES":
                data["propane_tank_sizes"] = _tanksize_refs(val)

            elif var == "IBC_TANK_SIZES":
                data["ibc_tank_sizes"] = _tanksize_refs(val)

            elif var == "TANK_SIZE_RANGES":
                if isinstance(val, ast.Dict):
                    for k in val.keys:
                        data["tank_size_ranges"].update(_tanksize_refs(k))

            elif var == "IBC_TANK_SIZE_RANGES":
                if isinstance(val, ast.Dict):
                    for k in val.keys:
                        data["ibc_tank_size_ranges"].update(_tanksize_refs(k))

            elif var == "HORIZONTAL_TANK_SIZES":
                data["horizontal_tank_sizes"] = _tanksize_refs(val)

            elif var == "TANK_SIZE_CAPACITIES":
                if isinstance(val, ast.Dict):
                    for k in val.keys:
                        data["tank_size_capacities"].update(_tanksize_refs(k))

    return data


# ---------------------------------------------------------------------------
# strings.json / translations/en.json helpers
# ---------------------------------------------------------------------------

def _load_json(rel_path: str) -> dict:
    try:
        return json.loads((REPO_ROOT / rel_path).read_text())
    except Exception:
        return {}


def _selector_keys(data: dict, selector_name: str) -> set[str]:
    try:
        return set(data["selector"][selector_name]["options"].keys())
    except (KeyError, TypeError):
        return set()


def _state_keys(data: dict) -> set[str]:
    try:
        return set(data["entity"]["sensor"]["propane_preset"]["state"].keys())
    except (KeyError, TypeError):
        return set()


# ---------------------------------------------------------------------------
# Validation logic
# ---------------------------------------------------------------------------

Check = tuple[str, bool, str]   # (description, passed, detail_on_failure)


def _validate() -> list[Check]:
    checks: list[Check] = []

    def chk(description: str, passed: bool, detail: str = "") -> None:
        checks.append((description, passed, detail))

    # ── Fetch and diff ──────────────────────────────────────────────────────
    _fetch_base()
    changed = _changed_files()

    # ── Parse head and base const.py ────────────────────────────────────────
    try:
        head_source = (REPO_ROOT / CONST_PY).read_text()
        head = _parse_const_py(head_source)
    except SyntaxError as exc:
        chk(
            f"`{CONST_PY}` parses without errors",
            False,
            f"Python syntax error: {exc}",
        )
        return checks

    base_source = _base_content(CONST_PY)
    base = _parse_const_py(base_source) if base_source else {"tank_size_enum": {}}

    # ── Find new TankSize entries ────────────────────────────────────────────
    new_keys: dict[str, str] = {
        attr: val
        for attr, val in head["tank_size_enum"].items()
        if attr not in base["tank_size_enum"]
    }

    if not new_keys:
        # Not a tank-preset PR (or const.py was edited for another reason).
        # Return without checks so the workflow passes silently.
        return []

    # ── Per-preset checks ───────────────────────────────────────────────────
    strings = _load_json(STRINGS_JSON)
    en = _load_json(TRANSLATIONS_EN)

    for attr, val in new_keys.items():
        label = f"`TankSize.{attr}` (`\"{val}\"`)"

        # 1. In PROPANE_TANK_SIZES or IBC_TANK_SIZES
        in_propane = attr in head["propane_tank_sizes"]
        in_ibc = attr in head["ibc_tank_sizes"]
        chk(
            f"{label} — in `PROPANE_TANK_SIZES` or `IBC_TANK_SIZES`",
            in_propane or in_ibc,
            "Add it to `PROPANE_TANK_SIZES` (propane preset) or `IBC_TANK_SIZES` "
            "(IBC / non-propane preset) in `const.py`.",
        )

        # 2. In TANK_SIZE_RANGES or IBC_TANK_SIZE_RANGES
        in_propane_ranges = attr in head["tank_size_ranges"]
        in_ibc_ranges = attr in head["ibc_tank_size_ranges"]
        chk(
            f"{label} — in `TANK_SIZE_RANGES` or `IBC_TANK_SIZE_RANGES`",
            in_propane_ranges or in_ibc_ranges,
            "Add `(empty_mm, full_mm)` for this preset to the appropriate ranges "
            "dict in `const.py`.",
        )

        # 3. Ranges-dict / sizes-list consistency
        if in_propane and in_ibc_ranges and not in_propane_ranges:
            chk(
                f"{label} — propane preset uses `TANK_SIZE_RANGES` (not IBC ranges)",
                False,
                "Propane presets must go in `TANK_SIZE_RANGES`, not `IBC_TANK_SIZE_RANGES`.",
            )
        if in_ibc and in_propane_ranges and not in_ibc_ranges:
            chk(
                f"{label} — IBC preset uses `IBC_TANK_SIZE_RANGES` (not propane ranges)",
                False,
                "IBC presets must go in `IBC_TANK_SIZE_RANGES`, not `TANK_SIZE_RANGES`.",
            )

        # 4. In TANK_SIZE_CAPACITIES
        chk(
            f"{label} — in `TANK_SIZE_CAPACITIES`",
            attr in head["tank_size_capacities"],
            "Add the gallon capacity for this preset to `TANK_SIZE_CAPACITIES` in `const.py`.",
        )

        # 5. Horizontal consistency (key string ends with "_h")
        is_horiz_key = val.endswith("_h")
        in_horiz = attr in head["horizontal_tank_sizes"]
        if is_horiz_key and not in_horiz:
            chk(
                f"{label} — horizontal preset in `HORIZONTAL_TANK_SIZES`",
                False,
                "The key ends with `_h` (horizontal) but was not added to "
                "`HORIZONTAL_TANK_SIZES` in `const.py`.  Add it so the integration "
                "uses circular-segment geometry for fill %.",
            )
        elif in_horiz and not is_horiz_key:
            chk(
                f"{label} — non-horizontal key not in `HORIZONTAL_TANK_SIZES`",
                False,
                "The key does not end with `_h` but was added to `HORIZONTAL_TANK_SIZES`. "
                "Only horizontal presets belong there.",
            )

        # 6 & 7. strings.json — selector + diagnostic state
        selector = "ibc_tank_size" if in_ibc else "tank_size"
        str_selector = _selector_keys(strings, selector)
        str_state = _state_keys(strings)

        chk(
            f"{label} — label in `strings.json` → `selector.{selector}.options`",
            val in str_selector,
            f'Add `"{val}": "<display label>"` to `selector.{selector}.options` '
            f"in `strings.json`.",
        )
        chk(
            f"{label} — label in `strings.json` → `entity.sensor.propane_preset.state`",
            val in str_state,
            f'Add `"{val}": "<display label>"` to `entity.sensor.propane_preset.state` '
            f"in `strings.json`.",
        )

        # 8 & 9. translations/en.json — same two locations
        en_selector = _selector_keys(en, selector)
        en_state = _state_keys(en)

        chk(
            f"{label} — label in `translations/en.json` → `selector.{selector}.options`",
            val in en_selector,
            f"Mirror the label in `selector.{selector}.options` "
            f"in `translations/en.json`.",
        )
        chk(
            f"{label} — label in `translations/en.json` → `entity.sensor.propane_preset.state`",
            val in en_state,
            f"Mirror the label in `entity.sensor.propane_preset.state` "
            f"in `translations/en.json`.",
        )

    # ── CHANGELOG updated ───────────────────────────────────────────────────
    chk(
        "`CHANGELOG.md` updated",
        CHANGELOG_MD in changed,
        "Add a release-note entry in `CHANGELOG.md` describing the new preset(s) "
        "and their measurement source.",
    )

    # ── manifest.json version NOT bumped ────────────────────────────────────
    try:
        base_ver = json.loads(_base_content(MANIFEST_JSON)).get("version")
        head_ver = json.loads((REPO_ROOT / MANIFEST_JSON).read_text()).get("version")
        ver_ok = base_ver == head_ver
    except Exception:
        ver_ok = True  # Can't determine — treat as passing

    chk(
        "`manifest.json` version NOT bumped",
        ver_ok,
        "Do **not** bump the version in `manifest.json`. "
        "The maintainer handles version bumps at release time.",
    )

    # ── config_flow.py NOT modified ─────────────────────────────────────────
    chk(
        "`config_flow.py` NOT modified",
        CONFIG_FLOW_PY not in changed,
        "Do **not** modify `config_flow.py`. The selector lists are driven "
        "dynamically from `PROPANE_TANK_SIZES` / `IBC_TANK_SIZES`; no flow "
        "changes are needed for standard preset additions.",
    )

    return checks


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def _build_report(checks: list[Check], new_key_count: int) -> str:
    passed_all = all(p for _, p, _ in checks)

    lines = [COMMENT_MARKER, ""]

    if passed_all:
        lines += [
            "## ✅ Tank Preset PR — All Checks Passed",
            "",
            "> 🎉 All automated guideline checks passed. "
            f"**{new_key_count} new preset(s) validated.** "
            "This PR is ready for maintainer review.",
            "",
        ]
    else:
        fail_count = sum(1 for _, p, _ in checks if not p)
        lines += [
            "## ❌ Tank Preset PR — Validation Issues Found",
            "",
            f"> {fail_count} check(s) did not pass. "
            "Please review the items below, fix them, and push again.",
            "",
        ]

    lines.append("### Checklist")
    lines.append("")
    for description, passed, detail in checks:
        icon = "✅" if passed else "❌"
        lines.append(f"- {icon} {description}")
        if not passed and detail:
            lines.append(f"  > {detail}")

    lines += [
        "",
        "---",
        "_Automated check — updates on every push to this PR. "
        "See [PR submission guidelines](.github/PULL_REQUEST_TEMPLATE.md) for details._",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    checks = _validate()

    if not checks:
        # No new tank presets found — not a tank-preset PR; exit silently.
        (_OUT_DIR / "validation_report.md").write_text("")
        (_OUT_DIR / "validation_passed.txt").write_text("skip")
        sys.exit(0)

    passed_all = all(p for _, p, _ in checks)

    # Count how many new TankSize entries triggered the run
    # (approximate: one entry adds 8 checks)
    report = _build_report(checks, new_key_count=max(1, len(checks) // 8))

    (_OUT_DIR / "validation_report.md").write_text(report)
    (_OUT_DIR / "validation_passed.txt").write_text("true" if passed_all else "false")

    print(report)
    sys.exit(0 if passed_all else 1)


if __name__ == "__main__":
    main()
