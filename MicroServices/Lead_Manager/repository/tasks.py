"""
Task Repository for Async SQLite.
"""

import json
from typing import Any, Dict, List, Optional
from ..domain.stage import TaskStatus, TaskType
from ..domain.task import LeadTask, utc_now_iso
from .database import DatabaseManager


class TaskRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_task(self, row: Any) -> LeadTask:
        return LeadTask(
            id=row["id"],
            lead_id=row["lead_id"],
            type=row["type"],
            status=TaskStatus(row["status"]),
            due_at=row["due_at"],
            assigned_to=row["assigned_to"],
            title=row["title"],
            description=row["description"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create(self, task: LeadTask) -> LeadTask:
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO tasks (
                    id, lead_id, type, status, due_at, assigned_to,
                    title, description, metadata, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.id,
                    task.lead_id,
                    task.type,
                    task.status.value if hasattr(task.status, "value") else str(task.status),
                    task.due_at,
                    task.assigned_to,
                    task.title,
                    task.description,
                    json.dumps(task.metadata),
                    task.created_at,
                    task.updated_at,
                ),
            )
            await conn.commit()
        return task

    async def get_by_id(self, task_id: str) -> Optional[LeadTask]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_task(row)
            return None

    async def get_by_lead_id(self, lead_id: str) -> List[LeadTask]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM tasks WHERE lead_id = ? ORDER BY created_at DESC",
                (lead_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    async def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        assigned_to: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[LeadTask]:
        query = "SELECT * FROM tasks WHERE 1=1"
        params: List[Any] = []

        if status:
            query += " AND status = ?"
            params.append(status.value if hasattr(status, "value") else str(status))

        if assigned_to:
            query += " AND assigned_to = ?"
            params.append(assigned_to)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with self.db.get_connection() as conn:
            cursor = await conn.execute(query, tuple(params))
            rows = await cursor.fetchall()
            return [self._row_to_task(row) for row in rows]

    async def update_status(
        self, task_id: str, status: TaskStatus, metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[LeadTask]:
        status_str = status.value if hasattr(status, "value") else str(status)
        now_str = utc_now_iso()

        async with self.db.get_connection() as conn:
            if metadata is not None:
                await conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, metadata = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, json.dumps(metadata), now_str, task_id),
                )
            else:
                await conn.execute(
                    """
                    UPDATE tasks
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (status_str, now_str, task_id),
                )
            await conn.commit()

        return await self.get_by_id(task_id)
