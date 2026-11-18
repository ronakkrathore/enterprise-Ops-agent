
import pytest

from shared.semantic.catalog.relationship_catalog import (
    RelationshipCatalog
)

from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)

from shared.semantic.models.mappings import ApprovalStatus


@pytest.fixture
def catalog():
    return RelationshipCatalog()


def create_relationship(
    source_id="ecommerce_prod",
    left_schema="main",
    left_table="customers",
    left_column="id",
    right_schema="main",
    right_table="orders",
    right_column="user_id",
    status=ApprovalStatus.APPROVED
):
    return SemanticRelationship(
        source_id=source_id,
        left_schema=left_schema,
        left_table=left_table,
        left_column=left_column,
        right_schema=right_schema,
        right_table=right_table,
        right_column=right_column,
        relationship_type=RelationshipType.ONE_TO_MANY,
        relationship_origin=RelationshipOrigin.SCHEMA_DISCOVERED,
        confidence=0.99,
        approval_status=status
    )


def test_add_relationship(catalog):
    relationship = create_relationship()

    catalog.add_relationship(relationship)

    assert len(catalog.get_all_relationships()) == 1


def test_duplicate_relationship_is_not_added(catalog):
    relationship = create_relationship()

    catalog.add_relationship(relationship)
    catalog.add_relationship(relationship)

    assert len(catalog.get_all_relationships()) == 1


def test_get_relationships_by_source(catalog):
    relationship_a = create_relationship(
        source_id="ecommerce_prod"
    )

    relationship_b = create_relationship(
        source_id="crm_prod",
        left_table="client_master",
        right_table="sales"
    )

    catalog.add_relationship(relationship_a)
    catalog.add_relationship(relationship_b)

    results = catalog.get_relationships_by_source("crm_prod")

    assert len(results) == 1
    assert results[0].source_id == "crm_prod"


def test_get_relationships_by_left_table(catalog):
    relationship = create_relationship()

    catalog.add_relationship(relationship)

    results = catalog.get_relationships_by_table(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="customers"
    )

    assert len(results) == 1


def test_get_relationships_by_right_table(catalog):
    relationship = create_relationship()

    catalog.add_relationship(relationship)

    results = catalog.get_relationships_by_table(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="orders"
    )

    assert len(results) == 1


def test_unapproved_relationship_is_not_returned_by_table_lookup(
    catalog
):
    relationship = create_relationship(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(relationship)

    results = catalog.get_relationships_by_table(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="customers"
    )

    assert len(results) == 0


def test_get_approved_relationships(catalog):
    approved = create_relationship()

    proposed = create_relationship(
        left_table="products",
        left_column="id",
        right_table="order_items",
        right_column="product_id",
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(approved)
    catalog.add_relationship(proposed)

    results = catalog.get_approved_relationships(
        "ecommerce_prod"
    )

    assert len(results) == 1
    assert results[0] == approved


def test_catalog_rejects_invalid_relationship(catalog):
    with pytest.raises(TypeError):
        catalog.add_relationship("not a relationship")


def test_same_table_name_in_different_schemas(catalog):
    relationship_a = create_relationship(
        left_schema="sales",
        left_table="customers"
    )

    relationship_b = create_relationship(
        left_schema="archive",
        left_table="customers",
        right_table="historical_orders"
    )

    catalog.add_relationship(relationship_a)
    catalog.add_relationship(relationship_b)

    results = catalog.get_relationships_by_table(
        source_id="ecommerce_prod",
        schema_name="archive",
        table_name="customers"
    )

    assert len(results) == 1
    assert results[0] == relationship_b


def test_update_proposed_relationship_to_approved(catalog):
    relationship = create_relationship(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(relationship)

    updated = catalog.update_relationship_status(
        relationship,
        ApprovalStatus.APPROVED
    )

    assert updated.approval_status == ApprovalStatus.APPROVED

    results = catalog.get_approved_relationships("ecommerce_prod")

    assert len(results) == 1
    assert results[0] == updated


def test_update_relationship_to_rejected(catalog):
    relationship = create_relationship(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(relationship)

    updated = catalog.update_relationship_status(
        relationship,
        ApprovalStatus.REJECTED
    )

    assert updated.approval_status == ApprovalStatus.REJECTED


def test_update_nonexistent_relationship(catalog):
    relationship = create_relationship()

    with pytest.raises(ValueError):
        catalog.update_relationship_status(
            relationship,
            ApprovalStatus.APPROVED
        )


def test_update_with_invalid_status(catalog):
    relationship = create_relationship(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(relationship)

    with pytest.raises(TypeError):
        catalog.update_relationship_status(
            relationship,
            "approved"
        )


def test_updated_relationship_replaces_original(catalog):
    relationship = create_relationship(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(relationship)

    updated = catalog.update_relationship_status(
        relationship,
        ApprovalStatus.APPROVED
    )

    assert relationship not in catalog.get_all_relationships()
    assert updated in catalog.get_all_relationships()
