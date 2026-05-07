# Resource-Safe Mode

Trigger `sequential-safe` when you observe:
- repeated child timeouts;
- high CPU/RAM pressure;
- unstable delegation/provider behavior;
- very heavy research per chapter;
- user request for careful one-chapter-at-a-time work.

Resource-safe posture:
- single-agent or low-parallelism only;
- no Kanban;
- no background workers unless strictly necessary;
- save after each chapter or revision stage;
- keep the active working set small.

User-facing status line:

```md
Перехожу в безопасный последовательный режим: один активный этап, без Kanban и без массовой параллельности.
```
