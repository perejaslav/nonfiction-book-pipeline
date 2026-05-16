# NonFiction Pipeline (NFP)

> Многостадийный pipeline для создания научно-популярных книг с помощью Hermes Agent и параллельных субагентов.

NFP разбивает написание книги объёмом примерно 60–100K слов на 5 этапов: **Intake → Foundation → Drafting → Expansion → Assembly**. Каждый этап производит конкретные артефакты на диске и проверяемый результат.

Этот репозиторий — одновременно:

- **источник истины** для skill `nonfiction-book-pipeline`;
- **набор шаблонов и рабочих инструкций** для запуска нового книжного проекта.

---

## Что внутри репозитория

Основные части:

- `SKILL.md` — сам skill Hermes Agent и полное рабочее руководство
- `references/` — процедуры, проверки, диагностика, чистка, публикация
- `templates/` — шаблоны foundation-файлов для нового проекта книги
- `README.en.md` — английская версия этого файла

Примерные материалы по Венеции лежат не в отдельной папке `examples/`, а в `references/`:

- `references/example-thesis-venice.md`
- `references/example-structure-venice.md`

Типичный результат работы pipeline в директории конкретной книги:

- `intake.json` — карточка проекта
- `foundation/` — тезис, структура, voice, термины, факты и дополнительные фактологические реестры
- `chapters/` — главы книги
- `manuscript.md` — собранная рукопись
- `book.pdf` — финальный PDF, если установлены pandoc, XeLaTeX и шрифты

---

## Установка

### Шаг 1. Убедитесь, что установлен Hermes Agent

Если Hermes ещё не установлен — следуйте официальной документации:

https://hermes-agent.nousresearch.com/docs

Проверьте запуск:

```bash
hermes --help
```

### Шаг 2. Клонируйте репозиторий

```bash
git clone https://github.com/perejaslav/nonfiction-book-pipeline.git
cd nonfiction-book-pipeline
```

### Шаг 3. Установите pipeline как skill

Hermes видит skill-файлы из `~/.hermes/skills/`. Проще всего сделать симлинк или копию.

**Вариант A — симлинк, удобнее для обновлений:**

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s "$(pwd)" ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

**Вариант B — копирование:**

```bash
mkdir -p ~/.hermes/skills/software-development/nonfiction-book-pipeline
rsync -a --exclude .git ./ ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

> Категория `software-development` не критична, но так skill удобно держать в общей структуре.

### Шаг 4. Проверьте, что skill подхватился

```bash
ls ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

Если видите `SKILL.md`, `references/` и `templates/` — файлы на месте.

Также можно открыть Hermes CLI и проверить список skills командой `/skills`.

### Шаг 5. Установите системные зависимости для PDF

Финальная сборка PDF требует `pandoc`, XeLaTeX, шрифты и инструменты проверки PDF:

```bash
# Debian / Ubuntu
sudo apt-get install pandoc texlive-xelatex fonts-liberation fonts-freefont-otf poppler-utils

# macOS
brew install pandoc texlive poppler

# Если не ставить зависимости сейчас — pipeline всё равно соберёт manuscript.md,
# а PDF можно создать позже.
```

---

## Как пользоваться

После установки достаточно сказать агенту одну из триггерных фраз:

- «Напиши научно-популярную книгу о космосе»
- «Запусти NFP для темы история Рима»
- «Создай nonfiction pipeline для книги по квантовой физике»
- «Нужно написать книгу на историческую тему»
- «Собери книгу из глав, создай manuscript»

Агент сам:

1. Уточнит название, объём, аудиторию и режим работы
2. Создаст foundation — тезис, план, voice-гид, термины, факты
3. Для исторических книг добавит `entities.md`, `fact_risk_map.md` и `reconstruction_policy.md`
4. Запустит параллельных субагентов через Hermes `delegate_task` — каждый пишет по 2–3 главы
5. **Предъявит пользователю Введение + Главу 1 для подтверждения тона и стиля** (единственная точка контроля)
6. Проверит объём и доработает недостающие или короткие главы
7. Проведёт фактологический spot-check, чистку языковых артефактов и **удаление запрещённых конструкций**
8. Соберёт `manuscript.md` и, если установлен pandoc, `book.pdf`

