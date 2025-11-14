const DEFAULT_BASE_URL = "http://localhost:8000";

export class ApiClient {
  constructor(baseUrl = DEFAULT_BASE_URL) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.token = null;
  }

  setToken(token) {
    this.token = token;
  }

  async register({ email, password, fullName }) {
    const payload = { email, password, full_name: fullName };
    return this._request("/api/register", {
      method: "POST",
      body: payload,
      includeAuth: false,
    });
  }

  async login({ email, password }) {
    return this._request("/api/login", {
      method: "POST",
      body: { email, password },
      includeAuth: false,
    });
  }

  async getLists() {
    return this._request("/api/lists", { method: "GET" });
  }

  async createList(name) {
    return this._request("/api/lists", {
      method: "POST",
      body: { name },
    });
  }

  async getTasks(listId) {
    return this._request(`/api/lists/${listId}/tasks`, { method: "GET" });
  }

  async createTask(listId, task) {
    return this._request(`/api/lists/${listId}/tasks`, {
      method: "POST",
      body: task,
    });
  }

  async updateTask(taskId, updates) {
    return this._request(`/api/tasks/${taskId}`, {
      method: "PUT",
      body: updates,
    });
  }

  async deleteTask(taskId) {
    return this._request(`/api/tasks/${taskId}`, {
      method: "DELETE",
    });
  }

  async reorderTasks(listId, taskIds) {
    return this._request(`/api/lists/${listId}/tasks/reorder`, {
      method: "PUT",
      body: { task_ids: taskIds },
    });
  }

  async _request(path, options) {
    const { method = "GET", body, includeAuth = true } = options;
    const headers = {
      Accept: "application/json",
      ...(body ? { "Content-Type": "application/json" } : {}),
    };

    if (includeAuth) {
      if (!this.token) {
        throw new Error("Authentication token missing");
      }
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (response.status === 204) {
      return null;
    }

    const contentType = response.headers.get("Content-Type") || "";
    const isJson = contentType.includes("application/json");
    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
      const detail = isJson && data && data.detail ? data.detail : response.statusText;
      throw new Error(typeof detail === "string" ? detail : "Request failed");
    }

    return data;
  }
}

