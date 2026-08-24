"""
Opportunity Repository for Async SQLite.
"""

import json
from typing import Any

from ..domain.opportunity import Opportunity
from .database import DatabaseManager


class OpportunityRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_opp(self, row: Any) -> Opportunity:
        return Opportunity(
            id=row["id"],
            lead_id=row["lead_id"],
            type=row["type"],
            score=row["score"],
            problem_summary=row["problem_summary"],
            evidence=json.loads(row["evidence"]) if row["evidence"] else [],
            recommended=bool(row["recommended"]),
            status=row["status"],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=row["created_at"],
        )

    async def create(self, opp: Opportunity) -> Opportunity:
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO opportunities (
                    id, lead_id, type, score, problem_summary,
                    evidence, recommended, status, metadata, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    opp.id,
                    opp.lead_id,
                    opp.type,
                    opp.score,
                    opp.problem_summary,
                    json.dumps(opp.evidence),
                    1 if opp.recommended else 0,
                    opp.status,
                    json.dumps(opp.metadata),
                    opp.created_at,
                ),
            )
            await conn.commit()
        return opp

    async def bulk_create(self, opportunities: list[Opportunity]) -> list[Opportunity]:
        if not opportunities:
            return []

        async with self.db.get_connection() as conn:
            for opp in opportunities:
                await conn.execute(
                    """
                    INSERT INTO opportunities (
                        id, lead_id, type, score, problem_summary,
                        evidence, recommended, status, metadata, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        opp.id,
                        opp.lead_id,
                        opp.type,
                        opp.score,
                        opp.problem_summary,
                        json.dumps(opp.evidence),
                        1 if opp.recommended else 0,
                        opp.status,
                        json.dumps(opp.metadata),
                        opp.created_at,
                    ),
                )
            await conn.commit()
        return opportunities

    async def get_by_lead_id(self, lead_id: str) -> list[Opportunity]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM opportunities WHERE lead_id = ? ORDER BY score DESC",
                (lead_id,),
            )
            rows = await cursor.fetchall()
            return [self._row_to_opp(row) for row in rows]

    async def get_by_id(self, opp_id: str) -> Opportunity | None:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM opportunities WHERE id = ?", (opp_id,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_opp(row)
            return None
