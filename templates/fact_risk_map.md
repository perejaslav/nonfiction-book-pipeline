# Fact Risk Map

Use this file before drafting and before final review. It identifies claims that are likely to attract criticism if wrong or overstated.

## Risk categories

- `absolute_first` — first, earliest, oldest, unprecedented
- `exact_number` — precise quantities, dimensions, budgets, armies, dates
- `named_specialist` — archaeologists, translators, expeditions, catalogued objects
- `direct_influence` — claims that one religion/culture directly produced another
- `anachronism` — modern metaphors or later concepts projected backward
- `specialist_term` — rare technical term with uncertain function
- `quote` — direct speech, translated passage, poetic line
- `artifact` — tablet, papyrus, inscription, statue, seal, museum object
- `chronology` — person/event/date alignment
- `entity_link` — city ↔ patron, office ↔ function, person ↔ event

## High-risk claims

### risk_001
Claim: "[exact wording or paraphrase]"
Risk type: absolute_first|exact_number|named_specialist|direct_influence|anachronism|specialist_term|quote|artifact|chronology|entity_link
Why risky: [what could be wrong]
Safer wording: "[safe formulation]"
Status: allow|allow_with_caveat|needs_source|forbid
Source: fact_XXX / external check needed
Owner: [chapter/section]

## Standard safer formulations

- "first" → "one of the earliest known" / "among the earliest documented"
- "X caused Y" → "X was one of the earlier layers in the broader cultural field around Y"
- "direct descendant" → "transformed through later traditions" / "typological parallel"
- exact number without source → "several", "many", "roughly", "by some estimates"
- named specialist without source → "archaeologists", "researchers", "a later source"
- direct quote without source → paraphrase or mark as reconstruction

## Final review checklist

- [ ] No absolute-first claims without source and criterion
- [ ] No exact numbers without facts.json or caveat
- [ ] No named specialists without source
- [ ] No artifact claims without provenance/source
- [ ] No reconstructed quotes presented as direct quotations
- [ ] No direct influence claims where only typological parallels are supported
- [ ] No specialist terms used in unsupported roles
