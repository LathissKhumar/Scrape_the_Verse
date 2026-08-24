"""
Lead Repository for Async SQLite.
"""

import json
from typing import Any

from ..domain.lead import Lead, utc_now_iso
from ..domain.stage import LeadStage
from .database import DatabaseManager


class LeadRepository:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_lead(self, row: Any) -> Lead:
        return Lead(
            id=row["id"],
            campaign_id=row["campaign_id"],
            company_name=row["company_name"],
            industry=row["industry"],
            location=row["location"],
            website_url=row["website_url"],
            primary_contact_name=row["primary_contact_name"],
            primary_contact_email=row["primary_contact_email"],
            primary_contact_phone=row["primary_contact_phone"],
            stage=LeadStage(row["stage"]),
            fit_score=row["fit_score"],
            opportunity_score=row["opportunity_score"],
            recommended_services=json.loads(row["recommended_services"])
            if row["recommended_services"]
            else [],
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            source=row["source"] or "leadfinder",
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )

    async def create(self, lead: Lead) -> Lead:
        async with self.db.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO leads (
                    id, campaign_id, company_name, industry, location,
                    website_url, primary_contact_name, primary_contact_email,
                    primary_contact_phone, stage, fit_score, opportunity_score,
                    recommended_services, metadata, source, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    lead.id,
                    lead.campaign_id,
                    lead.company_name,
                    lead.industry,
                    lead.location,
                    lead.website_url,
                    lead.primary_contact_name,
                    lead.primary_contact_email,
                    lead.primary_contact_phone,
                    lead.stage.value
                    if hasattr(lead.stage, "value")
                    else str(lead.stage),
                    lead.fit_score,
                    lead.opportunity_score,
                    json.dumps(lead.recommended_services),
                    json.dumps(lead.metadata),
                    lead.source,
                    lead.created_at,
                    lead.updated_at,
                ),
            )
            await conn.commit()
        return lead

    async def get_by_id(self, lead_id: str) -> Lead | None:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
            row = await cursor.fetchone()
            if row:
                return self._row_to_lead(row)
            return None

    async def get_by_email(self, email: str) -> Lead | None:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT * FROM leads WHERE primary_contact_email = ? LIMIT 1", (email,)
            )
            row = await cursor.fetchone()
            if row:
                return self._row_to_lead(row)
            return None

    async def update_stage(self, lead_id: str, new_stage: LeadStage) -> Lead | None:
        stage_str = new_stage.value if hasattr(new_stage, "value") else str(new_stage)
        now_str = utc_now_iso()
        async with self.db.get_connection() as conn:
            await conn.execute(
                "UPDATE leads SET stage = ?, updated_at = ? WHERE id = ?",
                (stage_str, now_str, lead_id),
            )
            await conn.commit()
        return await self.get_by_id(lead_id)

    async def update(self, lead_id: str, updates: dict[str, Any]) -> Lead | None:
        if not updates:
            return await self.get_by_id(lead_id)

        updates["updated_at"] = utc_now_iso()
        set_clauses = []
        values = []

        for key, val in updates.items():
            if key in ("recommended_services", "metadata") and isinstance(
                val, (dict, list)
            ):
                val = json.dumps(val)
            elif key == "stage" and hasattr(val, "value"):
                val = val.value
            set_clauses.append(f"{key} = ?")
            values.append(val)

        values.append(lead_id)
        query = f"UPDATE leads SET {', '.join(set_clauses)} WHERE id = ?"

        async with self.db.get_connection() as conn:
            await conn.execute(query, tuple(values))
            await conn.commit()

        return await self.get_by_id(lead_id)

    async def list_all(
        self,
        stage: LeadStage | None = None,
        campaign_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Lead]:
        query = "SELECT * FROM leads WHERE 1=1"
        params: list[Any] = []

        if stage:
            stage_str = stage.value if hasattr(stage, "value") else str(stage)
            query += " AND stage = ?"
            params.append(stage_str)

        if campaign_id:
            query += " AND campaign_id = ?"
            params.append(campaign_id)

        query += " ORDER BY updated_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        async with self.db.get_connection() as conn:
            cursor = await conn.execute(query, tuple(params))
            rows = await cursor.fetchall()
            return [self._row_to_lead(row) for row in rows]

    async def get_pipeline_counts(self) -> dict[str, int]:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute(
                "SELECT stage, COUNT(*) as count FROM leads GROUP BY stage"
            )
            rows = await cursor.fetchall()
            counts = {stage.value: 0 for stage in LeadStage}
            for row in rows:
                counts[row["stage"]] = row["count"]
            return counts

    async def delete(self, lead_id: str) -> bool:
        async with self.db.get_connection() as conn:
            cursor = await conn.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
            await conn.commit()
            return cursor.rowcount > 0
