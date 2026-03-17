# Algorithm Comparison Report

## Typical strengths

- `FCFS`: simple and predictable, but long jobs can delay short urgent work.
- `SJF`: minimizes average waiting time when burst estimates are accurate.
- `PRIORITY`: best when urgent CRM tasks must be executed first.
- `RR`: fair for mixed workloads and improves response time for queued tasks.

## Typical tradeoffs

- `FCFS`: convoy effect
- `SJF`: longer tasks may starve behind many short jobs
- `PRIORITY`: low-priority tasks can starve
- `RR`: context switching overhead grows as the quantum shrinks
