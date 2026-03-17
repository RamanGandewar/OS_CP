# SalesCRM

SalesCRM is a full-stack CRM application built phase by phase to demonstrate core Operating System concepts inside a practical business workflow. The project starts with a basic customer and sales pipeline, then incrementally integrates process management, CPU scheduling, thread management, synchronization, deadlock handling, memory management, disk scheduling, and a final unified monitoring dashboard.

The final system combines:
- CRM workflow management for customers, enquiries, quotations, sales orders, invoices, and reports
- Flask backend with SQLite persistence
- React frontend with a unified monitoring experience
- Phase-wise Operating System concept demonstrations tied to real CRM actions
- A single-command launcher for the complete application

## Project Goals

- Build a working CRM instead of isolated OS theory demos
- Map each major Operating System concept to a practical application scenario
- Provide dashboards, analytics, validation scripts, and documentation for every phase
- Keep the project runnable locally with a simple setup and a single launch command

## Tech Stack

- Backend: Python 3, Flask, Flask-SQLAlchemy, SQLite
- Frontend: React.js, Axios, Bootstrap
- OS/Analytics Libraries: multiprocessing, threading, concurrent.futures, psutil, matplotlib, pandas, numpy, networkx
- Final Monitoring Layer: REST APIs with live polling and event-stream support

## Final Features

### CRM Features

- Customer management
- Enquiry creation and tracking
- Quotation generation
- Sales order creation
- Invoice generation
- Reporting and summary counts

### OS Concepts Integrated

- Phase 1: Basic CRM foundation
- Phase 2: Process management with session processes and PCB tracking
- Phase 3: CPU scheduling with FCFS, SJF, Priority, and Round Robin
- Phase 4: Thread management with worker threads, daemon threads, and thread pools
- Phase 5: Synchronization using mutexes, semaphores, reader-writer locks, and producer-consumer patterns
- Phase 6: Deadlock detection, avoidance, and recovery with RAG and Banker's Algorithm
- Phase 7: Memory management with paging, page replacement, caching, and allocation strategies
- Phase 8: I/O and disk scheduling with FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK
- Phase 9: Unified integration dashboard for complete system monitoring

## Directory Structure

```text
Code/
|-- Backend/
|   |-- app.py
|   |-- requirements.txt
|   |-- database/
|   |-- models/
|   |-- routes/
|   `-- utils/
|-- Frontend/
|   |-- package.json
|   |-- public/
|   `-- src/
|       |-- components/
|       |-- pages/
|       `-- utils/
|-- Phase_1_Basic_CRM/
|-- Phase_2_Process_Management/
|-- Phase_3_CPU_Scheduling/
|-- Phase_4_Thread_Management/
|-- Phase_5_Synchronization/
|-- Phase_6_Deadlock_Management/
|-- Phase_7_Memory_Management/
|-- Phase_8_IO_Management/
|-- Phase_9_Integration_Dashboard/
|-- Documentation/
|-- scripts/
|-- CRM.py
`-- README.md
```

## Phase Breakdown

### Phase 1 - Basic CRM

- Core Flask and React application structure
- Database schema for users, customers, enquiries, quotations, sales orders, and invoices
- CRUD APIs and list views
- Initial reports and seed data

### Phase 2 - Process Management

- Separate user session processes
- Process Control Block model
- Process state tracking and transition logs
- Process monitor dashboard

### Phase 3 - CPU Scheduling

- Background task queue
- FCFS, SJF, Priority, and Round Robin scheduling
- Gantt chart generation
- Scheduler analytics and comparison metrics

### Phase 4 - Thread Management

- Auto-save, validation, notification, report, and sync threads
- Thread pool with worker reuse
- Thread monitor dashboard
- Thread-safe execution and lifecycle tracking

### Phase 5 - Synchronization

- Mutex locking for quotation editing
- Semaphore-based access control
- Reader-writer coordination
- Producer-consumer demo and race-condition monitoring

### Phase 6 - Deadlock Management

- Resource Allocation Graph construction
- Deadlock cycle detection
- Safe-state evaluation with Banker's Algorithm
- Deadlock recovery and victim rollback

### Phase 7 - Memory Management

- Paging for large reports
- FIFO, LRU, and Optimal page replacement
- LRU-style caching
- First Fit, Best Fit, Worst Fit, and Next Fit allocation strategies

### Phase 8 - I/O Management

- Disk request scheduling
- FCFS, SSTF, SCAN, C-SCAN, LOOK, and C-LOOK algorithms
- I/O buffering
- Print spooling and queue management

### Phase 9 - Final Integration Dashboard

