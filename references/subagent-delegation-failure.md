# Subagent Delegation — opencode-go + deepseek-v4-flash

## Конфигурация (рабочая, с 2026-05-12)

`delegate_task` использует `provider: opencode-go`, `model: deepseek-v4-flash` с явным `base_url`.

**Конфиг (`~/.hermes/config.yaml`):**
```yaml
delegation:
  model: deepseek-v4-flash
  provider: opencode-go
  base_url: 'https://opencode.ai/zen/go/v1'   # ← критично
  api_key: ''                                  # ← берётся из .env
  max_iterations: 50
  child_timeout_seconds: 900
  reasoning_effort: low
  max_concurrent_children: 3
```

**Ключи (`~/.hermes/.env`):**
```
OPENCODE_GO_API_KEY=sk-...
```

## Ключевой момент: delegation.base_url

Секция `delegation.base_url` обходит `_resolve_delegation_credentials` полностью. Без неё функция вызывается без `target_model` и получает неправильный `api_mode` + `base_url`:

| Параметр | Без base_url | С base_url |
|----------|-------------|------------|
| `api_mode` | `anthropic_messages` | `chat_completions` |
| `base_url` | `https://opencode.ai/zen/go` | `https://opencode.ai/zen/go/v1` |

Запрос без `/v1` попадает на Anthropic-совместимый эндпоинт и возвращает 404.

## DeepSeek reasoning

`deepseek-v4-flash` — reasoning-модель. Без `{"thinking":{"type":"disabled"}}` весь ответ кладётся в `reasoning_content`, а `content` остаётся пустым. Hermes-код в `agent/transports/chat_completions.py` автоматически добавляет `thinking:disabled` для провайдера `opencode-go`.

## Проверка работоспособности

```bash
source ~/.hermes/.env
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"OK"}],"max_tokens":10,"thinking":{"type":"disabled"}}'
```

Ожидаемый ответ: `"content":"OK"`, `finish_reason:"stop"`.

## История

- До 2026-05-12: делегирование не работало (HTTP 404, отсутствие `base_url`)
- 2026-05-12, попытка 1: переключено на minimax-m2.5 (работало, но модели пишут хуже)
- 2026-05-12, попытка 2: возвращено на opencode-go + deepseek-v4-flash с явным `base_url` — работает
