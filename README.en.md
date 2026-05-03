# NonFiction Pipeline (NFP)

> A multi-stage pipeline for creating non-fiction books with parallel subagents.

NFP breaks a 60–80K-word book into 5 stages: **Intake → Foundation → Drafting → Expansion → Assembly**. Each stage produces concrete disk artifacts and a verifiable result.

The pipeline lives as a **Hermes Agent skill** — you can simply say something like “write a popular science book about …”, and Hermes will run all 5 stages.

---

## What this repository contains

This repository is both:

- the **source of truth** for the NFP skill;
- a **template kit** for starting new book projects.

Typical project output:

- `intake.json` — project metadata
- `foundation/` — thesis, structure, voice, terms, facts
- `chapters/` — chapter drafts
- `drafts/manuscript.md` — assembled manuscript
- `drafts/book.pdf` — final PDF, if the toolchain is installed

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

Hermes scans `~/.hermes/skills/` automatically. Copy or link this repository there.

**Option A — symlink (easier to update):**

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s $(pwd) ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

**Option B — copy:**

```bash
mkdir -p ~/.hermes/skills/software-development/nonfiction-book-pipeline
cp -r . ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

### Step 4. Verify that the skill is available

```bash
ls ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

If you see `SKILL.md` and `templates/`, the installation is complete.

You can also start Hermes CLI and run `/skills` — `nonfiction-book-pipeline` should appear in the list.

### Step 5. Install system dependencies for PDF output

PDF generation at the end of the pipeline requires Pandoc and LaTeX:

```bash
# Debian / Ubuntu
sudo apt-get install pandoc texlive-xelatex fonts-dejavu

# macOS
brew install pandoc texlive

# Or skip this step — the pipeline still produces manuscript.md
# and you can convert it to PDF later.
```

---

## How to use it

After installation, just say one of the trigger phrases to Hermes:

- “Write a popular science book about space”
- “Run NFP for the topic history of Rome”
- “Create a nonfiction pipeline for a book on quantum physics”
- “I need a book on a historical topic”
- “Assemble a book from chapters, create manuscript”

Hermes will then:

1. Ask for clarifications (title, scope, audience)
2. Build the foundation — thesis, structure, voice guide, terms, facts
3. Launch parallel subagents — each writes 2–3 chapters
4. Check length and expand short chapters
5. Assemble `manuscript.md` and, if Pandoc is installed, `book.pdf`

---

## Repository structure

```text
nonfiction-book-pipeline/
├── README.md                 # Main Russian README
├── README.en.md              # English README
├── LICENSE                   # MIT
├── .gitignore
├── SKILL.md                  # Skill definition and operating rules
├── references/               # Supporting procedures and notes
├── templates/                # Foundation templates
└── examples/                 # Example materials
```

More details:

- `SKILL.md` — full skill definition and operating rules
- `references/` — step-by-step procedures, checks, and recommendations
- `templates/` — templates for a new book project
- `examples/` — example thesis and structure materials

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

### 3. Drafting

Split chapters across subagents:

- 2–3 chapters per subagent
- every subagent must receive the same foundation files
- each chapter must follow the assigned structure and style

### 4. Expansion

Review chapter length and completeness:

- find missing chapters
- find chapters under the target length
- expand them without deleting the good parts

### 5. Assembly

Merge chapters into `manuscript.md`, then build PDF if the toolchain is available.

```bash
pandoc --standalone --toc --pdf-engine=xelatex -o book.pdf drafts/manuscript.md
```

---

## Important operating rules

- Keep one `foundation/` directory as the single source of truth.
- Do not let subagents invent facts, names, or direct quotes.
- Use the fact confidence / verification rules before drafting.
- Prefer short, controlled subagent tasks over large ones.
- After expansion, clean mixed-language artifacts and verify word count.

---

## Where to read more

- `SKILL.md` — full operating guide
- `references/github-publish.md` — publishing workflow
- `references/subagent-delegation-failure.md` — delegation workaround
- `references/final-review-protocol.md` — final editing workflow
- `references/json-source-validation.md` — JSON validation rules

---

## License

MIT License.
