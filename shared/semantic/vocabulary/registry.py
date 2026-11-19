
from shared.semantic.vocabulary.concepts import (
    BusinessConcept,
    BusinessDomain,
    ConceptType
)


CANONICAL_CONCEPTS = (

    # Customer concepts
    BusinessConcept(
        concept_id="customer.id",
        domain=BusinessDomain.CUSTOMER,
        name="Customer ID",
        concept_type=ConceptType.IDENTIFIER,
        description="Unique identifier for a customer."
    ),

    BusinessConcept(
        concept_id="customer.name",
        domain=BusinessDomain.CUSTOMER,
        name="Customer Name",
        concept_type=ConceptType.ATTRIBUTE,
        description="Name of a customer."
    ),

    BusinessConcept(
        concept_id="customer.region",
        domain=BusinessDomain.CUSTOMER,
        name="Customer Region",
        concept_type=ConceptType.DIMENSION,
        description="Geographic region associated with a customer."
    ),

    # Order concepts
    BusinessConcept(
        concept_id="order.id",
        domain=BusinessDomain.ORDER,
        name="Order ID",
        concept_type=ConceptType.IDENTIFIER,
        description="Unique identifier for an order."
    ),

    BusinessConcept(
        concept_id="order.created_at",
        domain=BusinessDomain.ORDER,
        name="Order Creation Date",
        concept_type=ConceptType.DATE,
        description="Date and time when an order was created."
    ),

    BusinessConcept(
        concept_id="order.status",
        domain=BusinessDomain.ORDER,
        name="Order Status",
        concept_type=ConceptType.STATUS,
        description="Current or recorded status of an order."
    ),

        BusinessConcept(
        concept_id="order_item.id",
        domain=BusinessDomain.ORDER,
        name="Order Item ID",
        concept_type=ConceptType.IDENTIFIER,
        description="Unique identifier for an individual item within an order."
    ),

    BusinessConcept(
        concept_id="order_item.status",
        domain=BusinessDomain.ORDER,
        name="Order Item Status",
        concept_type=ConceptType.STATUS,
        description="Lifecycle status of an individual order item."
    ),

    BusinessConcept(
        concept_id="order_item.created_at",
        domain=BusinessDomain.ORDER,
        name="Order Item Creation Date",
        concept_type=ConceptType.DATE,
        description="Date and time when an individual order item was created."
    ),

    BusinessConcept(
        concept_id="order_item.sale_price",
        domain=BusinessDomain.ORDER,
        name="Sale Price",
        concept_type=ConceptType.MEASURE,
        description=(
            "Price recorded for an individual order item; "
            "not necessarily accounting-recognized revenue."
        ),
    ),

    # Product concepts
    BusinessConcept(
        concept_id="product.id",
        domain=BusinessDomain.PRODUCT,
        name="Product ID",
        concept_type=ConceptType.IDENTIFIER,
        description="Unique identifier for a product."
    ),

    BusinessConcept(
        concept_id="product.name",
        domain=BusinessDomain.PRODUCT,
        name="Product Name",
        concept_type=ConceptType.ATTRIBUTE,
        description="Name of a product."
    ),

    BusinessConcept(
        concept_id="product.category",
        domain=BusinessDomain.PRODUCT,
        name="Product Category",
        concept_type=ConceptType.DIMENSION,
        description="Category to which a product belongs."
    ),

    # Revenue concepts
    BusinessConcept(
        concept_id="revenue.amount",
        domain=BusinessDomain.REVENUE,
        name="Revenue Amount",
        concept_type=ConceptType.MEASURE,
        description="Monetary amount recognized as revenue under a defined business metric."
    ),

    BusinessConcept(
        concept_id="revenue.transaction_date",
        domain=BusinessDomain.REVENUE,
        name="Revenue Transaction Date",
        concept_type=ConceptType.DATE,
        description="Date associated with a revenue-generating transaction."
    ),

    # Inventory concepts
    BusinessConcept(
        concept_id="inventory.quantity",
        domain=BusinessDomain.INVENTORY,
        name="Inventory Quantity",
        concept_type=ConceptType.MEASURE,
        description="Quantity of inventory available or recorded."
    ),

    # Return concepts
    BusinessConcept(
        concept_id="return.id",
        domain=BusinessDomain.RETURNS,
        name="Return ID",
        concept_type=ConceptType.IDENTIFIER,
        description="Unique identifier for a return."
    ),

    BusinessConcept(
        concept_id="return.status",
        domain=BusinessDomain.RETURNS,
        name="Return Status",
        concept_type=ConceptType.STATUS,
        description="Status associated with a return."
    )
)


def validate_registry(
    concepts: tuple[BusinessConcept, ...]
) -> None:
    concept_ids = [
        concept.concept_id
        for concept in concepts
    ]

    if len(concept_ids) != len(set(concept_ids)):
        raise ValueError(
            "Duplicate concept IDs found in canonical registry."
        )


def get_concept(concept_id: str) -> BusinessConcept:
    """
    Retrieve a canonical concept using its ID.
    """

    for concept in CANONICAL_CONCEPTS:
        if concept.concept_id == concept_id:
            return concept

    raise KeyError(
        f"Canonical concept '{concept_id}' not found."
    )


# Validate the registry when this module is imported.
validate_registry(CANONICAL_CONCEPTS)
