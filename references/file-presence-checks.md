# File presence checks

Use this when a user asks whether a manuscript/file is "on place", exists, or was changed on disk.

## Recommended checks

```bash
# exact existence
test -f /root/hermes-nonfiction-pipeline/derzhava-ahemenidov/manuscript.md && echo present || echo missing

# details
ls -l /root/hermes-nonfiction-pipeline/derzhava-ahemenidov/manuscript.md
stat /root/hermes-nonfiction-pipeline/derzhava-ahemenidov/manuscript.md

# if path might be stale, inspect project root
pwd
ls -la /root/hermes-nonfiction-pipeline/derzhava-ahemenidov/
```

## Rules

- Verify the exact filesystem path, not the task list or memory.
- If the file is missing, report that plainly and include the exact path checked.
- If the file exists, report presence plus any useful status (size, mtime) only after confirming with a tool.
- For edited manuscripts, prefer `stat` or `ls -l` before concluding the file is current.
