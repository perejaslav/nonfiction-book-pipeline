#!/usr/bin/env python3
"""
validate_manuscript.py — Pre-delivery validation for NFP manuscripts

Usage:
    python3 scripts/validate_manuscript.py [path/to/manuscript.md]

Runs 7 checks (adapted from Booksmith RU §8, проход 7):
  1. Orphaned footnotes — [^N] references without definitions
  2. Service tags — [FACT-CHECK], [TODO], [DRAFT], [UNVERIFIED]
  3. Empty sections — consecutive headings with no content between
  4. Chapter presence — all TOC entries exist in text
  5. Service comments — agent/debug markers
  6. Bibliography split — verified vs unverified sections
  7. Evidence gaps — high-risk items in evidence_gaps.md (if exists)

Returns: PASS or FAIL with details. Exit code 0 = pass, 1 = fail.
"""

import re
import sys
from pathlib import Path


def count_words(text: str) -> int:
    """Count Russian + Latin words in text."""
    cleaned = re.sub(r"[#*>|`\-]", " ", text)
    return len(re.findall(r"[\u0400-\u04FF\w]+", cleaned))


def check_orphaned_footnotes(text: str) -> list[str]:
    """Find [^N] references that have no matching definition."""
    refs = set(re.findall(r"\[\^(\d+)\]", text))
    defs = set(re.findall(r"^\[\^(\d+)\]:", text, re.MULTILINE))
    orphans = refs - defs
    if orphans:
        nums = ", ".join(sorted(orphans, key=int))
        return [f"Orphaned footnotes [^{n}]" for n in sorted(orphans, key=int)]
    return []


def check_service_tags(text: str) -> list[str]:
    """Find leftover service tags."""
    tags = ["FACT-CHECK", "TODO", "DRAFT", "UNVERIFIED"]
    issues = []
    for tag in tags:
        pattern = rf"\[{tag}\]"
        matches = re.findall(pattern, text)
        if matches:
            issues.append(f"[{tag}] found {len(matches)} time(s)")
    return issues


def check_empty_sections(text: str) -> list[str]:
    """Find sections with no content between consecutive headings."""
    lines = text.splitlines()
    issues = []
    for i in range(len(lines) - 1):
        if re.match(r"^#{1,3}\s+", lines[i].strip()):
            # Skip book title (first H1) — it's expected to be followed by TOC
            if i == 0 and lines[i].strip().startswith("# "):
                continue
            # Check if next non-empty line is also a heading
            for j in range(i + 1, min(i + 5, len(lines))):
                stripped = lines[j].strip()
                if stripped:
                    if re.match(r"^#{1,3}\s+", stripped):
                        # H2 followed by H3 is normal nesting (e.g. Библиография → Проверенные)
                        curr_prefix = lines[i].split()[0] if lines[i].split() else ""
                        next_prefix = stripped.split()[0] if stripped.split() else ""
                        curr_level = len(curr_prefix) - len(curr_prefix.lstrip("#"))
                        next_level = len(next_prefix) - len(next_prefix.lstrip("#"))
                        if next_level > curr_level:
                            break  # subsection — not empty
                        issues.append(
                            f"Empty section: L{i+1} '{lines[i].strip()[:60]}' "
                            f"→ L{j+1} '{stripped[:60]}'"
                        )
                    break
    return issues


