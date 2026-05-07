# Foundation Readiness Verification Script

Скрипт для быстрой проверки готовности фундамента NFP. Запускать после завершения Foundation и перед запуском Drafting.

## Быстрый запуск

```bash
python3 << 'EOF'
import json, re, sys

base = "/root/hermes-nonfiction-pipeline"  # изменить для другого проекта
project = "derzhava-ahemenidov"            # изменить для другого проекта

facts_path = f"{base}/{project}/foundation/facts.json"
struct_path = f"{base}/{project}/foundation/structure.md"

try:
    with open(facts_path) as f:
        facts_data = json.load(f)
    with open(struct_path) as f:
        structure = f.read()
except FileNotFoundError as e:
    print(f"❌ FILE NOT FOUND: {e}")
    sys.exit(1)

facts = facts_data.get("facts", [])
db_ids = {f["id"]: f for f in facts}
fact_refs = set(re.findall(r"fact_\w+", structure))

uncovered = fact_refs - db_ids
unused = db_ids - fact_refs

# Group by chapter
missing_by_ch = {}
for fid in sorted(uncovered):
    parts = fid.replace("fact_", "").split("_")
    ch = parts[0]
    missing_by_ch.setdefault(ch, []).append(fid)

blocked = [ch for ch, fids in missing_by_ch.items()
           if ch.isdigit() and len(fids) >= 3]

print("=" * 60)
print(f"Foundation Readiness Report")
print(f"Project: {project}")
print("=" * 60)
print(f"Total facts in DB: {len(db_ids)}")
print(f"Total fact refs in structure: {len(fact_refs)}")
print(f"Uncovered (in plan, missing from DB): {len(uncovered)}")
print(f"Unused (in DB, not in plan): {len(unused)}")
print(f"Blocked chapters (all 3 facts missing): {blocked}")
print()

if uncovered:
    print("MISSING FACTS BY CHAPTER:")
    for ch, fids in sorted(missing_by_ch.items(), key=lambda x: (not x[0].isddigit(), x[0])):
        print(f"  {ch}: {fids}")
    print()

# Field completeness check
required_fields = ["id", "category", "claim", "source_type", "source_ref",
                   "confidence", "verified", "verification_method", "risk_categories"]
missing_fields = []
for fid, fact in db_ids.items():
    for req in required_fields:
        val = fact.get(req)
        if val is None or val == []:
            missing_fields.append((fid, req))

unverified = [fid for fid, f in db_ids.items() if not f.get("verified")]
low_conf = [fid for fid, f in db_ids.items() if f.get("confidence") == "low"]
empty_rc = [fid for fid, f in db_ids.items() if not f.get("risk_categories")]

print("QUALITY CHECKS:")
print(f"  Missing required fields: {len(missing_fields)}")
if missing_fields[:5]:
    print(f"    Examples: {missing_fields[:3]}")
print(f"  Unverified facts (verified:false): {len(unverified)}")
if unverified:
    print(f"    {unverified}")
print(f"  Low confidence: {len(low_conf)}")
print(f"  Empty risk_categories: {len(empty_rc)}")
if empty_rc:
    print(f"    {empty_rc[:5]}...")

high = sum(1 for f in facts if f.get("confidence") == "high")
medium = sum(1 for f in facts if f.get("confidence") == "medium")
print(f"\nConfidence: {high} high, {medium} medium")

print()
print("=" * 60)
if not uncovered and not unused and not missing_fields and not unverified and not empty_rc:
    print("✅ READY TO DRAFT")
else:
    print("❌ NOT READY — fix issues before Drafting")
print("=" * 60)
EOF
```

## Что проверять

| Метрика | Порог готовности |
|---|---|
| uncovered | 0 |
| unused | 0 |
| blocked chapters | 0 |
| missing required fields | 0 |
| verified: false | 0 |
| confidence: low | 0 |
| empty risk_categories | 0 |
| JSON valid | да |

## Что делать с каждой проблемой

**uncovered > 0:**
- Собрать факты через исследование (delegate_task с web search)
- Добавить в facts.json
- Повторить проверку

**blocked chapters > 0:**
- Приоритизировать блокирующие главы (16, 17, 22, 24 в проекте Ахеменидов)
- Каждая блокирующая глава получает 3 новых факта из академических источников

**empty risk_categories:**
- Для каждого факта без категорий риска определить тип риска по claim:
  - exact_number → ["exact_number"]
  - содержит прямые цитаты → ["direct_quote"]
  - содержит "по преданию", "по мнению" → ["debatable_claim"]
  - содержит термины specialist_term
  - утверждение о влиянии → ["direct_influence"]

**verified: false:**
- Переформулировать факт так, чтобы он был верифицируемым
- Или понизить до гипотезы ("по некоторым сведениям...")
- Или удалить из DB и из structure.md

## Хронология известных кейсов

- **2026-05-05 (Сотня лет позора):** Боевой прогон Full Auto — 14 глав, ~9 600 слов за 5 параллельных субагентных потоков (~218 с суммарно). Facts.json: 56 фактов (high/medium/low, verified). Все главы в диапазоне 640–740 слов. Мосты соблюдены. Двухволновая стратегия: волна 1 = все 14 субагентов, волна 2 = Expansion по необходимости. Итог: 14/14 файлов, manuscript.md собран за один проход.
- **2026-05-03 (Держава Ахеменидов):** Foundation "выглядел готовым" — все 9 файлов созданы, но facts.json содержал 55/89 фактов. 4 главы полностью заблокированы. Проверка выявила 34 missing facts. Процесс: сбор 34 фактов → добавление в DB → заполнение missing_fields (category, risk_categories) → повторная проверка → READY.
