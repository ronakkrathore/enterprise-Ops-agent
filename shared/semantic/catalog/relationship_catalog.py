
from shared.semantic.models.relationships import (
    SemanticRelationship
)

from shared.semantic.models.mappings import ApprovalStatus
from dataclasses import replace

class RelationshipCatalog:
    """
    Stores and retrieves source-specific semantic relationships.

    This initial implementation uses in-memory storage.
    """

    def __init__(self):
        self._relationships: list[SemanticRelationship] = []

    
    def add_relationship(
        self,
        relationship: SemanticRelationship
    ) -> None:
        """Add a relationship unless its physical endpoints already exist."""

        if not isinstance(relationship, SemanticRelationship):
            raise TypeError(
                "relationship must be a SemanticRelationship instance."
            )

        for existing in self._relationships:
            same_relationship = (
                existing.source_id == relationship.source_id
                and existing.left_schema == relationship.left_schema
                and existing.left_table == relationship.left_table
                and existing.left_column == relationship.left_column
                and existing.right_schema == relationship.right_schema
                and existing.right_table == relationship.right_table
                and existing.right_column == relationship.right_column
            )

            if same_relationship:
                return

        self._relationships.append(relationship)


    def get_all_relationships(
        self
    ) -> tuple[SemanticRelationship, ...]:
        """Return all relationships as an immutable tuple."""

        return tuple(self._relationships)

    def get_relationships_by_source(
        self,
        source_id: str
    ) -> tuple[SemanticRelationship, ...]:
        """Retrieve relationships belonging to a data source."""

        return tuple(
            relationship
            for relationship in self._relationships
            if relationship.source_id == source_id
        )

    def get_relationships_by_table(
        self,
        source_id: str,
        schema_name: str,
        table_name: str
    ) -> tuple[SemanticRelationship, ...]:
        """
        Retrieve approved relationships connected to a table.

        The table can appear on either side of the relationship.
        """

        return tuple(
            relationship
            for relationship in self._relationships
            if (
                relationship.source_id == source_id
                and relationship.approval_status == ApprovalStatus.APPROVED
                and (
                    (
                        relationship.left_schema == schema_name
                        and relationship.left_table == table_name
                    )
                    or
                    (
                        relationship.right_schema == schema_name
                        and relationship.right_table == table_name
                    )
                )
            )
        )

    def get_approved_relationships(
        self,
        source_id: str
    ) -> tuple[SemanticRelationship, ...]:
        """Retrieve approved relationships for a data source."""

        return tuple(
            relationship
            for relationship in self._relationships
            if (
                relationship.source_id == source_id
                and relationship.approval_status == ApprovalStatus.APPROVED
            )
        )


    def update_relationship_status(
        self,
        relationship: SemanticRelationship,
        new_status: ApprovalStatus
    ) -> SemanticRelationship:
        """
        Update the approval status of an existing relationship.

        Returns the updated immutable relationship.
        """

        if relationship not in self._relationships:
            raise ValueError(
                "Relationship does not exist in the catalog."
            )

        if not isinstance(new_status, ApprovalStatus):
            raise TypeError(
                "new_status must be an ApprovalStatus value."
            )

        updated_relationship = replace(
            relationship,
            approval_status=new_status
        )

        relationship_index = self._relationships.index(relationship)

        self._relationships[relationship_index] = updated_relationship

        return updated_relationship
