# Phase 6 - Deadlock Management

This phase adds deadlock handling to the Sales CRM using:

- Resource Allocation Graph (RAG) cycle detection
- Banker's algorithm for safe-state checking
- Deadlock recovery by victim selection and rollback
- Resource monitoring through the Deadlock Monitor dashboard

Key backend files live in `Phase_6_Deadlock_Management/code/`.
The frontend dashboard is available from the app navbar as `Deadlock Monitor`.

Run the full CRM from the project root with:

```bash
python CRM.py
```
