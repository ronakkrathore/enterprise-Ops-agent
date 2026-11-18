
import pytest

from sqlalchemy import text

from shared.database.connection import get_database_engine
from shared.semantic.models.relationships import (
    SemanticRelationship,
    RelationshipType,
    RelationshipOrigin
)
from shared.semantic.models.mappings import ApprovalStatus
from shared.semantic.relationship_resolver import (
    discover_relationships,
    discover_and_store_relationships,
    resolve_join_path
)

from shared.semantic.catalog.relationship_catalog import (
    RelationshipCatalog
)

@pytest.fixture
def test_engine(tmp_path):
    database_path = tmp_path / "relationship_test.duckdb"

    engine = get_database_engine(
        f"duckdb:///{database_path}"
    )

    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE customers (
                id INTEGER PRIMARY KEY,
                name VARCHAR
            )
        """))

        connection.execute(text("""
            CREATE TABLE orders (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES customers(id)
            )
        """))

    yield engine

    engine.dispose()


def test_discover_foreign_key_relationship(test_engine):
    relationships = discover_relationships(
        test_engine,
        source_id="test_source"
    )

    assert len(relationships) == 1

    relationship = relationships[0]

    assert relationship.source_id == "test_source"

    assert relationship.left_table == "orders"
    assert relationship.left_column == "user_id"

    assert relationship.right_table == "customers"
    assert relationship.right_column == "id"

    assert relationship.relationship_type == RelationshipType.MANY_TO_ONE
    assert relationship.relationship_origin == RelationshipOrigin.SCHEMA_DISCOVERED
    assert relationship.approval_status == ApprovalStatus.PROPOSED


def test_discovered_relationship_has_correct_schema(test_engine):
    relationships = discover_relationships(
        test_engine,
        source_id="test_source"
    )

    relationship = relationships[0]

    assert relationship.left_schema == "main"
    assert relationship.right_schema == "main"


def test_discover_and_store_relationships(test_engine):
    catalog = RelationshipCatalog()

    relationships = discover_and_store_relationships(
        test_engine,
        "test_source",
        catalog
    )

    assert len(relationships) == 1
    assert len(catalog.get_all_relationships()) == 1

    stored = catalog.get_all_relationships()[0]

    assert stored == relationships[0]
    assert stored.approval_status == ApprovalStatus.PROPOSED


def test_repeated_discovery_does_not_duplicate_relationships(
    test_engine
):
    catalog = RelationshipCatalog()

    discover_and_store_relationships(
        test_engine,
        "test_source",
        catalog
    )

    discover_and_store_relationships(
        test_engine,
        "test_source",
        catalog
    )

    assert len(catalog.get_all_relationships()) == 1


def test_discovery_rejects_invalid_catalog(test_engine):
    with pytest.raises(TypeError):
        discover_and_store_relationships(
            test_engine,
            "test_source",
            []
        )


def create_approved_relationship(
    left_table,
    left_column,
    right_table,
    right_column
):
    return SemanticRelationship(
        source_id="test_source",

        left_schema="main",
        left_table=left_table,
        left_column=left_column,

        right_schema="main",
        right_table=right_table,
        right_column=right_column,

        relationship_type=RelationshipType.MANY_TO_ONE,
        relationship_origin=RelationshipOrigin.MANUAL,
        confidence=1.0,
        approval_status=ApprovalStatus.APPROVED
    )


def test_resolve_direct_join_path():
    catalog = RelationshipCatalog()

    relationship = create_approved_relationship(
        "orders",
        "user_id",
        "customers",
        "id"
    )

    catalog.add_relationship(relationship)

    path = resolve_join_path(
        catalog,
        "test_source",
        "main",
        "orders",
        "main",
        "customers"
    )

    assert len(path) == 1
    assert path[0] == relationship


def test_resolve_multi_table_join_path():
    catalog = RelationshipCatalog()

    first = create_approved_relationship(
        "orders",
        "user_id",
        "customers",
        "id"
    )

    second = create_approved_relationship(
        "order_items",
        "order_id",
        "orders",
        "id"
    )

    catalog.add_relationship(first)
    catalog.add_relationship(second)

    path = resolve_join_path(
        catalog,
        "test_source",
        "main",
        "customers",
        "main",
        "order_items"
    )

    assert len(path) == 2
    assert set(path) == {first, second}


def test_resolve_join_path_ignores_proposed_relationships():
    catalog = RelationshipCatalog()

    proposed = SemanticRelationship(
        source_id="test_source",
        left_schema="main",
        left_table="orders",
        left_column="user_id",
        right_schema="main",
        right_table="customers",
        right_column="id",
        relationship_type=RelationshipType.MANY_TO_ONE,
        relationship_origin=RelationshipOrigin.SCHEMA_DISCOVERED,
        confidence=1.0,
        approval_status=ApprovalStatus.PROPOSED
    )

    catalog.add_relationship(proposed)

    with pytest.raises(ValueError, match="No approved relationship path"):
        resolve_join_path(
            catalog,
            "test_source",
            "main",
            "orders",
            "main",
            "customers"
        )


def test_resolve_join_path_returns_empty_for_same_table():
    catalog = RelationshipCatalog()

    path = resolve_join_path(
        catalog,
        "test_source",
        "main",
        "orders",
        "main",
        "orders"
    )

    assert path == ()


def test_resolve_join_path_rejects_ambiguous_paths():
    catalog = RelationshipCatalog()

    first = create_approved_relationship(
        "customers",
        "id",
        "orders",
        "user_id"
    )

    second = create_approved_relationship(
        "orders",
        "id",
        "order_items",
        "order_id"
    )

    third = create_approved_relationship(
        "customers",
        "id",
        "returns",
        "user_id"
    )

    fourth = create_approved_relationship(
        "returns",
        "order_id",
        "order_items",
        "order_id"
    )

    for relationship in (first, second, third, fourth):
        catalog.add_relationship(relationship)

    with pytest.raises(ValueError, match="Multiple shortest relationship paths"):
        resolve_join_path(
            catalog,
            "test_source",
            "main",
            "customers",
            "main",
            "order_items"
        )

def test_resolve_join_path_in_reverse_direction():
    catalog = RelationshipCatalog()

    relationship = create_approved_relationship(
        "orders",
        "user_id",
        "customers",
        "id"
    )

    catalog.add_relationship(relationship)

    path = resolve_join_path(
        catalog,
        "test_source",
        "main",
        "customers",
        "main",
        "orders"
    )

    assert len(path) == 1
    assert path[0] == relationship

def test_resolve_join_path_respects_schema_names():
    catalog = RelationshipCatalog()

    relationship = SemanticRelationship(
        source_id="test_source",
        left_schema="sales",
        left_table="orders",
        left_column="customer_id",
        right_schema="sales",
        right_table="customers",
        right_column="id",
        relationship_type=RelationshipType.MANY_TO_ONE,
        relationship_origin=RelationshipOrigin.MANUAL,
        confidence=1.0,
        approval_status=ApprovalStatus.APPROVED
    )

    catalog.add_relationship(relationship)

    path = resolve_join_path(
        catalog,
        "test_source",
        "sales",
        "orders",
        "sales",
        "customers"
    )

    assert len(path) == 1

    with pytest.raises(ValueError, match="No approved relationship path"):
        resolve_join_path(
            catalog,
            "test_source",
            "main",
            "orders",
            "main",
            "customers"
        )

def test_resolve_join_path_respects_source_id():
    catalog = RelationshipCatalog()

    relationship = create_approved_relationship(
        "orders",
        "user_id",
        "customers",
        "id"
    )

    catalog.add_relationship(relationship)

    # Correct source should find the path.
    path = resolve_join_path(
        catalog,
        "test_source",
        "main",
        "orders",
        "main",
        "customers"
    )

    assert len(path) == 1

    # Different source must not reuse that relationship.
    with pytest.raises(ValueError, match="No approved relationship path"):
        resolve_join_path(
            catalog,
            "another_company",
            "main",
            "orders",
            "main",
            "customers"
        )

def test_resolve_join_path_rejects_invalid_catalog():
    with pytest.raises(TypeError, match="catalog must be a RelationshipCatalog"):
        resolve_join_path(
            [],
            "test_source",
            "main",
            "orders",
            "main",
            "customers"
        )


def test_resolve_join_path_detects_converging_shortest_paths():
    catalog = RelationshipCatalog()

    relationships = [
        create_approved_relationship(
            "customers", "id", "orders", "customer_id"
        ),
        create_approved_relationship(
            "customers", "id", "invoices", "customer_id"
        ),
        create_approved_relationship(
            "orders", "product_id", "products", "id"
        ),
        create_approved_relationship(
            "invoices", "product_id", "products", "id"
        )
    ]

    for relationship in relationships:
        catalog.add_relationship(relationship)

    with pytest.raises(
        ValueError,
        match="Multiple shortest relationship paths"
    ):
        resolve_join_path(
            catalog,
            "test_source",
            "main",
            "customers",
            "main",
            "products"
        )


def test_rediscovery_preserves_approved_relationship(test_engine):
    from shared.semantic.catalog.relationship_catalog import (
        RelationshipCatalog
    )
    from shared.semantic.models.mappings import ApprovalStatus
    from shared.semantic.relationship_resolver import (
        discover_and_store_relationships
    )

    catalog = RelationshipCatalog()

    # First discovery
    discovered = discover_and_store_relationships(
        test_engine,
        "test_db",
        catalog
    )

    assert len(discovered) > 0

    # Approve the discovered relationship
    relationship = discovered[0]

    catalog.update_relationship_status(
        relationship,
        ApprovalStatus.APPROVED
    )

    # Discover the same database relationships again
    rediscovered = discover_and_store_relationships(
        test_engine,
        "test_db",
        catalog
    )

    # Catalog must retain the approved relationship
    stored = catalog.get_all_relationships()

    assert len(stored) == len(discovered)
    assert len(rediscovered) == len(discovered)

    assert any(
        item.approval_status == ApprovalStatus.APPROVED
        for item in stored
    )
