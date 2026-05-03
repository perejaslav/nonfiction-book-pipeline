# Subagent Delegation Failure — Диагностика и решение

## Две независимые причины HTTP 404

`delegate_task` с провайдером `opencode-go` может возвращать `HTTP 404 — Not Found | opencode` по двум разным причинам. Они независимы и могут сочетаться.

---

## Причина 1: Неправильный base_url (транспортная)

**Симптом:** HTTP 404 + HTML-страница в теле ответа.

**Механизм:** При вызове `delegate_task` → `_resolve_delegation_credentials(requested="opencode-go")` вызывается **без** параметра `target_model`. Для провайдера `opencode-go` это критично:

| Параметр | Без target_model | С target_model="deepseek-v4-flash" |
|----------|-------------------|--------------------------------------|
| `api_mode` | `anthropic_messages` | `chat_completions` |
| `base_url` | `https://opencode.ai/zen/go` | `https://opencode.ai/zen/go/v1` |

Запрос без `target_model` попадает на эндпоинт `/v1/messages` (Anthropic-совместимый), который возвращает 404 + HTML.

**Решение (workaround):** В `~/.hermes/config.yaml`:
```yaml
delegation:
  base_url: 'https://opencode.ai/zen/go/v1'
```
При наличии `delegation.base_url` функция `_resolve_delegation_credentials` обходится полностью — base_url и api_mode берутся напрямую из конфига.

---

## Причина 2: Reasoning-модель возвращает пустой content

**Симптом:** HTTP 200, ответ пришёл, но `content` пуст, `finish_reason: length`.

**Механизм:** `deepseek-v4-flash` — reasoning-модель. По умолчанию весь ответ кладётся в проприетарное поле `reasoning_content`, а `content` остаётся пустым:

```json
{
  "choices": [{
    "message": {
      "content": "",                    // ← ПУСТО
      "reasoning_content": "Thinking..." // ← всё здесь
    },
    "finish_reason": "length"
  }]
}
```

Hermes Agent парсит ответ, ожидая текст в `content`, получает пустую строку → generic error или 404.

**Решение:** Код в `agent/transports/chat_completions.py` (строки 327–331) уже содержит исправление:
```python
if provider_name == "opencode-go":
    extra_body["thinking"] = {"type": "disabled"}
```
Это добавляет `"thinking":{"type":"disabled}"` в запрос, и модель возвращает ответ в `content`. Исправление работает автоматически при правильном `base_url` (Причина 1).

**Диагностика:**
```bash
source ~/.hermes/.env
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"OK"}],"max_tokens":10}'
```

Без `thinking:disabled`: `"content":""`, `"finish_reason":"length"`
С `thinking:disabled`: `"content":"OK"`, `"finish_reason":"stop"`

---

## Комбинированная диагностика

```bash
source ~/.hermes/.env

# Тест 1: без thinking disabled (ожидаем пустой content = Причина 2)
echo "=== Тест 1: без thinking disabled ==="
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"ANSWER"}],"max_tokens":10}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('content:', repr(r['choices'][0]['message'].get('content','')), 'finish:', r['choices'][0]['finish_reason'])"

# Тест 2: с thinking disabled (ожидаем content = ANSWER)
echo "=== Тест 2: с thinking disabled ==="
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"ANSWER"}],"max_tokens":10,"thinking":{"type":"disabled"}}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print('content:', repr(r['choices'][0]['message'].get('content','')), 'finish:', r['choices'][0]['finish_reason'])"
```

**Тест 1** должен показать пустой content (если показывает ANSWER — модель не reasoning и проблема в другом).
**Тест 2** должен показать content = "ANSWER". Если нет — проверить API-ключ.

---

## Что НЕ помогает

- Смена модели на `kimi-k2.6`, `deepseek-chat` и т.д. (не решает проблему base_url)
- Изменение `acp_command`, `acp_args`
- Установка бинарника `copilot` (ACP-транспорт не используется при правильном base_url)

## Что работает (актуально 2026-05-02, подтверждено)

1. `~/.hermes/config.yaml` — секция `delegation.base_url`
2. `~/.hermes/.env` — `OPENAI_API_KEY` с валидным ключом
3. Субагент-делегация работает: 8 глав (4–11) книги «Глина и Звёзды» написаны за два последовательных батча

## Хронология

| Дата | Событие |
|------|---------|
| 2026-05-01 | Первые тесты delegate_task — HTTP 404. ACP-транспорт не найден. |
| 2026-05-02 AM | Пользователь находит root cause: `_resolve_delegation_credentials` без `target_model` → неправильный api_mode + base_url. |
| 2026-05-02 AM | Применён workaround: `delegation.base_url` в config.yaml. |
| 2026-05-02 AM | Дополнительная проблема: `deepseek-v4-flash` reasoning → пустой content. |
| 2026-05-02 AM | Код `chat_completions.py` уже содержит `{"thinking":{"type":"disabled"}}` для opencode-go. Работает при правильном base_url. |
| 2026-05-02 AM | Батч 1 (главы 4–6) — успех. |
| 2026-05-02 AM | Батч 2 (главы 7–9) — успех. |
| 2026-05-02 AM | Батч 3 (главы 10–11) — успех. |

## Ключевой файл

`agent/transports/chat_completions.py`, строки 327–331:
```python
# opencode.ai: top-level thinking parameter (not extra_body.reasoning)
# deepseek-v4-flash and similar reasoning models need {"type":"disabled"}
# to return content in the "content" field instead of "reasoning_content"
if provider_name == "opencode-go":
    extra_body["thinking"] = {"type": "disabled"}
```
