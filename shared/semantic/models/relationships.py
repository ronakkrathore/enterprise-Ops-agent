
from dataclasses import dataclass
from enum import Enum

from shared.semantic.models.mappings import ApprovalStatus


class RelationshipType(str, Enum):
    """Describes cardinality between two tables."""

    ONE_TO_ONE = "one_to_one"
    ONE_TO_MANY = "one_to_many"
    MANY_TO_ONE = "many_to_one"
    MANY_TO_MANY = "many_to_many"


class RelationshipOrigin(str, Enum):
    """Describes how a relationship was discovered."""

    MANUAL = "manual"
    SCHEMA_DISCOVERED = "schema_discovered"
    LLM_SUGGESTED = "llm_suggested"


@dataclass(frozen=True)
class SemanticRelationship:
    """
    Represents a relationship between two database columns.

    Relationships are specific to a data source.
    """

    source_id: str

    left_schema: str
    left_table: str
    left_column: str

    right_schema: str
    right_table: str
    right_column: str

    relationship_type: RelationshipType
    relationship_origin: RelationshipOrigin
    confidence: float
    approval_status: ApprovalStatus

    def __post_init__(self):
        """Validate relationship fields."""

        required_fields = {
            "source_id": self.source_id,
            "left_schema": self.left_schema,
            "left_table": self.left_table,
            "left_column": self.left_column,
            "right_schema": self.right_schema,
            "right_table": self.right_table,
            "right_column": self.right_column,
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

        if not isinstance(
            self.relationship_type,
            RelationshipType
        ):
            raise TypeError(
                "relationship_type must be a RelationshipType value."
            )

        if not isinstance(
            self.relationship_origin,
            RelationshipOrigin
        ):
            raise TypeError(
                "relationship_origin must be a RelationshipOrigin value."
            )

        if not isinstance(
            self.approval_status,
            ApprovalStatus
        ):
            raise TypeError(
                "approval_status must be an ApprovalStatus value."
            )

        if (
            self.left_schema == self.right_schema
            and self.left_table == self.right_table
            and self.left_column == self.right_column
        ):
            raise ValueError(
                "A relationship cannot connect a column to itself."
            )
