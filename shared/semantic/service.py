
from shared.semantic.catalog.catalog import SemanticCatalog
from shared.semantic.catalog.relationship_catalog import RelationshipCatalog
from shared.semantic.catalog.metric_catalog import MetricCatalog
from shared.semantic.relationship_resolver import resolve_join_path


class SemanticLayer:
    """
    Central service coordinating semantic catalogs
    for a particular analytical data source.
    """

    
    def __init__(
        self,
        semantic_catalog: SemanticCatalog,
        relationship_catalog: RelationshipCatalog,
        metric_catalog: MetricCatalog
    ):
        if not isinstance(semantic_catalog, SemanticCatalog):
            raise TypeError(
                "semantic_catalog must be a SemanticCatalog instance."
            )

        if not isinstance(relationship_catalog, RelationshipCatalog):
            raise TypeError(
                "relationship_catalog must be a RelationshipCatalog instance."
            )

        if not isinstance(metric_catalog, MetricCatalog):
            raise TypeError(
                "metric_catalog must be a MetricCatalog instance."
            )

        self.semantic_catalog = semantic_catalog
        self.relationship_catalog = relationship_catalog
        self.metric_catalog = metric_catalog



    def get_approved_mappings(
        self,
        source_id: str
    ):
        """
        Retrieve all approved semantic mappings
        belonging to a data source.
        """

        from shared.semantic.models.mappings import ApprovalStatus

        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(
                "source_id must be a non-empty string."
            )

        mappings = self.semantic_catalog.get_mappings_by_source(
            source_id
        )

        return tuple(
            mapping
            for mapping in mappings
            if mapping.approval_status == ApprovalStatus.APPROVED
        )


    def get_metric(
        self,
        metric_id: str
    ):
        """
        Retrieve a metric definition by its identifier.
        """

        if not isinstance(metric_id, str) or not metric_id.strip():
            raise ValueError(
                "metric_id must be a non-empty string."
            )

        return self.metric_catalog.get_metric(metric_id)


    def resolve_relationship_path(
        self,
        source_id: str,
        start_schema: str,
        start_table: str,
        target_schema: str,
        target_table: str
    ):
        """
        Resolve an approved relationship path between two tables.
        """

        if not isinstance(source_id, str) or not source_id.strip():
            raise ValueError(
                "source_id must be a non-empty string."
            )

        return resolve_join_path(
            catalog=self.relationship_catalog,
            source_id=source_id,
            start_schema=start_schema,
            start_table=start_table,
            target_schema=target_schema,
            target_table=target_table
        )