- Unified dashboard across all prior phases
- Consolidated overview and system metrics
- CSV export and performance report generation
- Final integration analytics and documentation templates

## Backend Modules

- `Backend/app.py`
  Main Flask application, blueprint registration, database setup, and health endpoint.

- `Backend/models/`
  All SQLAlchemy models used by CRM modules and OS monitoring features.

- `Backend/routes/`
  Core CRM and reporting APIs.

- `Phase_*/*/routes/`
  Phase-specific REST APIs for processes, scheduling, threads, synchronization, deadlock, memory, I/O, and dashboard aggregation.

## Frontend Modules

- `Frontend/src/App.js`
  Application routing.

- `Frontend/src/components/Layout.js`
  Global application shell and navigation.

- `Frontend/src/pages/`
  CRM pages and per-phase monitoring pages.

- `Frontend/src/components/integration/`
  Final unified dashboard tab views for Phase 9.

- `Frontend/src/utils/api.js`
  Shared Axios API client and module-specific API helpers.

## Database Coverage

The project includes CRM tables and OS-monitoring tables, including:

- `users`
- `customers`
- `enquiries`
- `quotations`
- `sales_orders`
- `invoices`
- `processes`
- `tasks`
- `threads`
- `locks`
- `lock_queue`
- `resources`
- `resource_allocation`
- `deadlock_events`
- `memory_pages`
- `cache_stats`
- `disk_requests`
- `print_queue`

## Setup Instructions

### 1. Backend Setup

```powershell
cd Backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python database\seed_data.py
```

### 2. Frontend Setup

```powershell
cd Frontend
npm install
```

### 3. Run the Full Application

From the project root:

```powershell
python CRM.py
```

This starts:
- Backend: `http://127.0.0.1:5000`
- Frontend: `http://localhost:3000`

## Default Demo Access

At the moment, the frontend is configured to go directly to the application dashboard using a demo user flow. Seeded credentials still exist in the database if authentication is re-enabled later.

Example seeded account:
- Username: `user1`
- Password: `password123`

## Final Dashboard Coverage

The unified dashboard includes:

- Overview tab
- Process monitor tab
- Task scheduler tab
- Thread monitor tab
- Synchronization monitor tab
- Deadlock detector tab
- Memory monitor tab
- I/O monitor tab

It also supports:
- Auto-refresh
- Analytics generation
- CSV export
- Performance report export
- Light and dark theme switching

## Validation and Testing

Validation scripts are included phase-wise inside each phase folder. These cover:

- Process creation and cleanup
- Scheduler comparisons
- Thread pool execution
- Synchronization safety
- Deadlock detection and recovery
- Memory algorithm validation
- Disk scheduling validation
- Final dashboard integration validation

The final integration validation script is:

`Phase_9_Integration_Dashboard/code/final_validation_test.py`

## Outputs and Analytics

Each phase contains:

- `code/` for implementation files
- `output/` for generated logs, charts, exports, and screenshots
- `analytics/` for reports, comparisons, and analysis artifacts

This keeps the project submission organized and allows each concept to be reviewed independently.

## Documentation

The `Documentation/` folder contains:

- System Architecture
- OS Concepts Mapping
- User Manual
- Performance Analysis
- Developer Documentation

These files summarize:
- architecture and data flow
- where each OS concept is used
- how to run and operate the system
- performance impact of the integrated OS techniques
- codebase and deployment notes

## Deployment and Utility Scripts

Available helper scripts include:

- `CRM.py`
  Single-command launcher for backend and frontend

- `scripts/run_final_dashboard.ps1`
  Helper for final integrated execution flow

- `scripts/generate_final_artifacts.ps1`
  Helper for generating report artifacts and outputs

## What Still Needs Final Manual Completion

The codebase is ready, but some deliverables are naturally manual or presentation-oriented and should be completed by running the app and capturing results:

- Final screenshots for every dashboard tab
- Video walkthrough or demo recording
- Final benchmark screenshots
- Presentation slides
- Any instructor-specific formatting for reports or exports

## Recommended Submission Checklist

- Run backend seed script successfully
- Launch the project with `python CRM.py`
- Verify all dashboard tabs load
- Generate analytics and export reports
- Capture screenshots for each phase and the final dashboard
- Review files in `Documentation/`
- Package the complete folder structure for submission

## Project Summary

SalesCRM is both a CRM application and an Operating Systems laboratory project. Instead of treating OS concepts as disconnected exercises, the project demonstrates how processes, scheduling, threads, synchronization, deadlock control, memory handling, and disk scheduling can all be applied inside one realistic software system.
