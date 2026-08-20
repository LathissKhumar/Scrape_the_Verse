import re
from typing import Any, Optional
from app.validation.schemas import SchemaMetric

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}$")
DATE_REGEX = re.compile(
    r"^(?:\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4})$",
    re.IGNORECASE,
)
URL_REGEX = re.compile(r"^https?://[^\s/$.?#].[^\s]*$", re.IGNORECASE)


class TypeValidator:
    """Validates field value types deterministically against schema definitions."""

    def validate_value(self, val: Any, expected_type: str) -> bool:
        """Validate if a value matches expected semantic type."""
        if val is None:
            return True  # nulls handled by completeness validator

        t = expected_type.lower().strip()

        if t in ("string", "str", "text"):
            return isinstance(val, (str, int, float))

        if t in ("integer", "int"):
            if isinstance(val, int) and not isinstance(val, bool):
                return True
            if isinstance(val, str):
                cleaned = val.replace(",", "").strip()
                return cleaned.lstrip("-").isdigit()
            return False

        if t in ("number", "float", "numeric", "decimal"):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return True
            if isinstance(val, str):
                cleaned = re.sub(r"[\$,€£₹\s]", "", val)
                try:
                    float(cleaned)
                    return True
                except ValueError:
                    return False
            return False

        if t in ("boolean", "bool"):
            if isinstance(val, bool):
                return True
            if isinstance(val, str):
                return val.strip().lower() in ("true", "false", "yes", "no", "1", "0")
            return False

        if t == "email":
            return isinstance(val, str) and bool(EMAIL_REGEX.match(val.strip()))

        if t in ("url", "link", "uri"):
            return isinstance(val, str) and bool(URL_REGEX.match(val.strip()))

        if t in ("date", "datetime"):
            return isinstance(val, str) and bool(DATE_REGEX.match(val.strip()))

        if t in ("price", "currency", "cost"):
            if isinstance(val, (int, float)) and not isinstance(val, bool):
                return True
            if isinstance(val, str):
                cleaned = val.strip().lower()
                # Must contain at least one digit
                if not re.search(r"\d", cleaned):
                    return False
                # Slogans and generic buttons without numerical context are invalid
                if cleaned in ("free", "on request", "call for price", "get quote", "सही दाम पर", "best price"):
                    return False
                return True
            return False

        return True

    def validate_records_schema(
        self,
        records: list[dict[str, Any]],
        output_schema: Optional[dict[str, Any]],
        required_fields: Optional[list[str]] = None,
    ) -> SchemaMetric:
        """Assess overall schema conformance across all records."""
        total = len(records)
        if total == 0:
            return SchemaMetric(valid_records=0, invalid_records=0, valid_rate=1.0)

        schema = output_schema or {}
        req_fields = required_fields or list(schema.keys())

        valid_records = 0
        invalid_records = 0
        missing_fields: set[str] = set()

        for r in records:
            record_valid = True
            for f in req_fields:
                if f not in r:
                    missing_fields.add(f)
                    record_valid = False

            for field_name, expected_type in schema.items():
                val = r.get(field_name)
                f_type = str(expected_type)
                if ("price" in field_name.lower() or "cost" in field_name.lower()) and f_type in ("string", "str"):
                    f_type = "price"
                if val is not None and not self.validate_value(val, f_type):
                    record_valid = False

            if record_valid:
                valid_records += 1
            else:
                invalid_records += 1

        valid_rate = round(valid_records / total, 4)

        return SchemaMetric(
            valid_records=valid_records,
            invalid_records=invalid_records,
            valid_rate=valid_rate,
            missing_required_fields=sorted(list(missing_fields)),
        )
