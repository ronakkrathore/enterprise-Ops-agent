
import pytest

from shared.semantic.catalog.catalog import SemanticCatalog

from shared.semantic.models.mappings import (
    SemanticMapping,
    MappingOrigin,
    ApprovalStatus
)


@pytest.fixture
def catalog():
    return SemanticCatalog()


def create_mapping(
    source_id="ecommerce_prod",
    schema_name="main",
    table_name="customers",
    column_name="customer_id",
    concept_id="customer.id",
    status=ApprovalStatus.APPROVED
):
    return SemanticMapping(
        source_id=source_id,
        schema_name=schema_name,
        table_name=table_name,
        column_name=column_name,
        concept_id=concept_id,
        confidence=0.95,
        mapping_origin=MappingOrigin.MANUAL,
        approval_status=status,
        source_data_type="BIGINT"
    )


def test_add_mapping(catalog):
    mapping = create_mapping()

    catalog.add_mapping(mapping)

    assert len(catalog.get_all_mappings()) == 1


def test_duplicate_mapping_is_not_added(catalog):
    mapping = create_mapping()

    catalog.add_mapping(mapping)
    catalog.add_mapping(mapping)

    assert len(catalog.get_all_mappings()) == 1


def test_get_mappings_by_source(catalog):
    mapping_a = create_mapping(
        source_id="ecommerce_prod"
    )

    mapping_b = create_mapping(
        source_id="crm_prod",
        table_name="client_master",
        column_name="client_ref"
    )

    catalog.add_mapping(mapping_a)
    catalog.add_mapping(mapping_b)

    results = catalog.get_mappings_by_source("crm_prod")

    assert len(results) == 1
    assert results[0].source_id == "crm_prod"


def test_get_mappings_by_concept(catalog):
    mapping = create_mapping()

    catalog.add_mapping(mapping)

    results = catalog.get_mappings_by_concept(
        "ecommerce_prod",
        "customer.id"
    )

    assert len(results) == 1
    assert results[0].concept_id == "customer.id"


def test_get_approved_mapping_by_column(catalog):
    mapping = create_mapping()

    catalog.add_mapping(mapping)

    result = catalog.get_mapping_by_column(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="customers",
        column_name="customer_id"
    )

    assert result == mapping


def test_unapproved_mapping_is_not_returned_by_column_lookup(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    result = catalog.get_mapping_by_column(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="customers",
        column_name="customer_id"
    )

    assert result is None


def test_conflicting_approved_mapping_is_rejected(catalog):
    mapping_a = create_mapping(
        concept_id="customer.id"
    )

    mapping_b = create_mapping(
        concept_id="customer.name"
    )

    catalog.add_mapping(mapping_a)

    with pytest.raises(ValueError):
        catalog.add_mapping(mapping_b)


def test_same_concept_can_be_mapped_across_sources(catalog):
    mapping_a = create_mapping(
        source_id="ecommerce_prod",
        table_name="customers",
        column_name="customer_id"
    )

    mapping_b = create_mapping(
        source_id="crm_prod",
        table_name="client_master",
        column_name="client_ref"
    )

    catalog.add_mapping(mapping_a)
    catalog.add_mapping(mapping_b)

    assert len(catalog.get_mappings_by_concept(
        "ecommerce_prod",
        "customer.id"
    )) == 1

    assert len(catalog.get_mappings_by_concept(
        "crm_prod",
        "customer.id"
    )) == 1


def test_get_mappings_by_status(catalog):
    approved = create_mapping()

    proposed = create_mapping(
        column_name="email",
        concept_id="customer.name",
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(approved)
    catalog.add_mapping(proposed)

    results = catalog.get_mappings_by_status(
        ApprovalStatus.PROPOSED
    )

    assert len(results) == 1
    assert results[0] == proposed


def test_catalog_rejects_invalid_mapping(catalog):
    with pytest.raises(TypeError):
        catalog.add_mapping("not a semantic mapping")


def test_same_table_name_in_different_schemas(catalog):
    mapping_a = create_mapping(
        schema_name="sales",
        table_name="customers"
    )

    mapping_b = create_mapping(
        schema_name="archive",
        table_name="customers"
    )

    catalog.add_mapping(mapping_a)
    catalog.add_mapping(mapping_b)

    result = catalog.get_mapping_by_column(
        source_id="ecommerce_prod",
        schema_name="archive",
        table_name="customers",
        column_name="customer_id"
    )

    assert result == mapping_b


def test_update_proposed_mapping_to_approved(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    updated = catalog.update_mapping_status(
        mapping,
        ApprovalStatus.APPROVED
    )

    assert updated.approval_status == ApprovalStatus.APPROVED

    result = catalog.get_mapping_by_column(
        "ecommerce_prod",
        "main",
        "customers",
        "customer_id"
    )

    assert result == updated


def test_update_mapping_to_rejected(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    updated = catalog.update_mapping_status(
        mapping,
        ApprovalStatus.REJECTED
    )

    assert updated.approval_status == ApprovalStatus.REJECTED


def test_update_nonexistent_mapping(catalog):
    mapping = create_mapping()

    with pytest.raises(ValueError):
        catalog.update_mapping_status(
            mapping,
            ApprovalStatus.APPROVED
        )


def test_update_with_invalid_status(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    with pytest.raises(TypeError):
        catalog.update_mapping_status(
            mapping,
            "approved"
        )


def test_approval_rejects_conflicting_mapping(catalog):
    mapping_a = create_mapping(
        concept_id="customer.id",
        status=ApprovalStatus.APPROVED
    )

    mapping_b = create_mapping(
        concept_id="customer.name",
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping_a)
    catalog.add_mapping(mapping_b)

    with pytest.raises(ValueError):
        catalog.update_mapping_status(
            mapping_b,
            ApprovalStatus.APPROVED
        )

    # Original mapping must remain proposed.
    assert (
        catalog.get_mappings_by_status(
            ApprovalStatus.PROPOSED
        )[0] == mapping_b
    )


def test_updated_mapping_replaces_original(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    updated = catalog.update_mapping_status(
        mapping,
        ApprovalStatus.APPROVED
    )

    assert updated not in ()
    assert mapping not in catalog.get_all_mappings()
    assert updated in catalog.get_all_mappings()


def test_rejected_mapping_can_be_reapproved(catalog):
    mapping = create_mapping(
        status=ApprovalStatus.PROPOSED
    )

    catalog.add_mapping(mapping)

    rejected = catalog.update_mapping_status(
        mapping,
        ApprovalStatus.REJECTED
    )

    approved = catalog.update_mapping_status(
        rejected,
        ApprovalStatus.APPROVED
    )

    assert approved.approval_status == ApprovalStatus.APPROVED
