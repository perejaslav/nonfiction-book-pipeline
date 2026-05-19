# PDF Export Reference

## Overview

Pandoc + XeLaTeX workflow for Russian-language nonfiction books. A5 format, DejaVu fonts, cover page + body assembled via `pdfunite`.

## Full Pipeline

### Step 1 — Cover image (AI-generated)

```python
image_generate(aspect_ratio='portrait', prompt='...')
# Save to: project/assembly/cover.jpg
```

### Step 2 — Cover PDF (standalone XeLaTeX)

Create `/project/assembly/cover.tex`:
```latex
\documentclass[12pt]{article}
\usepackage{fontspec}
\usepackage[russian]{babel}
\usepackage{graphicx}
\usepackage{geometry}
\geometry{papersize={170mm,240mm}, top=0mm, bottom=0mm, left=0mm, right=0mm}
\usepackage[export]{adjustbox}
\usepackage{color}

\pagecolor{black}
\begin{document}
\thispagestyle{empty}
\noindent\adjustbox{width=\paperwidth,height=\paperheight,bfspan}{\includegraphics{cover.jpg}}
\vspace{-120mm}
\begin{center}
\textcolor{white}{\LARGE\textbf{Заголовок книги}}\\[4mm]
\textcolor{white}{\large Подзаголовок}\\[8mm]
\textcolor{white}{Автор}\\[2mm]
\textcolor{white}{2026}
\end{center}
\end{document}
```

Build:
```bash
cd project/assembly && xelatex -interaction=batchmode cover.tex
```

### Step 3 — Manuscript body

**CRITICAL**: Always include `toc: true` in YAML frontmatter. This generates a clickable table of contents as page 2 of the body. Without it, there is no ToC or it won't be clickable.

```bash
cd project/assembly
pandoc --pdf-engine=xelatex manuscript.md -o body.pdf
```

**YAML frontmatter must contain `toc: true`**:
```yaml
---
title: "Название книги"
author: "Автор"
date: "2026"
lang: ru-RU
mainfont: "DejaVu Serif"
fontsize: 11pt
papersize: a5
geometry:
  - top=20mm
  - bottom=20mm
  - left=18mm
  - right=18mm
toc-title: "Содержание"
numbersections: false
toc: true          # ← ОБЯЗАТЕЛЬНО: генерирует кликабельное оглавление
linkcolor: darkgray
urlcolor: darkgray
---

### Step 4 — Extract clean cover page

`xelatex` may output 3 pages (blank + cover + blank). Extract only page 2 (the real cover):

```python
from pypdf import PdfReader, PdfWriter
cover = PdfReader('cover.pdf')
clean = PdfWriter()
clean.add_page(cover.pages[1])  # page 2 (0-indexed = 1)
with open('cover-single.pdf', 'wb') as f:
    clean.write(f)
```

### Step 5 — Merge

```bash
pdfunite cover-single.pdf body.pdf final.pdf
```

## Common Problems

### `! Text line contains an invalid character. l.99 ^^H`

**Cause**: LaTeX commands (e.g. `\begin`, `\vspace`, `\newpage`) from a failed cover prepend ended up as raw text in `manuscript.md`. The `^^H` is backspace control char (0x08).

**Detection**:
```python
import re
dirty = [(i+1, l) for i, l in enumerate(content.split('\n'))
         if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', l)]
```

**Fix**:
```python
import re
clean = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', content)
```

### Corrupted LaTeX fragments in markdown (e.g. `egin{center}`, `space*{0pt}`)

**Cause**: When inserting cover page with raw LaTeX commands into markdown (using pandoc YAML or `\begin{center}` syntax), pandoc mishandles it and outputs corrupted text to the markdown file on subsequent runs.

**Fix**: Remove the corrupted lines. The first line after YAML frontmatter should NOT be `egin{center}` or `\begin{center}`. If it is — the cover page insert attempt failed. Remove everything from `\begin` to `\newpage` in the corrupted area and rebuild.

**Prevention**: Never insert raw LaTeX into markdown files. Always build cover as a separate standalone XeLaTeX document, then merge PDFs with `pdfunite`.

### Duplicate YAML frontmatter

**Cause**: Prepending a new YAML header to a file that already has one.

**Fix**: Strip existing frontmatter before adding new one:
```python
if content.startswith('---'):
    end = content.index('\n---\n', 4)
    content = content[end+5:].lstrip()
with open(path, 'w') as f:
    f.write(new_header + content)
```

### Font not found: `! Font ... not loadable`

**Fix**: Use fonts guaranteed to be on the system:
- `DejaVu Serif` — default, good for Cyrillic
- `Liberation Serif` — fallback if DejaVu missing
- `FreeSerif` — for non-Latin scripts (Greek, Coptic)

```bash
fc-list :lang=ru family  # list Cyrillic-capable fonts
```

## Verification

```bash
pdfinfo final.pdf  # Pages, size, creator
pdftotext final.pdf - | head -20  # readable start
```

## File Size

~300-500 KB for A5, ~24K words is normal.