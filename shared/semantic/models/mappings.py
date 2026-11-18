
from dataclasses import dataclass
from enum import Enum


class MappingOrigin(str, Enum):
    """Describes how a semantic mapping was created."""

    MANUAL = "manual"
    RULE_BASED = "rule_based"
    LLM_SUGGESTED = "llm_suggested"


class ApprovalStatus(str, Enum):
    """Describes the review state of a semantic mapping."""

    PROPOSED = "proposed"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


@dataclass(frozen=True)
class SemanticMapping:
    """
    Maps a physical database column to a canonical business concept.

    The mapping is specific to one data source.
    """

    source_id: str
    schema_name: str
    table_name: str
    column_name: str

    concept_id: str

    confidence: float
    mapping_origin: MappingOrigin
    approval_status: ApprovalStatus

    source_data_type: str | None = None

    def __post_init__(self):
        """Validate the mapping's required fields and values."""

        required_fields = {
            "source_id": self.source_id,
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "column_name": self.column_name,
            "concept_id": self.concept_id,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if (
            isinstance(self.confidence, bool)
            or not isinstance(self.confidence, (int, float))
            or not 0.0 <= self.confidence <= 1.0
        ):
            raise ValueError(
                "Confidence must be a number between 0.0 and 1.0."
            )

        if not isinstance(self.mapping_origin, MappingOrigin):
            raise TypeError(
                "mapping_origin must be a MappingOrigin value."
            )

        if not isinstance(self.approval_status, ApprovalStatus):
            raise TypeError(
                "approval_status must be an ApprovalStatus value."
            )

        if (
            self.source_data_type is not None
            and not isinstance(self.source_data_type, str)
        ):
            raise TypeError(
                "source_data_type must be a string or None."
            )