def check_chapter_presence(text: str) -> list[str]:
    """Check that TOC entries match actual chapters in text."""
    # Extract TOC entries (lines after '## Содержание' or '## Оглавление')
    toc_section = re.search(
        r"^##\s+(?:Содержание|Оглавление)\s*\n(.*?)(?=\n##\s|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if not toc_section:
        return []  # No TOC found — skip check

    toc_text = toc_section.group(1)
    toc_chapters = re.findall(r"[-*]\s+(?:Глава\s+\d+[.\s:]*)?(.+)", toc_text)
    if not toc_chapters:
        return []

    # Collect all headings from the text body (after TOC)
    body_start = toc_section.end()
    body = text[body_start:]
    headings = re.findall(r"^#{1,2}\s+(.+)$", body, re.MULTILINE)
    # Normalize headings: strip numbers, dots, prefixes
    heading_texts = []
    for h in headings:
        # Remove "Глава N." prefix if present
        cleaned = re.sub(r"^Глава\s+\d+[.\s:]*", "", h).strip()
        heading_texts.append(cleaned.lower())

    issues = []
    for ch_name in toc_chapters:
        name = ch_name.strip().rstrip(".")
        if len(name) < 5:
            continue
        # Check if this TOC entry matches any heading (partial match)
        name_lower = name.lower()
        found = False
        for heading in heading_texts:
            # Match if TOC name is a substring of heading or vice versa
            if name_lower in heading or heading in name_lower:
                found = True
                break
            # Also check first 30 chars for fuzzy match
            if len(name_lower) > 10 and name_lower[:30] in heading:
                found = True
                break
        if not found:
            issues.append(f"TOC entry not found in text: '{name[:50]}'")
    return issues


def check_service_comments(text: str) -> list[str]:
    """Find agent/debug markers."""
    markers = [
        r"<!--\s*(agent|debug|internal|todo|fixme|hack)",
        r"^\s*//\s*(TODO|FIXME|HACK|XXX|AGENT)",
        r"\[AGENT-NOTE\]",
        r"\[INTERNAL\]",
        r"\[DEBUG\]",
    ]
    issues = []
    for pat in markers:
        matches = re.findall(pat, text, re.IGNORECASE | re.MULTILINE)
        if matches:
            issues.append(f"Service comment found: {pat} ({len(matches)}x)")
    return issues


def check_bibliography(text: str) -> list[str]:
    """Check that bibliography has verified/unverified split if present."""
    has_bib = bool(re.search(r"^##\s+Библиограф", text, re.MULTILINE))
    if not has_bib:
        has_bib = bool(re.search(r"^##\s+Bibliography", text, re.MULTILINE))
    if not has_bib:
        return []

    has_verified = bool(re.search(r"Проверенные\s+источники", text))
    has_unverified = bool(re.search(r"Требующие\s+верификации", text))

    issues = []
    if not has_verified:
        issues.append("Bibliography missing 'Проверенные источники' section")
    # Having no unverified section is fine (all sources verified)
    return issues


def check_evidence_gaps(project_dir: Path) -> list[str]:
    """Check evidence_gaps.md for high-risk items."""
    gaps_file = project_dir / "foundation" / "evidence_gaps.md"
    if not gaps_file.exists():
        return []

    text = gaps_file.read_text(encoding="utf-8")
    # Look for HIGH/ВЫСОКИЙ risk markers
    high_risk = re.findall(
        r"ВЫСОКИЙ|HIGH|🔴",
        text,
        re.IGNORECASE,
    )
    if high_risk:
        return [
            f"evidence_gaps.md contains {len(high_risk)} HIGH-risk item(s) "
            f"— must resolve before delivery"
        ]
    return []


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "manuscript.md"
    manuscript_path = Path(path)

    if not manuscript_path.exists():
        print(f"❌ File not found: {path}", file=sys.stderr)
        sys.exit(1)

    text = manuscript_path.read_text(encoding="utf-8")
    words = count_words(text)

    # Project dir is parent of manuscript (or cwd)
    project_dir = manuscript_path.parent

    all_issues: dict[str, list[str]] = {}

    checks = {
        "1. Orphaned footnotes":   check_orphaned_footnotes(text),
        "2. Service tags":         check_service_tags(text),
        "3. Empty sections":       check_empty_sections(text),
        "4. Chapter presence":     check_chapter_presence(text),
        "5. Service comments":     check_service_comments(text),
        "6. Bibliography":         check_bibliography(text),
        "7. Evidence gaps":        check_evidence_gaps(project_dir),
    }

    total_issues = 0
    for name, issues in checks.items():
        if issues:
            all_issues[name] = issues
            total_issues += len(issues)

    # --- Output ---
    print(f"📖 Manuscript: {manuscript_path}")
    print(f"📊 Words: {words:,}")
    print(f"📋 Checks: {len(checks)}\n")

    for name, issues in all_issues.items():
        print(f"⚠️  {name}:")
        for issue in issues:
            print(f"   • {issue}")
        print()

    if total_issues == 0:
        print("✅ PASS — All checks passed. Manuscript is ready for delivery.")
        sys.exit(0)
    else:
        print(f"❌ FAIL — {total_issues} issue(s) found. Fix before delivery.")
        sys.exit(1)


if __name__ == "__main__":
    main()
