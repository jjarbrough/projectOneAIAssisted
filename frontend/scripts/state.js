const TOKEN_STORAGE_KEY = "tasktrack/token";

export const state = {
  token: null,
  lists: [],
  tasksByList: new Map(),
  currentListId: null,
  realtime: {
    connected: false,
    socket: null,
  },
};

export function initializeState() {
  const storedToken = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  if (storedToken) {
    state.token = storedToken;
  }
}

export function setToken(token) {
  state.token = token;
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
  } else {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}

export function setLists(lists) {
  state.lists = lists;
}

export function setCurrentList(listId) {
  state.currentListId = listId;
}

export function setTasks(listId, tasks) {
  state.tasksByList.set(listId, tasks);
}

export function getTasks(listId) {
  return state.tasksByList.get(listId) ?? [];
}

export function resetState() {
  state.lists = [];
  state.tasksByList.clear();
  state.currentListId = null;
  setToken(null);
  state.realtime.connected = false;
  if (state.realtime.socket) {
    try {
      state.realtime.socket.close();
    } catch (error) {
      console.warn("Error closing socket", error);
    }
  }
  state.realtime.socket = null;
}

