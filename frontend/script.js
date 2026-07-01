
const API_URL = window.location.hostname === "localhost"
  ? "http://localhost:5000"
  : "https://todo-api-t0vn.onrender.com"; 

// ── Estado ──────────────────────────────────────────────────────────────────
let allTasks = [];
let currentFilter = "";

// ── Referencias al DOM ───────────────────────────────────────────────────────
const form = document.getElementById("task-form");
const formError = document.getElementById("form-error");
const taskList = document.getElementById("task-list");
const emptyState = document.getElementById("empty-state");
const apiStatus = document.getElementById("api-status");
const filterButtons = document.querySelectorAll(".filter-btn");
const todayDateEl = document.getElementById("today-date");

// ── Inicialización ───────────────────────────────────────────────────────────
todayDateEl.textContent = new Date().toLocaleDateString("es-AR", {
  day: "2-digit", month: "2-digit", year: "numeric"
});

checkApiHealth();
loadTasks();

// ── Conexión con la API ──────────────────────────────────────────────────────
async function checkApiHealth() {
  try {
    const res = await fetch(`${API_URL}/`);
    if (res.ok) {
      apiStatus.textContent = "conectada ✓";
      apiStatus.style.color = "var(--green-stamp)";
    } else {
      throw new Error("respuesta no OK");
    }
  } catch (err) {
    apiStatus.textContent = "sin conexión ✗";
    apiStatus.style.color = "var(--red-stamp)";
  }
}

async function loadTasks() {
  try {
    const url = currentFilter
      ? `${API_URL}/tasks?status=${currentFilter}`
      : `${API_URL}/tasks`;
    const res = await fetch(url);
    allTasks = await res.json();
    renderTasks();
  } catch (err) {
    taskList.innerHTML = `<p class="empty-state">No se pudo conectar con la API. Verificá que el backend esté corriendo.</p>`;
  }
}

// ── Crear tarea ───────────────────────────────────────────────────────────────
form.addEventListener("submit", async (e) => {
  e.preventDefault();
  formError.hidden = true;

  const payload = {
    title: document.getElementById("title").value,
    priority: document.getElementById("priority").value,
    due_date: document.getElementById("due_date").value || null,
    description: document.getElementById("description").value,
  };

  try {
    const res = await fetch(`${API_URL}/tasks`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();

    if (!res.ok) {
      const errors = data.errors || [data.error] || ["Error desconocido"];
      formError.textContent = errors.join(" ");
      formError.hidden = false;
      return;
    }

    form.reset();
    document.getElementById("priority").value = "media";
    await loadTasks();
  } catch (err) {
    formError.textContent = "No se pudo conectar con la API.";
    formError.hidden = false;
  }
});

// ── Filtros ───────────────────────────────────────────────────────────────────
filterButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    filterButtons.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    currentFilter = btn.dataset.filter;
    loadTasks();
  });
});

// ── Render ────────────────────────────────────────────────────────────────────
function renderTasks() {
  if (allTasks.length === 0) {
    taskList.innerHTML = "";
    taskList.appendChild(emptyState);
    emptyState.hidden = false;
    return;
  }

  emptyState.hidden = true;
  taskList.innerHTML = allTasks.map(taskCardHTML).join("");

  // Bind de acciones
  taskList.querySelectorAll("[data-action]").forEach((btn) => {
    btn.addEventListener("click", () => handleAction(btn.dataset.action, btn.dataset.id));
  });
}

function taskCardHTML(task) {
  const dueLabel = task.due_date ? `Vence: ${task.due_date}` : "Sin fecha";
  const canComplete = task.status === "pendiente";
  const canCancel = task.status === "pendiente";

  return `
    <article class="task-card" data-status="${task.status}">
      <span class="task-priority ${task.priority}">${task.priority}</span>
      <div class="task-main">
        <p class="task-title">${escapeHTML(task.title)}</p>
        ${task.description ? `<p class="task-desc">${escapeHTML(task.description)}</p>` : ""}
        <div class="task-meta">
          <span class="task-status-badge ${task.status}">${task.status}</span>
          <span>${dueLabel}</span>
        </div>
      </div>
      <div class="task-actions">
        <button data-action="complete" data-id="${task.id}" ${canComplete ? "" : "disabled"}>Completar</button>
        <button data-action="cancel" data-id="${task.id}" ${canCancel ? "" : "disabled"}>Cancelar</button>
        <button class="btn-delete" data-action="delete" data-id="${task.id}">Eliminar</button>
      </div>
    </article>
  `;
}

async function handleAction(action, id) {
  try {
    if (action === "complete") {
      await fetch(`${API_URL}/tasks/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "completada" }),
      });
    } else if (action === "cancel") {
      await fetch(`${API_URL}/tasks/${id}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: "cancelada" }),
      });
    } else if (action === "delete") {
      await fetch(`${API_URL}/tasks/${id}`, { method: "DELETE" });
    }
    await loadTasks();
  } catch (err) {
    alert("No se pudo completar la acción. Verificá la conexión con la API.");
  }
}

// ── Utilidad ──────────────────────────────────────────────────────────────────
function escapeHTML(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
