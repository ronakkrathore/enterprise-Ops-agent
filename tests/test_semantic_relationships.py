
import pytest
from dataclasses import FrozenInstanceError

from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)

from shared.semantic.models.mappings import ApprovalStatus


@pytest.fixture
def valid_relationship():
    return SemanticRelationship(
        source_id="ecommerce_prod",
        left_schema="main",
        left_table="customers",
        left_column="id",
        right_schema="main",
        right_table="orders",
        right_column="user_id",
        relationship_type=RelationshipType.ONE_TO_MANY,
        relationship_origin=RelationshipOrigin.SCHEMA_DISCOVERED,
        confidence=0.99,
        approval_status=ApprovalStatus.APPROVED
    )


def test_valid_semantic_relationship(valid_relationship):
    assert valid_relationship.source_id == "ecommerce_prod"
    assert valid_relationship.left_table == "customers"
    assert valid_relationship.right_table == "orders"
    assert (
        valid_relationship.relationship_type
        == RelationshipType.ONE_TO_MANY
    )


def test_relationship_type_enum():
    assert RelationshipType.ONE_TO_ONE.value == "one_to_one"
    assert RelationshipType.ONE_TO_MANY.value == "one_to_many"
    assert RelationshipType.MANY_TO_ONE.value == "many_to_one"
    assert RelationshipType.MANY_TO_MANY.value == "many_to_many"


def test_relationship_origin_enum():
    assert RelationshipOrigin.MANUAL.value == "manual"
    assert (
        RelationshipOrigin.SCHEMA_DISCOVERED.value
        == "schema_discovered"
    )
    assert RelationshipOrigin.LLM_SUGGESTED.value == "llm_suggested"


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1, "high", True]
)
def test_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        SemanticRelationship(
            source_id="ecommerce_prod",
            left_schema="main",
            left_table="customers",
            left_column="id",
            right_schema="main",
            right_table="orders",
            right_column="user_id",
            relationship_type=RelationshipType.ONE_TO_MANY,
            relationship_origin=RelationshipOrigin.MANUAL,
            confidence=confidence,
            approval_status=ApprovalStatus.PROPOSED
        )


def test_empty_source_id_is_rejected():
    with pytest.raises(ValueError):
        SemanticRelationship(
            source_id="",
            left_schema="main",
            left_table="customers",
            left_column="id",
            right_schema="main",
            right_table="orders",
            right_column="user_id",
            relationship_type=RelationshipType.ONE_TO_MANY,
            relationship_origin=RelationshipOrigin.MANUAL,
            confidence=0.9,
            approval_status=ApprovalStatus.PROPOSED
        )


def test_relationship_is_immutable(valid_relationship):
    with pytest.raises(FrozenInstanceError):
        valid_relationship.source_id = "another_source"


def test_invalid_relationship_type_is_rejected():
    with pytest.raises(TypeError):
        SemanticRelationship(
            source_id="ecommerce_prod",
            left_schema="main",
            left_table="customers",
            left_column="id",
            right_schema="main",
            right_table="orders",
            right_column="user_id",
            relationship_type="one_to_many",
            relationship_origin=RelationshipOrigin.MANUAL,
            confidence=0.9,
            approval_status=ApprovalStatus.PROPOSED
        )


def test_same_column_relationship_is_rejected():
    with pytest.raises(ValueError):
        SemanticRelationship(
            source_id="ecommerce_prod",
            left_schema="main",
            left_table="customers",
            left_column="id",
            right_schema="main",
            right_table="customers",
            right_column="id",
            relationship_type=RelationshipType.ONE_TO_ONE,
            relationship_origin=RelationshipOrigin.MANUAL,
            confidence=0.9,
            approval_status=ApprovalStatus.PROPOSED
        )
