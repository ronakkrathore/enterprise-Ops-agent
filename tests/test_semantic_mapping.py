
import pytest
from dataclasses import FrozenInstanceError

from shared.semantic.models.mappings import (
    SemanticMapping,
    MappingOrigin,
    ApprovalStatus
)


@pytest.fixture
def valid_mapping():
    return SemanticMapping(
        source_id="ecommerce_prod",
        schema_name="main",
        table_name="customers",
        column_name="customer_id",
        concept_id="customer.id",
        confidence=0.96,
        mapping_origin=MappingOrigin.RULE_BASED,
        approval_status=ApprovalStatus.APPROVED,
        source_data_type="BIGINT"
    )


def test_valid_semantic_mapping(valid_mapping):
    assert valid_mapping.source_id == "ecommerce_prod"
    assert valid_mapping.concept_id == "customer.id"
    assert valid_mapping.confidence == 0.96


def test_mapping_origin_enum():
    assert MappingOrigin.MANUAL.value == "manual"
    assert MappingOrigin.RULE_BASED.value == "rule_based"
    assert MappingOrigin.LLM_SUGGESTED.value == "llm_suggested"


def test_approval_status_enum():
    assert ApprovalStatus.PROPOSED.value == "proposed"
    assert ApprovalStatus.APPROVED.value == "approved"
    assert ApprovalStatus.REJECTED.value == "rejected"
    assert ApprovalStatus.NEEDS_REVIEW.value == "needs_review"


@pytest.mark.parametrize(
    "confidence",
    [-0.1, 1.1, "high", True]
)
def test_invalid_confidence(confidence):
    with pytest.raises(ValueError):
        SemanticMapping(
            source_id="ecommerce_prod",
            schema_name="main",
            table_name="customers",
            column_name="customer_id",
            concept_id="customer.id",
            confidence=confidence,
            mapping_origin=MappingOrigin.MANUAL,
            approval_status=ApprovalStatus.PROPOSED
        )


def test_empty_source_id_is_rejected():
    with pytest.raises(ValueError):
        SemanticMapping(
            source_id="",
            schema_name="main",
            table_name="customers",
            column_name="customer_id",
            concept_id="customer.id",
            confidence=0.9,
            mapping_origin=MappingOrigin.MANUAL,
            approval_status=ApprovalStatus.PROPOSED
        )


def test_mapping_is_immutable(valid_mapping):
    with pytest.raises(FrozenInstanceError):
        valid_mapping.concept_id = "customer.name"


def test_source_data_type_is_optional():
    mapping = SemanticMapping(
        source_id="crm_prod",
        schema_name="public",
        table_name="client_master",
        column_name="client_ref",
        concept_id="customer.id",
        confidence=0.95,
        mapping_origin=MappingOrigin.MANUAL,
        approval_status=ApprovalStatus.APPROVED
    )

    assert mapping.source_data_type is None


def test_invalid_mapping_origin_is_rejected():
    with pytest.raises(TypeError):
        SemanticMapping(
            source_id="ecommerce_prod",
            schema_name="main",
            table_name="customers",
            column_name="customer_id",
            concept_id="customer.id",
            confidence=0.9,
            mapping_origin="manual",
            approval_status=ApprovalStatus.PROPOSED
        )
