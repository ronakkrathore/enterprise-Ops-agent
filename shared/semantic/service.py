
from shared.semantic.catalog.catalog import SemanticCatalog
from shared.semantic.catalog.relationship_catalog import RelationshipCatalog
from shared.semantic.catalog.metric_catalog import MetricCatalog
from shared.semantic.relationship_resolver import resolve_join_path
from shared.semantic.models.metrics import (
    MetricDefinition,
    DerivedMetricDefinition
)

from shared.semantic.validator import (
    validate_metric_definition,
    validate_derived_metric_definition
)

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
        self._validate_existing_metrics()


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
    ) -> MetricDefinition | DerivedMetricDefinition | None:
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

    def register_metric(
        self,
        metric: MetricDefinition | DerivedMetricDefinition
    ) -> None:
        """
        Validate and register a semantic metric.
        """

        if isinstance(metric, MetricDefinition):
            validate_metric_definition(metric)

        elif isinstance(metric, DerivedMetricDefinition):
            validate_derived_metric_definition(
                metric,
                self.metric_catalog
            )

        else:
            raise TypeError(
                "metric must be a MetricDefinition or "
                "DerivedMetricDefinition instance."
            )

        self.metric_catalog.add_metric(metric)

    def _validate_existing_metrics(self) -> None:
        """Validate all metrics already present in the catalog."""

        metrics = self.metric_catalog.get_all_metrics()

        # Validate atomic definitions first.
        for metric in metrics:
            if isinstance(metric, MetricDefinition):
                validate_metric_definition(metric)

        # Then validate derived definitions and their dependencies.
        for metric in metrics:
            if isinstance(metric, DerivedMetricDefinition):
                validate_derived_metric_definition(
                    metric,
                    self.metric_catalog
                )