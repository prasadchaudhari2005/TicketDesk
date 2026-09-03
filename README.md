# 🎫 TicketDesk - Ticket Management System

A lightweight, high-performance Ticket Management System built using **FastAPI** and **uv**. It uses an in-memory Python dictionary for storage and provides a responsive, dark-mode Web UI alongside clean REST API routes (`GET`, `POST`, `DELETE`).

---

## Features

- **FastAPI & UV**: Ultra-fast Python backend managed with modern `uv` tooling.
- **In-Memory Storage**: Simple, zero-setup dictionary-based persistence.
- **Interactive Web UI**: Modern dark-mode dashboard with real-time stats, live search, and priority badges.
- **Simple REST API**: Clean endpoints for managing tickets:
  - `GET /api/tickets` - List all tickets
  - `GET /api/tickets/{id}` - Get ticket details
  - `POST /api/tickets` - Create a new ticket
  - `DELETE /api/tickets/{id}` - Delete a ticket
- **Interactive API Docs**: Built-in Swagger UI at `/docs`.

---

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/prasadchaudhari2005/TicketDesk.git
cd TicketDesk
```

### 2. Run with UV
```bash
uv run fastapi dev main.py
```
*or using uvicorn:*
```bash
uv run uvicorn main:app --reload --port 8000
```

### 3. Open in Browser
- **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
- **Swagger Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
