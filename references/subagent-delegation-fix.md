# delegate_task + opencode-go: critical config fix

## Symptom

`delegate_task` returns HTTP 404 `/chat/completions` or empty `content` responses, even though the API key is valid and direct curl works fine.

## Root causes (two independent)

### Cause 1: Missing delegation.base_url in config.yaml

`_resolve_delegation_credentials` is called **without** `target_model`, so for provider `opencode-go` it sets:
- `api_mode = anthropic_messages` (wrong)
- `base_url = https://opencode.ai/zen/go` (missing `/v1`)

The request hits the wrong endpoint → 404 + HTML error page.

### Cause 2: reasoning model without thinking disabled

`deepseek-v4-flash` is a reasoning model. Without `{"thinking":{"type":"disabled"}}`, the entire response lands in `reasoning_content` and `content` stays empty. Hermes receives an empty string → parse error.

## Fix (both required)

In `~/.hermes/config.yaml`, set the **top-level `delegation`** section:

```yaml
delegation:
  model: deepseek-v4-flash
  provider: opencode-go
  base_url: 'https://opencode.ai/zen/go/v1'   # ← critical: must include /v1
  api_key: ''                                  # ← empty; resolves from .env
  inherit_mcp_toolsets: true
  max_iterations: 50
  child_timeout_seconds: 900
  reasoning_effort: low
  max_concurrent_children: 3
```

In `~/.hermes/.env`:

```bash
OPENCODE_GO_API_KEY=sk-...        # must match the key used for direct curl
OPENAI_API_KEY=sk-...             # same key, different env var name
```

**Why `base_url` in the delegation section fixes it:** When `delegation.base_url` is non-empty, `_resolve_delegation_credentials` is bypassed entirely. The subagent receives the correct `base_url`, `api_mode = chat_completions`, and the request goes to the right endpoint immediately.

## Pre-flight verification (run before launching NFP)

```bash
source ~/.hermes/.env
curl -s -X POST https://opencode.ai/zen/go/v1/chat/completions \
  -H "Authorization: Bearer $OPENCODE_GO_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-v4-flash","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10,"thinking":{"type":"disabled"}}'
```

Expected: `"content":"OK"`, `finish_reason":"stop"`.

If `"content":""` + `finish_reason:"length"` → reasoning model not receiving `thinking:disabled`. If AuthError → wrong key in .env.

## Timeline

- 2026-05-02: root cause identified (delegation.base_url empty → wrong endpoint)
- Fix confirmed: adding `base_url: 'https://opencode.ai/zen/go/v1'` resolves the 404
