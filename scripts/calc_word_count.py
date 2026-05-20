#!/usr/bin/env python3
"""
calc_word_count.py — Auto-calculate word count plan from structure.md

Usage:
    python3 scripts/calc_word_count.py [path/to/structure.md]

Parses structure.md, identifies chapter types and density,
applies baseline × multiplier formula, outputs word count plan.

Adapted from Booksmith RU §6 for NFP.
"""

import re
import sys
from pathlib import Path

# --- Baseline ranges (type → (min, max)) ---
BASELINES = {
    "intro":      (2000, 3500),
    "overview":   (3000, 4500),
    "research":   (4000, 6000),
    "practical":  (3500, 5000),
    "narrative":  (4000, 6000),
    "conclusion": (2000, 3500),
}

# --- Density multipliers ---
MULTIPLIERS = {
    "обзорная":          0.80,
    "survey":            0.80,
    "overview":          0.80,
    "практическая":      1.00,
    "practical":         1.00,
    "исследовательская": 1.20,
    "research":          1.20,
    "академическая":     1.30,
    "academic":          1.30,
    "повествовательная": 1.10,
    "narrative":         1.10,
}

# --- Keyword → type detection ---
TYPE_KEYWORDS = {
    "intro":      ["введение", "вводн", "prologue", "пролог", "opening"],
    "overview":   ["обзор", "вводн", "survey", "контекст", "context"],
    "research":   ["исследован", "research", "доказатель", "анализ", "источник",
                   "истори", "биограф", "археолог", "научн"],
    "practical":  ["практик", "метод", "упражнен", "применен", "кейс",
                   "руководств", "пошагов", "инструмент", "framework"],
    "narrative":  ["нарратив", "сюжет", "сцен", "истори", "хроник",
                   "повествован", "рассказ", "story"],
    "conclusion": ["заключен", "conclusion", "итог", "финал", "эпилог",
                   "epilogue", "резюме"],
}


def detect_chapter_type(title: str) -> str:
    """Detect chapter type from title keywords."""
    t = title.lower()
    # Check conclusion first (most specific)
    for kw in TYPE_KEYWORDS["conclusion"]:
        if kw in t:
            return "conclusion"
    # Check intro
    for kw in TYPE_KEYWORDS["intro"]:
        if kw in t:
            return "intro"
    # Score-based for the rest
    scores: dict[str, int] = {}
    for ctype, keywords in TYPE_KEYWORDS.items():
        if ctype in ("intro", "conclusion"):
            continue
        scores[ctype] = sum(1 for kw in keywords if kw in t)
    if scores:
        best = max(scores, key=scores.get)  # type: ignore[arg-type]
        if scores[best] > 0:
            return best
    return "overview"  # default fallback


def detect_density(title: str, type_hint: str) -> str:
    """Detect density from title or infer from type."""
    t = title.lower()
    density_keywords = {
        "исследовательская": ["исследован", "глубок", "подробн", "анализ"],
        "академическая":     ["академическ", "научн", "строг", "монограф"],
        "практическая":      ["практич", "пошагов", "упражнен", "метод"],
        "повествовательная": ["нарратив", "истори", "сюжет", "сцен"],
        "обзорная":          ["обзор", "вводн", "кратк", "survey"],
    }
    for density, keywords in density_keywords.items():
        if any(kw in t for kw in keywords):
            return density
    # Infer from type
    type_to_density = {
        "intro":      "обзорная",
        "overview":   "обзорная",
        "research":   "исследовательская",
        "practical":  "практическая",
        "narrative":  "повествовательная",
        "conclusion": "обзорная",
    }
    return type_to_density.get(type_hint, "практическая")


def parse_structure(path: str) -> list[dict]:
    """Parse structure.md and extract chapters."""
    text = Path(path).read_text(encoding="utf-8")
    chapters = []

    # Match headers like: ### Ch.01: Title, ## Глава 1. Title, ## Chapter 1: Title
    patterns = [
        r"^#{1,3}\s+(?:Ch\.?\s*(\d+)|Глава\s+(\d+)|Chapter\s+(\d+))[:.\s]+(.+)$",
        r"^#{1,3}\s+(Введение|Пролог|Заключение|Эпилог|Introduction|Prologue|Conclusion|Epilogue)\s*[:.\-—]?\s*(.*)$",
    ]

    for line in text.splitlines():
        line = line.strip()
        for pat in patterns:
            m = re.match(pat, line, re.IGNORECASE | re.MULTILINE)
            if m:
                groups = m.groups()
                if len(groups) >= 4:
                    # Numbered chapter: groups = (num1, num2, num3, title)
                    num = groups[0] or groups[1] or groups[2] or str(len(chapters) + 1)
                    title = (groups[3] or "").strip()
                    chapters.append({
                        "num": str(num).zfill(2),
                        "title": title,
                        "raw": line,
                    })
                elif len(groups) >= 1:
                    # Named section: groups = (name, subtitle)
                    name = groups[0] or ""
                    subtitle = groups[1] if len(groups) > 1 and groups[1] else ""
                    chapters.append({
                        "num": name,
                        "title": f"{name} {subtitle}".strip(),
                        "raw": line,
                    })
                break

    # Fallback: if no chapters found, try simpler patterns
    if not chapters:
        for line in text.splitlines():
            line = line.strip()
            m = re.match(r"^#{1,3}\s+(.+)$", line)
            if m and len(m.group(1)) > 3:
                chapters.append({
                    "num": str(len(chapters) + 1).zfill(2),
                    "title": m.group(1).strip(),
                    "raw": line,
                })

    return chapters


def calculate(chapters: list[dict]) -> list[dict]:
    """Calculate word count ranges for each chapter."""
    results = []
    for ch in chapters:
        ctype = detect_chapter_type(ch["title"])
        density = detect_density(ch["title"], ctype)
        base_min, base_max = BASELINES.get(ctype, (3000, 5000))
        mult = MULTIPLIERS.get(density, 1.0)
        adj_min = int(base_min * mult)
        adj_max = int(base_max * mult)
        results.append({
            "num": ch["num"],
            "title": ch["title"],
            "type": ctype,
            "density": density,
            "min": adj_min,
            "max": adj_max,
        })
    return results


def format_output(results: list[dict]) -> str:
    """Format results as markdown table + summary."""
    lines = []
    lines.append("# Word Count Plan — Auto-Calculated\n")
    lines.append(f"Chapters: **{len(results)}**\n")

    total_min = sum(r["min"] for r in results)
    total_max = sum(r["max"] for r in results)
    avg_min = total_min // len(results) if results else 0
    avg_max = total_max // len(results) if results else 0

    lines.append(f"Total range: **{total_min:,} – {total_max:,}** words")
    lines.append(f"Average per chapter: **{avg_min:,} – {avg_max:,}** words\n")

    lines.append("| # | Chapter | Type | Density | Min | Max |")
    lines.append("|---|---------|------|---------|-----|-----|")
    for r in results:
        lines.append(
            f"| {r['num']} | {r['title'][:50]} | {r['type']} | {r['density']} "
            f"| {r['min']:,} | {r['max']:,} |"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "foundation/structure.md"
    if not Path(path).exists():
        print(f"❌ File not found: {path}", file=sys.stderr)
        print(f"Usage: python3 {sys.argv[0]} [path/to/structure.md]", file=sys.stderr)
        sys.exit(1)

    chapters = parse_structure(path)
    if not chapters:
        print(f"❌ No chapters found in {path}", file=sys.stderr)
        sys.exit(1)

    results = calculate(chapters)
    print(format_output(results))


if __name__ == "__main__":
    main()
