
from enum import Enum
from dataclasses import dataclass

class BusinessDomain(str, Enum):
    """
    Broad business domains supported by the semantic layer.
    """

    CUSTOMER = "customer"
    ORDER = "order"
    PRODUCT = "product"
    REVENUE = "revenue"
    INVENTORY = "inventory"
    RETURNS = "returns"


class ConceptType(str, Enum):
    """
    Types of business concepts.
    """

    IDENTIFIER = "identifier"
    ATTRIBUTE = "attribute"
    MEASURE = "measure"
    DIMENSION = "dimension"
    DATE = "date"
    STATUS = "status"


@dataclass(frozen=True)
class BusinessConcept:
    """
    Represents a canonical business concept,
    independent of any database schema.
    """

    concept_id: str
    domain: BusinessDomain
    name: str
    concept_type: ConceptType
    description: str
