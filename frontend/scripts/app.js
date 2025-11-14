import { ApiClient } from "./apiClient.js";
import {
  state,
  initializeState,
  setToken,
  setLists,
  setCurrentList,
  setTasks,
  getTasks,
  resetState,
} from "./state.js";
import {
  setupAuthTabs,
  setAuthMessage,
  setAuthStatus,
  enterAppView,
  exitAppView,
  renderLists,
  renderTasks,
  updateCurrentListTitle,
  clearForm,
  setTasksMessage,
  updateRealtimeStatus,
} from "./ui.js";

const apiClient = new ApiClient();

const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const listForm = document.querySelector("#list-form");
const taskForm = document.querySelector("#task-form");
const logoutButton = document.querySelector("#logout-button");
const tasksListElement = document.querySelector("#tasks");

const dragState = {
  draggedId: null,
};

setupAuthTabs();
initializeState();
setupDragAndDrop();
updateRealtimeStatus(false);

if (state.token) {
  apiClient.setToken(state.token);
  setAuthStatus("restored session");
  loadInitialData();
}

loginForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(loginForm);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
  };

  try {
    const token = await apiClient.login(payload);
    setToken(token.access_token);
    apiClient.setToken(token.access_token);
    setAuthStatus(payload.email);
    setAuthMessage("Successfully logged in.", false);
    enterAppView();
    await loadInitialData();
    clearForm(loginForm);
  } catch (error) {
    setAuthMessage(error.message || "Unable to login.");
  }
});

registerForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(registerForm);
  const payload = {
    email: formData.get("email"),
    password: formData.get("password"),
    fullName: formData.get("fullName"),
  };

  try {
    const token = await apiClient.register(payload);
    setToken(token.access_token);
    apiClient.setToken(token.access_token);
    setAuthStatus(payload.email);
    setAuthMessage("Account created and logged in.", false);
    enterAppView();
    await loadInitialData();
    clearForm(registerForm);
  } catch (error) {
    setAuthMessage(error.message || "Unable to register.");
  }
});

logoutButton.addEventListener("click", () => {
  resetState();
  apiClient.setToken(null);
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
    reconnectTimer = null;
  }
  updateRealtimeStatus(false);
  exitAppView();
});

listForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const name = new FormData(listForm).get("name");
  try {
    const newList = await apiClient.createList(name);
    const lists = [...state.lists, newList];
    setLists(lists);
    renderLists(lists, state.currentListId, handleListSelect);
    clearForm(listForm);
    setTasksMessage("");
  } catch (error) {
    setTasksMessage(error.message || "Could not create list.", true);
  }
});

taskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.currentListId) {
    setTasksMessage("Select a list before adding tasks.", true);
    return;
  }
  const formData = new FormData(taskForm);
  const taskPayload = {
    title: formData.get("title"),
    description: formData.get("description"),
    due_date: formData.get("due_date") || null,
    status: formData.get("status"),
    priority: formData.get("priority"),
    tags: parseTags(formData.get("tags")),
  };

  try {
    const newTask = await apiClient.createTask(state.currentListId, taskPayload);
    const tasks = [...getTasks(state.currentListId), newTask];
    setTasks(state.currentListId, tasks);
    renderTasks(tasks, taskHandlers);
    clearForm(taskForm);
    setTasksMessage("");
  } catch (error) {
    setTasksMessage(error.message || "Could not create task.", true);
  }
});

const taskHandlers = {
  onComplete: async (task) => {
    try {
      const updated = await apiClient.updateTask(task.id, { status: "completed" });
      const tasks = getTasks(state.currentListId).map((t) => (t.id === task.id ? updated : t));
      setTasks(state.currentListId, tasks);
      renderTasks(tasks, taskHandlers);
      setTasksMessage("");
    } catch (error) {
      setTasksMessage(error.message || "Unable to update task.", true);
    }
  },
  onDelete: async (task) => {
    try {
      await apiClient.deleteTask(task.id);
      const tasks = getTasks(state.currentListId).filter((t) => t.id !== task.id);
      setTasks(state.currentListId, tasks);
      renderTasks(tasks, taskHandlers);
      setTasksMessage("");
    } catch (error) {
      setTasksMessage(error.message || "Unable to delete task.", true);
    }
  },
};

async function loadInitialData() {
  try {
    enterAppView();
    const lists = await apiClient.getLists();
    setLists(lists);
    renderLists(lists, state.currentListId, handleListSelect);
    if (lists.length) {
      handleListSelect(lists[0]);
    }
  } catch (error) {
    setAuthMessage(error.message || "Unable to load data.");
  }
}

