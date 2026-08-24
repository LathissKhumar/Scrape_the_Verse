"""Memory storage and retrieval for successful repair patterns indexed by domain and structural signatures."""

import hashlib
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from leadfinder.config.logging import get_logger
from leadfinder.healing.persistent_memory import PersistentRepairMemory
from leadfinder.healing.schemas import RepairMemoryRecord

logger = get_logger("REPAIR_MEMORY")


class RepairMemory:
    """Stores and retrieves proven successful repair patterns indexed by domain and DOM signatures."""

    def __init__(self, persistent_db_path: str = ".repair_memory.sqlite") -> None:
        self._records: list[RepairMemoryRecord] = []
        self.persistent_storage = PersistentRepairMemory(db_path=persistent_db_path)

    def generate_signature(self, url: str, html: str, fields: list[str]) -> str:
        """Derive a stable, deterministic structural signature representing the target extraction environment."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower() or "unknown_domain"
        path_prefix = "/".join(parsed.path.strip("/").split("/")[:2])

        # Extract top structural tags and repeating classes
        tag_summary: list[str] = []
        class_summary: list[str] = []
        if html:
            try:
                soup = BeautifulSoup(html[:10000], "html.parser")
                for tag in soup.find_all(True)[:50]:
                    tag_summary.append(tag.name)
                    classes = tag.get("class", [])
                    if isinstance(classes, list):
                        class_summary.extend(classes[:3])
            except Exception:
                pass

        tag_str = "-".join(sorted(tag_summary[:20]))
        class_str = "-".join(sorted(list(set(class_summary))[:20]))
        field_str = "-".join(sorted(fields))

        raw_key = f"{domain}:{path_prefix}:{tag_str}:{class_str}:{field_str}"
        sig_hash = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]
        return f"sig_{sig_hash}"

    def record_success(self, record: RepairMemoryRecord) -> None:
        """Save an accepted repair record to memory and persistent SQLite store."""
        logger.debug(
            f"Recording successful repair in memory for domain={record.domain} "
            f"sig={record.signature} type={record.repair_type.value}"
        )
        self._records.append(record)
        self.persistent_storage.record_success(record)

    def find_similar_repairs(
        self,
        domain: str,
        signature: str | None = None,
        root_cause: str | None = None,
    ) -> list[RepairMemoryRecord]:
        """Find relevant successful repair records matching domain, signature, or root cause."""
        clean_domain = domain.lower()
        exact_matches: list[RepairMemoryRecord] = []
        domain_matches: list[RepairMemoryRecord] = []

        # Check in-memory records first
        for rec in self._records:
            if rec.domain.lower() == clean_domain:
                if signature and rec.signature == signature:
                    if root_cause is None or rec.root_cause == root_cause:
                        exact_matches.append(rec)
                else:
                    if root_cause is None or rec.root_cause == root_cause:
                        domain_matches.append(rec)

        # Fallback to persistent SQLite storage if not found in RAM
        if not exact_matches and signature:
            persisted = self.persistent_storage.lookup(clean_domain, signature)
            if persisted:
                exact_matches.append(persisted)
                self._records.append(persisted)

        if exact_matches:
            return exact_matches
        return domain_matches

    def clear(self) -> None:
        """Clear all stored repair memory records."""
        self._records.clear()
