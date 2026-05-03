# NonFiction Pipeline (NFP)

> Многостадийный pipeline для создания научно-популярных книг с помощью параллельных субагентов.

NFP разбивает написание книги объёмом 60–80K слов на 5 этапов: **Intake → Foundation → Drafting → Expansion → Assembly**. Каждый этап производит конкретные артефакты на диске и проверяемый результат.

Этот репозиторий — одновременно:

- **источник истины** для skill `nonfiction-book-pipeline`;
- **набор шаблонов и инструкций** для запуска нового книжного проекта.

---

## Что внутри репозитория

Основные части:

- `SKILL.md` — сам skill Hermes Agent
- `references/` — рабочие процедуры, проверки, чистка, публикация
- `templates/` — шаблоны для проекта книги
- `examples/` — примерные материалы на основе книги о Венеции
- `README.en.md` — английская версия этого файла

Типичный результат работы pipeline:

- `intake.json` — карточка проекта
- `foundation/` — тезис, план, voice, термины, факты
- `chapters/` — главы книги
- `drafts/manuscript.md` — собранная рукопись
- `drafts/book.pdf` — финальный PDF, если установлены pandoc и LaTeX

---

## Установка

### Шаг 1. Убедитесь, что установлен Hermes Agent

Если Hermes ещё не установлен — следуйте [официальной документации](https://hermes-agent.nousresearch.com/docs).

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

Hermes автоматически видит файлы из `~/.hermes/skills/`. Проще всего сделать симлинк или копию.

**Вариант A — симлинк, удобнее для обновлений:**

```bash
mkdir -p ~/.hermes/skills/software-development
ln -s $(pwd) ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

**Вариант B — копирование:**

```bash
mkdir -p ~/.hermes/skills/software-development/nonfiction-book-pipeline
cp -r . ~/.hermes/skills/software-development/nonfiction-book-pipeline
```

> Категория `software-development` не критична, но так skill удобнее держать в одной структуре.

### Шаг 4. Проверьте, что skill подхватился

```bash
ls ~/.hermes/skills/software-development/nonfiction-book-pipeline/
```

Если видите `SKILL.md`, `references/` и `templates/` — всё в порядке.

Также можно открыть Hermes CLI и проверить список skills командой `/skills`.

### Шаг 5. Установите системные зависимости для PDF

Финальная сборка PDF требует `pandoc` и LaTeX:

```bash
# Debian / Ubuntu
sudo apt-get install pandoc texlive-xelatex fonts-dejavu

# macOS
brew install pandoc texlive

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

1. Спросит уточнения — название, объём, аудиторию
2. Создаст foundation — тезис, план, voice-гид, термины, факты
3. Запустит параллельных субагентов — каждый пишет по 2–3 главы
4. Проверит объём и доработает недостающие главы
5. Соберёт `manuscript.md` и, если установлен pandoc, `book.pdf`

---

## Структура репозитория

```text
nonfiction-book-pipeline/
├── README.md                 # Основной README на русском
├── README.en.md              # Английская версия README
├── LICENSE                   # MIT
├── .gitignore
├── SKILL.md                  # Описание skill и правила работы
├── references/               # Сценарии, проверки и вспомогательные документы
├── templates/                # Шаблоны для foundation
└── examples/                 # Примерные материалы
```

Подробнее:

- `SKILL.md` — полное описание skill и его правил
- `references/` — пошаговые процедуры, проверки и рекомендации
- `templates/` — шаблоны для нового проекта книги
- `examples/` — пример тезиса и структуры

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

### 3. Drafting

Разбейте главы между субагентами:

- по 2–3 главы на одного субагента
- каждый субагент получает одинаковый foundation
- каждая глава должна следовать заданной структуре и voice

### 4. Expansion

Проверьте полноту и объём:

- найдите отсутствующие главы
- найдите слишком короткие главы
- расширяйте их без удаления удачных фрагментов

### 5. Assembly

Соберите `manuscript.md` и, если есть инструменты, сгенерируйте PDF.

```bash
pandoc --standalone --toc --pdf-engine=xelatex -o book.pdf drafts/manuscript.md
```

---

## Важные правила работы

- Один `foundation/` должен быть единственным источником истины.
- Субагенты не должны выдумывать факты, имена и прямые цитаты.
- Перед drafting проверяйте confidence и verified в `facts.json`.
- Держите задачи для субагентов короткими и контролируемыми.
- После expansion чистите смешанные языковые артефакты и перепроверяйте объём.

---

## Где читать дальше

- `SKILL.md` — полное рабочее руководство
- `references/github-publish.md` — публикация и пуш в GitHub
- `references/subagent-delegation-failure.md` — workaround для делегации
- `references/final-review-protocol.md` — финальная редактура
- `references/json-source-validation.md` — проверка JSON

---

## Лицензия

MIT License.
