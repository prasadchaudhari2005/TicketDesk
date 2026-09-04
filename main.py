import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DATA_FILE = Path(__file__).parent / "tickets.json"

app = FastAPI(
    title="Ticket Management System",
    description="A lightweight ticket management API using local JSON file storage.",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")


class PriorityEnum(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    URGENT = "Urgent"


class CategoryEnum(str, Enum):
    BUG = "Bug"
    FEATURE = "Feature Request"
    SUPPORT = "Support"
    GENERAL = "General Inquiry"


class TicketCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=100, example="Cannot login to portal")
    description: str = Field(..., min_length=5, max_length=1000, example="Getting 500 error when clicking submit")
    priority: PriorityEnum = PriorityEnum.MEDIUM
    category: CategoryEnum = CategoryEnum.SUPPORT
    created_by: str = Field(default="Anonymous", max_length=50, example="John Doe")


class Ticket(BaseModel):
    id: int
    title: str
    description: str
    priority: PriorityEnum
    category: CategoryEnum
    created_by: str
    status: str
    created_at: str


# Global ID counter
ticket_id_counter: int = 1


def save_tickets_to_storage():
    """Write tickets dictionary to the local JSON file."""
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(tickets_db.values()), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving to {DATA_FILE}: {e}")


def seed_initial_data() -> dict[int, dict]:
    """Seed initial sample tickets and persist to file."""
    global ticket_id_counter
    sample_tickets = [
        {
            "id": 1,
            "title": "Payment Gateway Timeout",
            "description": "Users reporting timeout issues during checkout using credit cards.",
            "priority": PriorityEnum.URGENT.value,
            "category": CategoryEnum.BUG.value,
            "created_by": "Alex Morgan",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "id": 2,
            "title": "Dark Mode Toggle Request",
            "description": "Add dark mode support across the main analytics dashboard.",
            "priority": PriorityEnum.LOW.value,
            "category": CategoryEnum.FEATURE.value,
            "created_by": "Sarah Connor",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "id": 3,
            "title": "Email Notification Delay",
            "description": "Transactional emails are arriving 10-15 minutes later than expected.",
            "priority": PriorityEnum.MEDIUM.value,
            "category": CategoryEnum.SUPPORT.value,
            "created_by": "David Kim",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    ]

    initial_db = {t["id"]: t for t in sample_tickets}
    ticket_id_counter = max(initial_db.keys(), default=0) + 1
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(list(initial_db.values()), f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving initial data: {e}")
    return initial_db


def load_tickets_from_storage() -> dict[int, dict]:
    """Load tickets from local JSON file or create initial seed data if not found."""
    global ticket_id_counter
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    loaded_db = {item["id"]: item for item in data if isinstance(item, dict) and "id" in item}
                elif isinstance(data, dict):
                    loaded_db = {int(k): v for k, v in data.items()}
                else:
                    loaded_db = {}
                
                if loaded_db:
                    ticket_id_counter = max(loaded_db.keys(), default=0) + 1
                    return loaded_db
        except Exception as e:
            print(f"Error reading {DATA_FILE}: {e}")
    
    return seed_initial_data()


# Local storage database
tickets_db: dict[int, dict] = load_tickets_from_storage()


# ---------------- API ROUTES (GET, POST, DELETE) ----------------


@app.get("/", include_in_schema=False)
def serve_ui():
    """Serve the Web UI."""
    return FileResponse("static/index.html")


@app.get("/api/tickets", response_model=list[Ticket], summary="Get all tickets")
def get_all_tickets():
    """Retrieve all tickets from local storage."""
    return list(tickets_db.values())


@app.get("/api/tickets/{ticket_id}", response_model=Ticket, summary="Get ticket by ID")
def get_ticket_by_id(ticket_id: int):
    """Retrieve a single ticket by its ID."""
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found."
        )
    return tickets_db[ticket_id]


@app.post(
    "/api/tickets",
    response_model=Ticket,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticket"
)
def create_ticket(ticket_data: TicketCreate):
    """Create a new ticket and persist it to local storage."""
    global ticket_id_counter
    ticket_id = ticket_id_counter
    ticket_id_counter += 1

    new_ticket = {
        "id": ticket_id,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "priority": ticket_data.priority.value,
        "category": ticket_data.category.value,
        "created_by": ticket_data.created_by or "Anonymous",
        "status": "Open",
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    tickets_db[ticket_id] = new_ticket
    save_tickets_to_storage()
    return new_ticket


@app.delete("/api/tickets/{ticket_id}", status_code=status.HTTP_200_OK, summary="Delete a ticket")
def delete_ticket(ticket_id: int):
    """Delete a ticket from the local storage by its ID."""
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found."
        )
    deleted_ticket = tickets_db.pop(ticket_id)
    save_tickets_to_storage()
    return {
        "message": f"Ticket #{ticket_id} deleted successfully.",
        "ticket": deleted_ticket
    }
