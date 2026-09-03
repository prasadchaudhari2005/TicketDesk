// API Base URL
const API_BASE = '/api/tickets';

// State
let tickets = [];

// DOM Elements
const ticketsGrid = document.getElementById('tickets-grid');
const emptyState = document.getElementById('empty-state');
const ticketModal = document.getElementById('ticket-modal');
const createTicketForm = document.getElementById('create-ticket-form');
const searchInput = document.getElementById('search-input');
const priorityFilter = document.getElementById('priority-filter');
const categoryFilter = document.getElementById('category-filter');
const refreshBtn = document.getElementById('refresh-btn');
const openModalBtn = document.getElementById('open-modal-btn');
const closeModalBtn = document.getElementById('close-modal-btn');
const cancelBtn = document.getElementById('cancel-btn');
const emptyCreateBtn = document.getElementById('empty-create-btn');

// Stat Elements
const statTotal = document.getElementById('stat-total');
const statUrgent = document.getElementById('stat-urgent');
const statMedium = document.getElementById('stat-medium');
const statLow = document.getElementById('stat-low');

// Init
document.addEventListener('DOMContentLoaded', () => {
  fetchTickets();
  bindEvents();
});

function bindEvents() {
  // Modal handlers
  openModalBtn.addEventListener('click', () => openModal());
  emptyCreateBtn.addEventListener('click', () => openModal());
  closeModalBtn.addEventListener('click', () => closeModal());
  cancelBtn.addEventListener('click', () => closeModal());
  
  ticketModal.addEventListener('click', (e) => {
    if (e.target === ticketModal) closeModal();
  });

  // Form submission (POST /api/tickets)
  createTicketForm.addEventListener('submit', handleCreateTicket);

  // Search & Filter handlers
  searchInput.addEventListener('input', renderFilteredTickets);
  priorityFilter.addEventListener('change', renderFilteredTickets);
  categoryFilter.addEventListener('change', renderFilteredTickets);
  refreshBtn.addEventListener('click', fetchTickets);
}

// ---------------- API FUNCTIONS ----------------

// GET /api/tickets
async function fetchTickets() {
  try {
    const res = await fetch(API_BASE);
    if (!res.ok) throw new Error('Failed to fetch tickets');
    tickets = await res.json();
    updateStats();
    renderFilteredTickets();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

// POST /api/tickets
async function handleCreateTicket(e) {
  e.preventDefault();
  const submitBtn = document.getElementById('submit-ticket-btn');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Saving...';

  const payload = {
    title: document.getElementById('title').value.trim(),
    description: document.getElementById('description').value.trim(),
    priority: document.getElementById('priority').value,
    category: document.getElementById('category').value,
    created_by: document.getElementById('created_by').value.trim() || 'Anonymous'
  };

  try {
    const res = await fetch(API_BASE, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail ? JSON.stringify(err.detail) : 'Failed to create ticket');
    }

    const createdTicket = await res.json();
    showToast(`Ticket #${createdTicket.id} created successfully!`, 'success');
    closeModal();
    createTicketForm.reset();
    fetchTickets();
  } catch (error) {
    showToast(error.message, 'error');
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = 'Submit Ticket';
  }
}

// DELETE /api/tickets/{id}
async function deleteTicket(id) {
  if (!confirm(`Are you sure you want to delete Ticket #${id}?`)) return;

  try {
    const res = await fetch(`${API_BASE}/${id}`, {
      method: 'DELETE'
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'Failed to delete ticket');
    }

    showToast(`Ticket #${id} deleted.`, 'info');
    fetchTickets();
  } catch (error) {
    showToast(error.message, 'error');
  }
}

// ---------------- RENDER & STATS ----------------

function updateStats() {
  statTotal.textContent = tickets.length;
  
  const urgentCount = tickets.filter(t => t.priority === 'Urgent' || t.priority === 'High').length;
  const mediumCount = tickets.filter(t => t.priority === 'Medium').length;
  const lowCount = tickets.filter(t => t.priority === 'Low').length;

  statUrgent.textContent = urgentCount;
  statMedium.textContent = mediumCount;
  statLow.textContent = lowCount;
}

function renderFilteredTickets() {
  const query = searchInput.value.toLowerCase().trim();
  const selectedPriority = priorityFilter.value;
  const selectedCategory = categoryFilter.value;

  const filtered = tickets.filter(ticket => {
    const matchQuery = !query || 
      ticket.title.toLowerCase().includes(query) ||
      ticket.description.toLowerCase().includes(query) ||
      (ticket.created_by && ticket.created_by.toLowerCase().includes(query)) ||
      `#${ticket.id}`.includes(query);

    const matchPriority = selectedPriority === 'ALL' || ticket.priority === selectedPriority;
    const matchCategory = selectedCategory === 'ALL' || ticket.category === selectedCategory;

    return matchQuery && matchPriority && matchCategory;
  });

  if (filtered.length === 0) {
    ticketsGrid.innerHTML = '';
    emptyState.classList.remove('hidden');
    return;
  }

  emptyState.classList.add('hidden');
  // Render cards sorted descending by ID (newest first)
  const sorted = [...filtered].sort((a, b) => b.id - a.id);
  
  ticketsGrid.innerHTML = sorted.map(ticket => `
    <div class="ticket-card priority-${ticket.priority}">
      <div>
        <div class="ticket-header">
          <span class="ticket-id">#${ticket.id}</span>
          <button class="btn btn-danger-outline" onclick="deleteTicket(${ticket.id})">
            Delete
          </button>
        </div>
        <h3 class="ticket-title">${escapeHtml(ticket.title)}</h3>
        <div class="ticket-badges">
          <span class="badge badge-priority-${ticket.priority}">● ${ticket.priority}</span>
          <span class="badge badge-category">${escapeHtml(ticket.category)}</span>
        </div>
        <p class="ticket-desc">${escapeHtml(ticket.description)}</p>
      </div>

      <div class="ticket-footer">
        <div class="ticket-meta">
          <span>By <strong class="ticket-author">${escapeHtml(ticket.created_by || 'Anonymous')}</strong></span>
          <span>${ticket.created_at}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// ---------------- HELPERS ----------------

function openModal() {
  ticketModal.classList.remove('hidden');
  document.getElementById('title').focus();
}

function closeModal() {
  ticketModal.classList.add('hidden');
}

function showToast(message, type = 'info') {
  const toastContainer = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function escapeHtml(str) {
  if (!str) return '';
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}
