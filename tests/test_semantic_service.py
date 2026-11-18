
import pytest

from shared.semantic.service import SemanticLayer

from shared.semantic.catalog.catalog import SemanticCatalog
from shared.semantic.catalog.relationship_catalog import RelationshipCatalog
from shared.semantic.catalog.metric_catalog import MetricCatalog

from shared.semantic.models.mappings import (
    SemanticMapping,
    MappingOrigin,
    ApprovalStatus
)

from shared.semantic.models.metrics import (
    MetricDefinition,
    AggregationType
)

from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)

@pytest.fixture
def semantic_layer():
    semantic_catalog = SemanticCatalog()
    relationship_catalog = RelationshipCatalog()
    metric_catalog = MetricCatalog()

    return SemanticLayer(
        semantic_catalog=semantic_catalog,
        relationship_catalog=relationship_catalog,
        metric_catalog=metric_catalog
    )


def test_get_approved_mappings(semantic_layer):
    approved_mapping = SemanticMapping(
        source_id="test_db",
        schema_name="main",
        table_name="orders",
        column_name="id",
        concept_id="order.id",
        confidence=1.0,
        mapping_origin=MappingOrigin.MANUAL,
        approval_status=ApprovalStatus.APPROVED
    )

    proposed_mapping = SemanticMapping(
        source_id="test_db",
        schema_name="main",
        table_name="orders",
        column_name="status",
        concept_id="order.status",
        confidence=0.8,
        mapping_origin=MappingOrigin.RULE_BASED,
        approval_status=ApprovalStatus.PROPOSED
    )

    semantic_layer.semantic_catalog.add_mapping(approved_mapping)
    semantic_layer.semantic_catalog.add_mapping(proposed_mapping)

    result = semantic_layer.get_approved_mappings("test_db")

    assert result == (approved_mapping,)


def test_get_approved_mappings_rejects_empty_source_id(
    semantic_layer
):
    with pytest.raises(ValueError):
        semantic_layer.get_approved_mappings("")


def test_get_metric_returns_existing_metric(semantic_layer):
    metric = MetricDefinition(
        metric_id="total_revenue",
        name="Total Revenue",
        description="Total revenue generated",
        measure_concept_id="revenue.amount",
        aggregation=AggregationType.SUM,
        grain="order_item",
        date_concept_id="revenue.transaction_date"
    )

    semantic_layer.metric_catalog.add_metric(metric)

    result = semantic_layer.get_metric("total_revenue")

    assert result == metric


def test_get_metric_returns_none_for_unknown_metric(
    semantic_layer
):
    assert semantic_layer.get_metric("unknown_metric") is None


def test_get_metric_rejects_empty_metric_id(semantic_layer):
    with pytest.raises(ValueError):
        semantic_layer.get_metric("")


def test_resolve_relationship_path(semantic_layer):
    relationship = SemanticRelationship(
        source_id="test_db",
        left_schema="main",
        left_table="orders",
        left_column="user_id",
        right_schema="main",
        right_table="customers",
        right_column="id",
        relationship_type=RelationshipType.MANY_TO_ONE,
        relationship_origin=RelationshipOrigin.MANUAL,
        confidence=1.0,
        approval_status=ApprovalStatus.APPROVED
    )

    semantic_layer.relationship_catalog.add_relationship(
        relationship
    )

    result = semantic_layer.resolve_relationship_path(
        source_id="test_db",
        start_schema="main",
        start_table="orders",
        target_schema="main",
        target_table="customers"
    )

    assert result == (relationship,)


def test_semantic_layer_rejects_invalid_catalog():
    with pytest.raises(TypeError):
        SemanticLayer(
            semantic_catalog=[],
            relationship_catalog=RelationshipCatalog(),
            metric_catalog=MetricCatalog()
        )
