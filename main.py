from datetime import datetime
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

app = FastAPI(
    title="Ticket Management System",
    description="A lightweight ticket management API using in-memory dictionary storage.",
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


# In-memory dictionary storage: {ticket_id: ticket_dict}
tickets_db: dict[int, dict] = {}
ticket_id_counter: int = 1


def seed_initial_data():
    global ticket_id_counter
    sample_tickets = [
        {
            "title": "Payment Gateway Timeout",
            "description": "Users reporting timeout issues during checkout using credit cards.",
            "priority": PriorityEnum.URGENT.value,
            "category": CategoryEnum.BUG.value,
            "created_by": "Alex Morgan",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "title": "Dark Mode Toggle Request",
            "description": "Add dark mode support across the main analytics dashboard.",
            "priority": PriorityEnum.LOW.value,
            "category": CategoryEnum.FEATURE.value,
            "created_by": "Sarah Connor",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
        {
            "title": "Email Notification Delay",
            "description": "Transactional emails are arriving 10-15 minutes later than expected.",
            "priority": PriorityEnum.MEDIUM.value,
            "category": CategoryEnum.SUPPORT.value,
            "created_by": "David Kim",
            "status": "Open",
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        },
    ]

    for item in sample_tickets:
        ticket_id = ticket_id_counter
        item["id"] = ticket_id
        tickets_db[ticket_id] = item
        ticket_id_counter += 1


# Seed sample tickets on startup
seed_initial_data()


# ---------------- API ROUTES (GET, POST, DELETE) ----------------


@app.get("/", include_in_schema=False)
def serve_ui():
    """Serve the Web UI."""
    return FileResponse("static/index.html")


@app.get("/api/tickets", response_model=list[Ticket], summary="Get all tickets")
def get_all_tickets():
    """Retrieve all tickets from the dictionary."""
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
    """Create a new ticket and store it in the in-memory dictionary."""
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
    return new_ticket


@app.delete("/api/tickets/{ticket_id}", status_code=status.HTTP_200_OK, summary="Delete a ticket")
def delete_ticket(ticket_id: int):
    """Delete a ticket from the dictionary by its ID."""
    if ticket_id not in tickets_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket with ID {ticket_id} not found."
        )
    deleted_ticket = tickets_db.pop(ticket_id)
    return {
        "message": f"Ticket #{ticket_id} deleted successfully.",
        "ticket": deleted_ticket
    }
