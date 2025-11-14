const authSection = document.querySelector(".auth-section");
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const authMessage = document.querySelector("#auth-message");
const authStatus = document.querySelector("#auth-status");
const loginTab = document.querySelector("#login-tab");
const registerTab = document.querySelector("#register-tab");
const appContent = document.querySelector("#app-content");
const listContainer = document.querySelector("#lists");
const taskContainer = document.querySelector("#tasks");
const taskTemplate = document.querySelector("#task-item-template");
const currentListTitle = document.querySelector("#current-list-name");
const taskForm = document.querySelector("#task-form");
const tasksMessage = document.querySelector("#tasks-message");

export function setupAuthTabs() {
  loginTab.addEventListener("click", () => switchAuthMode("login"));
  registerTab.addEventListener("click", () => switchAuthMode("register"));
}

function switchAuthMode(mode) {
  const isLogin = mode === "login";
  loginTab.classList.toggle("active", isLogin);
  registerTab.classList.toggle("active", !isLogin);
  loginForm.classList.toggle("active", isLogin);
  registerForm.classList.toggle("active", !isLogin);
  setAuthMessage("");
}

export function setAuthMessage(message, isError = true) {
  authMessage.textContent = message;
  authMessage.style.color = isError ? "#f87171" : "#16a34a";
}

export function setAuthStatus(email) {
  if (email) {
    authStatus.textContent = `Logged in as ${email}`;
  } else {
    authStatus.textContent = "";
  }
}

export function enterAppView() {
  authSection.classList.add("hidden");
  appContent.classList.remove("hidden");
}

export function exitAppView() {
  authSection.classList.remove("hidden");
  appContent.classList.add("hidden");
  setAuthStatus("");
  setAuthMessage("");
  currentListTitle.textContent = "Select a list";
  taskForm.classList.add("hidden");
  renderLists([], null);
  renderTasks([], { onComplete: null, onDelete: null });
}

export function renderLists(lists, currentListId, onSelect) {
  listContainer.innerHTML = "";
  if (!lists.length) {
    const empty = document.createElement("li");
    empty.textContent = "No lists yet. Add one!";
    empty.classList.add("empty");
    listContainer.appendChild(empty);
    return;
  }

  lists.forEach((list) => {
    const item = document.createElement("li");
    item.textContent = list.name;
    item.dataset.id = list.id;
    item.classList.toggle("active", list.id === currentListId);
    item.addEventListener("click", () => onSelect(list));
    listContainer.appendChild(item);
  });
}

export function renderTasks(tasks, { onComplete, onDelete }) {
  taskContainer.innerHTML = "";
  if (!tasks.length) {
    tasksMessage.textContent = "No tasks for this list yet.";
    tasksMessage.style.color = "#64748b";
    return;
  }
  tasksMessage.textContent = "";

  tasks.forEach((task) => {
    const node = taskTemplate.content.firstElementChild.cloneNode(true);
    node.dataset.id = String(task.id);
    node.classList.toggle("completed", task.status === "completed");
    node.querySelector(".task-title").textContent = task.title;
    node.querySelector(".task-description").textContent = task.description || "No description";

    const priorityBadge = node.querySelector(".task-priority");
    priorityBadge.textContent = `${task.priority} priority`;
    priorityBadge.className = `task-priority priority-${task.priority}`;

    const meta = node.querySelector(".task-meta");
    meta.textContent = formatTaskMeta(task);

    const tagsContainer = node.querySelector(".task-tags");
    tagsContainer.innerHTML = "";
    if (Array.isArray(task.tags) && task.tags.length) {
      task.tags.forEach((tag) => {
        const chip = document.createElement("span");
        chip.className = "tag-chip";
        chip.textContent = `#${tag}`;
        tagsContainer.appendChild(chip);
      });
    }

    const completeButton = node.querySelector(".mark-complete");
    completeButton.addEventListener("click", () => onComplete?.(task));
    completeButton.disabled = task.status === "completed";
    if (task.status === "completed") {
      completeButton.textContent = "Completed";
    } else {
      completeButton.textContent = "Mark Complete";
    }

    const deleteButton = node.querySelector(".delete");
    deleteButton.addEventListener("click", () => onDelete?.(task));

    taskContainer.appendChild(node);
  });
}

function formatTaskMeta(task) {
  const due = task.due_date ? new Date(task.due_date).toLocaleDateString() : "No due date";
  const statusLabel = task.status.replace("_", " ");
  return `${statusLabel} • Due ${due}`;
}

export function updateCurrentListTitle(name) {
  currentListTitle.textContent = name;
  if (name) {
    taskForm.classList.remove("hidden");
  } else {
    taskForm.classList.add("hidden");
  }
}

export function clearForm(formElement) {
  formElement.reset();
}

export function setTasksMessage(message, isError = false) {
  tasksMessage.textContent = message;
  tasksMessage.style.color = isError ? "#f87171" : "#64748b";
}

export function updateRealtimeStatus(connected) {
  const indicator = document.querySelector("#realtime-status");
  if (!indicator) return;
  indicator.textContent = connected ? "Live" : "Offline";
  indicator.classList.toggle("connected", connected);
  indicator.classList.toggle("disconnected", !connected);
}

