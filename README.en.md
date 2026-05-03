# NonFiction Pipeline (NFP)

> A multi-stage pipeline for creating non-fiction books with Hermes Agent and parallel subagents.

NFP breaks a roughly 60–100K-word book into 5 stages: **Intake → Foundation → Drafting → Expansion → Assembly**. Each stage produces concrete disk artifacts and a verifiable result.

This repository is both:

- the **source of truth** for the `nonfiction-book-pipeline` skill;
- a **template and operations kit** for starting new book projects.

---

## What this repository contains

Main parts:

- `SKILL.md` — the Hermes Agent skill and the full operating guide
- `references/` — procedures, checks, troubleshooting, cleanup, publishing notes
- `templates/` — foundation templates for new book projects
- `README.md` — Russian version of this file

Venice example materials live in `references/`, not in a separate `examples/` directory:

- `references/example-thesis-venice.md`
- `references/example-structure-venice.md`

Typical output inside a concrete book project directory:

- `intake.json` — project metadata
- `foundation/` — thesis, structure, voice, terms, facts, and additional factual registries
- `chapters/` — chapter drafts
- `manuscript.md` — assembled manuscript
- `book.pdf` — final PDF, if Pandoc, XeLaTeX, and fonts are installed

---

## Installation

### Step 1. Make sure Hermes Agent is installed

Follow the official Hermes Agent documentation:

https://hermes-agent.nousresearch.com/docs

Verify that Hermes runs:

```bash
hermes --help
```

### Step 2. Clone the repository

```bash
git clone https://github.com/perejaslav/nonfiction-book-pipeline.git
cd nonfiction-book-pipeline
```

### Step 3. Install the pipeline as a skill

Hermes reads skill files from `~/.hermes/skills/`. Copy or link this repository there.

**Option A — symlink, easier to update:**

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$(pwd)" ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

**Option B — copy:**

```bash
mkdir -p ~/.hermes/skills/software-development/nonfiction-book-pipeline
rsync -a --exclude .git ./ ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

### Step 4. Verify that the skill is available

```bash
ls ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

If you see `SKILL.md`, `references/`, and `templates/`, the files are in place.

You can also start Hermes CLI and run `/skills` — `nonfiction-book-pipeline` should appear in the list.

### Step 5. Install system dependencies for PDF output

PDF generation requires Pandoc, XeLaTeX, fonts, and PDF inspection tools:

```bash
# Debian / Ubuntu
sudo apt-get install pandoc texlive-xelatex fonts-liberation fonts-freefont-otf poppler-utils

# macOS
brew install pandoc texlive poppler

# Or skip this step — the pipeline still produces manuscript.md
# and you can convert it to PDF later.
```

---

## How to use it

After installation, say one of the trigger phrases to Hermes:

- “Write a popular science book about space”
- “Run NFP for the topic history of Rome”
- “Create a nonfiction pipeline for a book on quantum physics”
- “I need a book on a historical topic”
- “Assemble a book from chapters, create manuscript”

Hermes will then:

1. Ask for clarifications: title, scope, audience, and execution mode
2. Build the foundation — thesis, structure, voice guide, terms, facts
3. For historical books, add `entities.md`, `fact_risk_map.md`, and `reconstruction_policy.md`
4. Launch parallel subagents through Hermes `delegate_task` — each writes 2–3 chapters
5. Check length and expand missing or short chapters
6. Run factual spot-checks and clean language artifacts
7. Assemble `manuscript.md` and, if Pandoc is installed, `book.pdf`

---

## Repository structure

```text
nonfiction-book-pipeline/
├── README.md                 # Russian README
├── README.en.md              # English README
├── SKILL.md                  # Skill definition and operating rules
├── references/               # Supporting procedures and notes
└── templates/                # Foundation templates
```

More details:

- `SKILL.md` — full skill definition and operating rules
- `references/` — step-by-step procedures, checks, troubleshooting, and recommendations
- `templates/` — templates for a new book project
- `references/example-*.md` — example thesis and structure materials

---

## Step-by-step workflow

### 1. Intake

Collect the user brief:

- title
- subject
- thesis
- target word count
- chapter count
- audience
- language

Write the result to `intake.json`.

### 2. Foundation

Create the canonical project baseline:

- `foundation/thesis.md`
- `foundation/structure.md`
- `foundation/voice.md`
- `foundation/terms.md`
- `foundation/facts.json`

For historical books, also maintain:

- `foundation/entities.md`
- `foundation/fact_risk_map.md`
- `foundation/reconstruction_policy.md`

`facts.json` must include `confidence` and `verified` fields; facts with `confidence: low` or `verified: false` must not be used as established facts.

### 3. Drafting

Split chapters across subagents:

- 2–3 chapters per subagent
- every subagent must receive the same foundation files
- each chapter must follow the assigned structure and style
- uncertain names, dates, numbers, and quotes must be checked before insertion

### 4. Expansion & Verification

Review completeness, length, and factual risks:

- find missing chapters
- find chapters under the target length
- expand them without deleting the good parts
- run a spot-check on 5–10 high-risk claims
- use the local Search Harvester for verification; external `web_search`, `web_extract`, and browser search require separate user permission
- after expansion, clean CJK/English/mixed-script artifacts

### 5. Assembly

Merge chapters into `manuscript.md`, then build PDF if the toolchain is available.

```bash
pandoc \
  --standalone \
  --toc \
  --toc-depth=1 \
  --pdf-engine=xelatex \
  -V mainfont="Liberation Serif" \
  -o book.pdf \
  manuscript.md
```

Verify the result:

```bash
pdfinfo book.pdf
pdftotext book.pdf - | head -60
```

---

## Important operating rules

- Keep one `foundation/` directory as the single source of truth.
- Do not let subagents invent facts, names, exact numbers, or direct quotes.
- Check `confidence` and `verified` in `facts.json` before drafting.
- For historical books, maintain `entities.md`, `fact_risk_map.md`, and `reconstruction_policy.md`.
- Prefer short, controlled subagent tasks: 2–3 chapters per task.
- Expansion is a mandatory second wave, not an optional stage.
- After expansion, clean mixed-language artifacts and verify word count.

---

## Where to read more

- `SKILL.md` — full operating guide
- `references/github-publish.md` — publishing workflow
- `references/subagent-delegation-failure.md` — delegation workaround
- `references/final-review-protocol.md` — final editing workflow
- `references/json-source-validation.md` — JSON validation rules
- `references/cleanup-patterns.md` — language and patch-artifact cleanup

---

## License

MIT License.
