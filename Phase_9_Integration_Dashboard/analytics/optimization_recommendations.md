# Optimization Recommendations

- Prefer low-seek disk scheduling strategies like SSTF or LOOK when request locality is high.
- Increase memory frames if page faults remain higher than page hits under report workloads.
- Review lock contention hotspots whenever the synchronization wait queue grows persistently.
- Use the unified dashboard alerts panel as the first checkpoint during live demos.