# Phase 2 - Process Management

This phase extends the Phase 1 CRM with operating-system process management concepts.

## OS Concepts Used

- `multiprocessing` creates real child processes for user sessions and background tasks.
- A Process Control Block (PCB) model tracks PID, state, priority, CPU time, parent PID, and ownership.
- State transitions are logged through `NEW -> READY -> RUNNING -> WAITING -> TERMINATED`.
- Background tasks demonstrate `fork()`, `exec()`, `wait()`, and `exit()` style behavior.

## Main Files

- `code/pcb.py`
- `code/process_manager.py`
- `code/process_monitor.py`
- `code/routes/process_routes.py`
- `code/process_validation_test.py`

## Run

Use the project root command:

```bash
python run_phase_2.py
```
