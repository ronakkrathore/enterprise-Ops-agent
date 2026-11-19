from shared.semantic.vocabulary.registry import get_concept
from shared.semantic.models.mappings import SemanticMapping
from shared.semantic.models.metrics import (
    MetricDefinition,
    DerivedMetricDefinition,
    MetricReference,
    BinaryMetricExpression
)

from shared.semantic.catalog.metric_catalog import MetricCatalog
from shared.semantic.models.relationships import SemanticRelationship
from sqlalchemy.engine import Engine

from shared.database.schema_inspector import (
    get_table_names,
    get_table_columns
)



def validate_semantic_mapping(mapping: SemanticMapping) -> None:
    """
    Validate that a semantic mapping references
    a registered canonical business concept.
    """

    if not isinstance(mapping, SemanticMapping):
        raise TypeError(
            "mapping must be a SemanticMapping instance."
        )

    try:
        get_concept(mapping.concept_id)
    except KeyError as exc:
        raise ValueError(
            f"Unknown business concept: {mapping.concept_id}"
        ) from exc


def validate_metric_definition(metric: MetricDefinition) -> None:
    """
    Validate that a metric references registered
    canonical business concepts.
    """

    if not isinstance(metric, MetricDefinition):
        raise TypeError(
            "metric must be a MetricDefinition instance."
        )

    concept_ids = [metric.measure_concept_id]

    if metric.date_concept_id is not None:
        concept_ids.append(metric.date_concept_id)

    # Include concepts referenced by metric filters.
    concept_ids.extend(
        metric_filter.concept_id
        for metric_filter in metric.filters
    )

    for concept_id in concept_ids:
        try:
            get_concept(concept_id)
        except KeyError as exc:
            raise ValueError(
                f"Unknown business concept: {concept_id}"
            ) from exc


def validate_derived_metric_definition(
    metric: DerivedMetricDefinition,
    catalog: MetricCatalog
) -> None:
    """
    Validate references and detect circular dependencies
    in a derived metric's dependency chain.
    """

    if not isinstance(metric, DerivedMetricDefinition):
        raise TypeError(
            "metric must be a DerivedMetricDefinition instance."
        )

    if not isinstance(catalog, MetricCatalog):
        raise TypeError(
            "catalog must be a MetricCatalog instance."
        )

    visited = set()
    active_path = set()

    def visit(current_metric: DerivedMetricDefinition) -> None:
        metric_id = current_metric.metric_id

        if metric_id in active_path:
            raise ValueError(
                f"Detected circular dependency involving: {metric_id}"
            )

        if metric_id in visited:
            return

        active_path.add(metric_id)

        references = (
            current_metric.expression.left,
            current_metric.expression.right
        )

        for reference in references:

            if reference.metric_id == metric_id:
                raise ValueError(
                    "A derived metric cannot reference itself."
                )

            referenced_metric = catalog.get_metric(
                reference.metric_id
            )

            if referenced_metric is None:
                raise ValueError(
                    f"Referenced metric does not exist: "
                    f"{reference.metric_id}"
                )

            if isinstance(
                referenced_metric,
                DerivedMetricDefinition
            ):
                visit(referenced_metric)

        active_path.remove(metric_id)
        visited.add(metric_id)

    visit(metric)


def validate_semantic_relationship(
    relationship: SemanticRelationship
) -> None:
    """
    Validate the type of a semantic relationship.
    """

    if not isinstance(relationship, SemanticRelationship):
        raise TypeError(
            "relationship must be a SemanticRelationship instance."
        )

def validate_relationship_schema(
    engine: Engine,
    relationship: SemanticRelationship
) -> None:
    """
    Validate that both endpoints of a relationship
    exist in the connected database schema.
    """

    if not isinstance(engine, Engine):
        raise TypeError("engine must be a SQLAlchemy Engine.")

    validate_semantic_relationship(relationship)

    tables = get_table_names(engine)

    available_tables = {
        (table["schema"], table["name"])
        for table in tables
        if table["object_type"] == "BASE TABLE"
    }

    endpoints = [
        (
            relationship.left_schema,
            relationship.left_table,
            relationship.left_column
        ),
        (
            relationship.right_schema,
            relationship.right_table,
            relationship.right_column
        )
    ]

    for schema_name, table_name, column_name in endpoints:

        if (schema_name, table_name) not in available_tables:
            raise ValueError(
                f"Table does not exist: {schema_name}.{table_name}"
            )

        columns = get_table_columns(
            engine,
            table_name,
            schema_name
        )

        available_columns = {
            column["name"]
            for column in columns
        }

        if column_name not in available_columns:
            raise ValueError(
                f"Column does not exist: "
                f"{schema_name}.{table_name}.{column_name}"
            )


def validate_relationship_source(
    relationship: SemanticRelationship,
    expected_source_id: str
) -> None:
    """
    Ensure a relationship belongs to the expected data source.
    """

    validate_semantic_relationship(relationship)

    if (
        not isinstance(expected_source_id, str)
        or not expected_source_id.strip()
    ):
        raise ValueError(
            "expected_source_id must be a non-empty string."
        )

    if relationship.source_id != expected_source_id:
        raise ValueError(
            "Relationship belongs to a different data source."
        )
