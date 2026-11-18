
from shared.semantic.models.mappings import (
    SemanticMapping,
    ApprovalStatus
)
from dataclasses import replace

class SemanticCatalog:
    """
    Stores and retrieves source-specific semantic mappings.

    This initial implementation uses in-memory storage.
    """

    def __init__(self):
        self._mappings: list[SemanticMapping] = []

    def add_mapping(self, mapping: SemanticMapping) -> None:
        """
        Add a semantic mapping to the catalog.

        An identical mapping is not added twice.
        Conflicting approved mappings for the same source column
        are rejected.
        """

        if not isinstance(mapping, SemanticMapping):
            raise TypeError(
                "mapping must be a SemanticMapping instance."
            )

        if mapping in self._mappings:
            return

        if mapping.approval_status == ApprovalStatus.APPROVED:
            for existing in self._mappings:

                same_source_column = (
                    existing.source_id == mapping.source_id
                    and existing.schema_name == mapping.schema_name
                    and existing.table_name == mapping.table_name
                    and existing.column_name == mapping.column_name
                )

                existing_is_approved = (
                    existing.approval_status == ApprovalStatus.APPROVED
                )

                conflicting_concept = (
                    existing.concept_id != mapping.concept_id
                )

                if (
                    same_source_column
                    and existing_is_approved
                    and conflicting_concept
                ):
                    raise ValueError(
                        "Conflicting approved mappings exist "
                        "for this source column."
                    )

        self._mappings.append(mapping)

    def get_all_mappings(self) -> tuple[SemanticMapping, ...]:
        """Return all mappings as an immutable tuple."""

        return tuple(self._mappings)

    def get_mappings_by_source(
        self,
        source_id: str
    ) -> tuple[SemanticMapping, ...]:
        """Retrieve all mappings belonging to a data source."""

        return tuple(
            mapping
            for mapping in self._mappings
            if mapping.source_id == source_id
        )

    def get_mappings_by_concept(
        self,
        source_id: str,
        concept_id: str
    ) -> tuple[SemanticMapping, ...]:
        """Retrieve mappings for a canonical concept in one source."""

        return tuple(
            mapping
            for mapping in self._mappings
            if (
                mapping.source_id == source_id
                and mapping.concept_id == concept_id
            )
        )

    def get_mapping_by_column(
        self,
        source_id: str,
        schema_name: str,
        table_name: str,
        column_name: str
    ) -> SemanticMapping | None:
        """
        Retrieve an approved mapping for a specific source column.

        Returns None if no approved mapping exists.
        """

        matches = [
            mapping
            for mapping in self._mappings
            if (
                mapping.source_id == source_id
                and mapping.schema_name == schema_name
                and mapping.table_name == table_name
                and mapping.column_name == column_name
                and mapping.approval_status == ApprovalStatus.APPROVED
            )
        ]

        if len(matches) > 1:
            raise ValueError(
                "Multiple approved mappings exist for this source column."
            )

        return matches[0] if matches else None

    def get_mappings_by_status(
        self,
        status: ApprovalStatus
    ) -> tuple[SemanticMapping, ...]:
        """Retrieve mappings by their approval status."""

        return tuple(
            mapping
            for mapping in self._mappings
            if mapping.approval_status == status
        )


    def update_mapping_status(
        self,
        mapping: SemanticMapping,
        new_status: ApprovalStatus
    ) -> SemanticMapping:
        """
        Update the approval status of an existing mapping.

        Returns the updated immutable mapping.
        """

        if mapping not in self._mappings:
            raise ValueError(
                "Mapping does not exist in the catalog."
            )

        if not isinstance(new_status, ApprovalStatus):
            raise TypeError(
                "new_status must be an ApprovalStatus value."
            )

        updated_mapping = replace(
            mapping,
            approval_status=new_status
        )

        # Check for conflicts before approving.
        if new_status == ApprovalStatus.APPROVED:

            for existing in self._mappings:

                same_source_column = (
                    existing.source_id == mapping.source_id
                    and existing.schema_name == mapping.schema_name
                    and existing.table_name == mapping.table_name
                    and existing.column_name == mapping.column_name
                )

                existing_is_approved = (
                    existing.approval_status == ApprovalStatus.APPROVED
                )

                conflicting_concept = (
                    existing.concept_id != mapping.concept_id
                )

                if (
                    same_source_column
                    and existing_is_approved
                    and conflicting_concept
                ):
                    raise ValueError(
                        "Conflicting approved mappings exist "
                        "for this source column."
                    )

        mapping_index = self._mappings.index(mapping)

        self._mappings[mapping_index] = updated_mapping

        return updated_mapping
    