# Process State Transition Diagram

```text
NEW -> READY -> RUNNING -> WAITING -> RUNNING -> TERMINATED
  \_______________________________________________^
```

- `NEW`: process object created
- `READY`: waiting in the ready queue
- `RUNNING`: assigned CPU time
- `WAITING`: blocked or idle
- `TERMINATED`: graceful or forced cleanup
