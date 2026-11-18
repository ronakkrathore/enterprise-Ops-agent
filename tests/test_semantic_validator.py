
import pytest

from shared.semantic.validator import validate_semantic_mapping

from shared.semantic.models.mappings import (
    SemanticMapping,
    MappingOrigin,
    ApprovalStatus
)

from shared.semantic.validator import validate_metric_definition

from shared.semantic.models.metrics import (
    AggregationType,
    MetricDefinition
)

from shared.semantic.validator import validate_semantic_relationship

from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)

from shared.semantic.models.mappings import ApprovalStatus
from sqlalchemy import text
from shared.database.connection import get_database_engine
from shared.semantic.validator import validate_relationship_schema

from shared.semantic.validator import validate_relationship_source

def create_mapping(**overrides):
    values = {
        "source_id": "test_source",
        "schema_name": "main",
        "table_name": "customers",
        "column_name": "id",
        "concept_id": "customer.id",
        "confidence": 1.0,
        "mapping_origin": MappingOrigin.MANUAL,
        "approval_status": ApprovalStatus.APPROVED,
        "source_data_type": "INTEGER"
    }

    values.update(overrides)

    return SemanticMapping(**values)


def test_validate_registered_concept():
    mapping = create_mapping()

    assert validate_semantic_mapping(mapping) is None


def test_reject_unknown_concept():
    mapping = create_mapping(
        concept_id="customer.unknown_field"
    )

    with pytest.raises(
        ValueError,
        match="Unknown business concept"
    ):
        validate_semantic_mapping(mapping)


def test_reject_invalid_mapping_type():
    with pytest.raises(TypeError):
        validate_semantic_mapping("not a mapping")


def test_validate_different_registered_concepts():
    concepts = [
        "customer.id",
        "customer.name",
        "order.id",
        "order.status",
        "revenue.amount",
        "product.category"
    ]

    for concept_id in concepts:
        mapping = create_mapping(concept_id=concept_id)

        assert validate_semantic_mapping(mapping) is None


def create_metric(**overrides):
    values = {
        "metric_id": "gross_revenue",
        "name": "Gross Revenue",
        "description": "Total revenue before deductions.",
        "measure_concept_id": "revenue.amount",
        "aggregation": AggregationType.SUM,
        "grain": "order_item",
        "date_concept_id": "order.created_at"
    }

    values.update(overrides)

    return MetricDefinition(**values)


def test_validate_metric_definition():
    metric = create_metric()

    assert validate_metric_definition(metric) is None


def test_validate_metric_without_date_concept():
    metric = create_metric(date_concept_id=None)

    assert validate_metric_definition(metric) is None


def test_reject_metric_with_unknown_measure_concept():
    metric = create_metric(
        measure_concept_id="revenue.unknown"
    )

    with pytest.raises(
        ValueError,
        match="Unknown business concept"
    ):
        validate_metric_definition(metric)


def test_reject_metric_with_unknown_date_concept():
    metric = create_metric(
        date_concept_id="order.unknown_date"
    )

    with pytest.raises(
        ValueError,
        match="Unknown business concept"
    ):
        validate_metric_definition(metric)


def test_reject_invalid_metric_type():
    with pytest.raises(TypeError):
        validate_metric_definition("not a metric")


def create_relationship(**overrides):
    values = {
        "source_id": "test_source",
        "left_schema": "main",
        "left_table": "orders",
        "left_column": "customer_id",
        "right_schema": "main",
        "right_table": "customers",
        "right_column": "id",
        "relationship_type": RelationshipType.MANY_TO_ONE,
        "relationship_origin": RelationshipOrigin.MANUAL,
        "confidence": 1.0,
        "approval_status": ApprovalStatus.APPROVED
    }

    values.update(overrides)

    return SemanticRelationship(**values)


def test_validate_semantic_relationship():
    relationship = create_relationship()

    assert validate_semantic_relationship(relationship) is None


def test_reject_invalid_relationship_type():
    with pytest.raises(TypeError):
        validate_semantic_relationship("not a relationship")

@pytest.fixture
def schema_test_engine(tmp_path):
    database_path = tmp_path / "semantic_validation.duckdb"

    engine = get_database_engine(
        f"duckdb:///{database_path}"
    )

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY
            )
        """))

        connection.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                customer_id INTEGER
            )
        """))

    yield engine
    engine.dispose()


def test_validate_relationship_schema(schema_test_engine):
    relationship = create_relationship()

    assert validate_relationship_schema(
        schema_test_engine,
        relationship
    ) is None


def test_reject_relationship_with_missing_table(schema_test_engine):
    relationship = create_relationship(
        left_table="unknown_table"
    )

    with pytest.raises(
        ValueError,
        match="Table does not exist"
    ):
        validate_relationship_schema(
            schema_test_engine,
            relationship
        )


def test_reject_relationship_with_missing_column(schema_test_engine):
    relationship = create_relationship(
        left_column="unknown_column"
    )

    with pytest.raises(
        ValueError,
        match="Column does not exist"
    ):
        validate_relationship_schema(
            schema_test_engine,
            relationship
        )


def test_reject_invalid_engine():
    relationship = create_relationship()

    with pytest.raises(TypeError):
        validate_relationship_schema(
            "not an engine",
            relationship
        )


def test_validate_relationship_source():
    relationship = create_relationship()

    assert validate_relationship_source(
        relationship,
        "test_source"
    ) is None


def test_reject_relationship_from_different_source():
    relationship = create_relationship(
        source_id="company_A"
    )

    with pytest.raises(
        ValueError,
        match="different data source"
    ):
        validate_relationship_source(
            relationship,
            "company_B"
        )


@pytest.mark.parametrize(
    "source_id",
    ["", "   "]
)
def test_reject_empty_expected_source_id(source_id):
    relationship = create_relationship()

    with pytest.raises(
        ValueError,
        match="expected_source_id"
    ):
        validate_relationship_source(
            relationship,
            source_id
        )


def test_reject_invalid_relationship():
    with pytest.raises(TypeError):
        validate_relationship_source(
            "not a relationship",
            "test_source"
        )