---

## Структура репозитория

```text
nonfiction-book-pipeline/
├── README.md                 # Основной README на русском
├── README.en.md              # Английская версия README
├── SKILL.md                  # Описание skill и правила работы
├── references/               # Сценарии, проверки и вспомогательные документы
└── templates/                # Шаблоны для foundation
```

Подробнее:

| `SKILL.md` — описание skill (6 этапов, 4 режима работы, 7 проходов редактуры)
| `references/` — 40+ процедур и проверок: фактчекинг, чистка стиля, публикация, troubleshooting
| `templates/` — 17 шаблонов foundation-файлов: тезис, структура, voice, термины, факты, evidence gaps, карта повторов, карта рисков, word count plan, переходные якоря
- `references/example-*.md` — пример тезиса и структуры

---

## Пошаговый рабочий процесс

### 1. Intake

Соберите исходный запрос пользователя:

- название
- тема
- тезис
- целевой объём
- число глав
- аудитория
- язык

Результат запишите в `intake.json`.

### 2. Foundation

Создайте единую базу проекта:

- `foundation/thesis.md`
- `foundation/structure.md`
- `foundation/voice.md`
- `foundation/terms.md`
- `foundation/facts.json`

Для исторических книг дополнительно нужны:

- `foundation/entities.md`
- `foundation/fact_risk_map.md`
- `foundation/reconstruction_policy.md`

`facts.json` должен содержать поля `confidence` и `verified`; факты с `confidence: low` или `verified: false` нельзя использовать как установленные.

### 3. Drafting

Разбейте главы между субагентами:

- по 2–3 главы на одного субагента
- каждый субагент получает одинаковый foundation
- каждая глава должна следовать заданной структуре и voice
- сомнительные имена, даты, цифры и цитаты проверяются до вставки в текст

### 4. Expansion & Verification

Проверьте полноту, объём и фактологические риски:

- найдите отсутствующие главы
- найдите слишком короткие главы
- расширяйте их без удаления удачных фрагментов
- проведите spot-check 5–10 наиболее рискованных утверждений
- для проверки используйте локальный Search Harvester; внешние `web_search`, `web_extract` и браузерный поиск — только с отдельного разрешения пользователя
- после expansion чистите CJK/English/mixed-script артефакты

### 5. Assembly

Соберите `manuscript.md` и, если есть инструменты, сгенерируйте PDF.

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

Проверьте результат:

```bash
pdfinfo book.pdf
pdftotext book.pdf - | head -60
```

---

## Важные правила работы

- Один `foundation/` должен быть единственным источником истины.
- Субагенты не должны выдумывать факты, имена, точные числа и прямые цитаты.
- Перед drafting проверяйте `confidence` и `verified` в `facts.json`.
- Для исторических книг ведите `entities.md`, `fact_risk_map.md` и `reconstruction_policy.md`.
- Держите задачи для субагентов короткими и контролируемыми: 2–3 главы на задачу.
- Expansion — обязательная вторая волна, а не опциональный этап.
- После expansion чистите смешанные языковые артефакты и перепроверяйте объём.

---

## Где читать дальше

- `SKILL.md` — полное рабочее руководство
- `references/genre-narrative-patterns.md` — жанровые метапаттерны глав
- `references/anti-ai-style-patterns.md` — запрещённые конструкции и шаблонные фразы
- `references/manuscript-repetition-audit.md` — аудит повторов и лексический детектор
- `references/evidence-pack-guide.md` — evidence packs и evidence gaps
- `references/github-publish.md` — публикация и пуш в GitHub
- `references/subagent-delegation-failure.md` — workaround для делегации
- `references/final-review-protocol.md` — финальная редактура
- `references/json-source-validation.md` — проверка JSON
- `references/cleanup-patterns.md` — чистка языковых и patch-артефактов

---

## Лицензия

MIT License.