async function handleListSelect(list) {
  setCurrentList(list.id);
  updateCurrentListTitle(list.name);
  renderLists(state.lists, state.currentListId, handleListSelect);
  await loadTasksForList(list.id);
  connectRealtime(list.id);
}

async function loadTasksForList(listId) {
  try {
    const tasks = await apiClient.getTasks(listId);
    setTasks(listId, tasks);
    renderTasks(tasks, taskHandlers);
    setTasksMessage("");
  } catch (error) {
    setTasksMessage(error.message || "Unable to load tasks.", true);
  }
}

function parseTags(value) {
  if (!value) {
    return [];
  }
  return value
    .split(",")
    .map((tag) => tag.trim())
    .filter(Boolean);
}

let reconnectTimer = null;

function connectRealtime(listId) {
  if (!state.token) {
    updateRealtimeStatus(false);
    return;
  }
  if (state.realtime.socket) {
    state.realtime.socket.close();
  }
  const wsUrl = buildWebSocketUrl(listId);
  const socket = new WebSocket(wsUrl);
  state.realtime.socket = socket;

  socket.addEventListener("open", () => {
    state.realtime.connected = true;
    updateRealtimeStatus(true);
  });

  socket.addEventListener("message", (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data?.type === "tasks_changed" && data.list_id === state.currentListId) {
        loadTasksForList(state.currentListId);
      }
    } catch (error) {
      console.warn("Failed to parse realtime message", error);
    }
  });

  socket.addEventListener("close", () => {
    state.realtime.connected = false;
    updateRealtimeStatus(false);
    if (state.currentListId === listId) {
      scheduleReconnect(listId);
    }
  });

  socket.addEventListener("error", () => {
    socket.close();
  });
}

function scheduleReconnect(listId) {
  if (reconnectTimer) {
    clearTimeout(reconnectTimer);
  }
  reconnectTimer = setTimeout(() => {
    if (state.currentListId === listId) {
      connectRealtime(listId);
    }
  }, 2500);
}

function buildWebSocketUrl(listId) {
  const base = apiClient.baseUrl.replace(/^http/i, "ws");
  const token = encodeURIComponent(state.token);
  return `${base}/api/ws/lists/${listId}?token=${token}`;
}

function setupDragAndDrop() {
  if (!tasksListElement) return;

  tasksListElement.addEventListener("dragstart", (event) => {
    const item = event.target.closest(".task-item");
    if (!item) return;
    dragState.draggedId = item.dataset.id;
    event.dataTransfer.effectAllowed = "move";
    event.dataTransfer.setData("text/plain", dragState.draggedId);
  });

  tasksListElement.addEventListener("dragover", (event) => {
    event.preventDefault();
    const item = event.target.closest(".task-item");
    if (!item || item.dataset.id === dragState.draggedId) return;
    item.classList.add("drag-over");
  });

  tasksListElement.addEventListener("dragleave", (event) => {
    const item = event.target.closest(".task-item");
    if (item) {
      item.classList.remove("drag-over");
    }
  });

  tasksListElement.addEventListener("drop", async (event) => {
    event.preventDefault();
    const target = event.target.closest(".task-item");
    const draggedId = dragState.draggedId;
    dragState.draggedId = null;
    if (!target || !draggedId) return;
    target.classList.remove("drag-over");
    if (target.dataset.id === draggedId) return;

    const draggedElement = tasksListElement.querySelector(`[data-id="${draggedId}"]`);
    if (!draggedElement) return;

    const targetRect = target.getBoundingClientRect();
    const shouldInsertBefore = event.clientY < targetRect.top + targetRect.height / 2;
    if (shouldInsertBefore) {
      tasksListElement.insertBefore(draggedElement, target);
    } else {
      tasksListElement.insertBefore(draggedElement, target.nextSibling);
    }

    const orderedIds = Array.from(tasksListElement.querySelectorAll(".task-item")).map((el) =>
      Number(el.dataset.id),
    );

    try {
      const updatedTasks = await apiClient.reorderTasks(state.currentListId, orderedIds);
      setTasks(state.currentListId, updatedTasks);
      renderTasks(updatedTasks, taskHandlers);
      setTasksMessage("");
    } catch (error) {
      setTasksMessage(error.message || "Unable to reorder tasks.", true);
      await loadTasksForList(state.currentListId);
    }
  });

  tasksListElement.addEventListener("dragend", () => {
    dragState.draggedId = null;
    tasksListElement.querySelectorAll(".drag-over").forEach((el) => el.classList.remove("drag-over"));
  });
}

