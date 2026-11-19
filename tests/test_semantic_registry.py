
import pytest

from shared.semantic.vocabulary.concepts import (
    BusinessConcept,
    BusinessDomain,
    ConceptType
)

from shared.semantic.vocabulary.registry import (
    CANONICAL_CONCEPTS,
    get_concept,
    validate_registry
)


def test_canonical_registry_contains_concepts():
    assert len(CANONICAL_CONCEPTS) == 18


def test_canonical_registry_is_immutable():
    assert isinstance(CANONICAL_CONCEPTS, tuple)


def test_get_existing_concept():
    concept = get_concept("customer.id")

    assert concept.concept_id == "customer.id"
    assert concept.domain == BusinessDomain.CUSTOMER
    assert concept.concept_type == ConceptType.IDENTIFIER

@pytest.mark.parametrize(
    "concept_id, expected_type",
    [
        ("order_item.id", ConceptType.IDENTIFIER),
        ("order_item.status", ConceptType.STATUS),
        ("order_item.created_at", ConceptType.DATE),
    ]
)
def test_get_order_item_concepts(concept_id, expected_type):
    concept = get_concept(concept_id)

    assert concept.concept_id == concept_id
    assert concept.domain == BusinessDomain.ORDER
    assert concept.concept_type == expected_type


def test_get_missing_concept():
    with pytest.raises(KeyError):
        get_concept("customer.email")


def test_registry_rejects_duplicate_ids():
    duplicate_concepts = (
        CANONICAL_CONCEPTS
        + (CANONICAL_CONCEPTS[0],)
    )

    with pytest.raises(ValueError):
        validate_registry(duplicate_concepts)


def test_registry_accepts_unique_ids():
    validate_registry(CANONICAL_CONCEPTS)


def test_business_concept_is_immutable():
    concept = BusinessConcept(
        concept_id="customer.test",
        domain=BusinessDomain.CUSTOMER,
        name="Test Customer",
        concept_type=ConceptType.ATTRIBUTE,
        description="Test concept."
    )

    with pytest.raises(AttributeError):
        concept.name = "Changed Name"
