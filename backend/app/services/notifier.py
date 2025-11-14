from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import Any

from fastapi import WebSocket


class TaskNotifier:
    def __init__(self) -> None:
        self._connections: dict[int, set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, list_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[list_id].add(websocket)

    async def disconnect(self, list_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            connections = self._connections.get(list_id)
            if connections and websocket in connections:
                connections.remove(websocket)
                if not connections:
                    self._connections.pop(list_id, None)

    async def broadcast(self, list_id: int, message: dict[str, Any]) -> None:
        async with self._lock:
            connections = list(self._connections.get(list_id, set()))

        stale_connections: list[WebSocket] = []
        for websocket in connections:
            try:
                await websocket.send_json(message)
            except Exception:
                stale_connections.append(websocket)

        if stale_connections:
            async with self._lock:
                remaining = self._connections.get(list_id)
                if not remaining:
                    return
                for websocket in stale_connections:
                    remaining.discard(websocket)
                if not remaining:
                    self._connections.pop(list_id, None)

