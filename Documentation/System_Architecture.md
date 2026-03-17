# System Architecture Document

## High-Level Architecture

- React frontend for CRM workflow and unified OS monitoring
- Flask backend exposing CRM APIs and phase-specific OS simulation APIs
- SQLite database storing CRM data and monitoring metadata

## Component Interaction

- CRM actions trigger process, task, thread, lock, memory, and I/O updates
- Phase-specific managers publish state through a unified dashboard API
- Frontend dashboard refreshes every 2 seconds for near-live monitoring

## Data Flow

- User action -> CRM route -> OS concept manager -> database/log/chart output -> unified dashboard API -> frontend tab view
