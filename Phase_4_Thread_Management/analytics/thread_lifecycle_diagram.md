# Thread Lifecycle Diagram

```text
READY -> RUNNING -> COMPLETED
  |         |
  |         -> WAITING (timer / auto-save / notification sleep)
  |
  -> TERMINATED
```
