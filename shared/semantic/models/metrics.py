from dataclasses import dataclass
from enum import Enum


class AggregationType(str, Enum):
    """Supported metric aggregation operations."""

    SUM = "sum"
    COUNT = "count"
    COUNT_DISTINCT = "count_distinct"
    AVERAGE = "average"
    MIN = "min"
    MAX = "max"

class FilterOperator(str, Enum):
    """Supported operators for business metric filters."""

    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    GREATER_THAN = "greater_than"
    GREATER_THAN_OR_EQUAL = "greater_than_or_equal"
    LESS_THAN = "less_than"
    LESS_THAN_OR_EQUAL = "less_than_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"


@dataclass(frozen=True)
class MetricFilter:
    """
    Defines a business filter using a canonical concept,
    an operator, and a comparison value.
    """

    concept_id: str
    operator: FilterOperator
    value: object = None

    def __post_init__(self):
        """Validate and normalize metric filter fields."""

        if (
            not isinstance(self.concept_id, str)
            or not self.concept_id.strip()
        ):
            raise ValueError(
                "concept_id must be a non-empty string."
            )

        if not isinstance(self.operator, FilterOperator):
            raise TypeError(
                "operator must be a FilterOperator value."
            )

        # Null-check operators must not have comparison values.
        if self.operator in (
            FilterOperator.IS_NULL,
            FilterOperator.IS_NOT_NULL
        ):
            if self.value is not None:
                raise ValueError(
                    "IS_NULL and IS_NOT_NULL operators "
                    "must not have a comparison value."
                )

        # Membership operators require a non-empty collection.
        elif self.operator in (
            FilterOperator.IN,
            FilterOperator.NOT_IN
        ):
            if (
                not isinstance(self.value, (tuple, list))
                or len(self.value) == 0
            ):
                raise ValueError(
                    "IN and NOT_IN require a non-empty list or tuple."
                )

            # Convert mutable lists into immutable tuples.
            object.__setattr__(
                self,
                "value",
                tuple(self.value)
            )

        # Other comparison operators require a value.
        elif self.value is None:
            raise ValueError(
                "This filter operator requires a comparison value."
            )

class ArithmeticOperator(str, Enum):
    ADD = "add"
    SUBTRACT = "subtract"
    MULTIPLY = "multiply"
    DIVIDE = "divide"


@dataclass(frozen=True)
class MetricReference:
    metric_id: str

    def __post_init__(self):
        if (
            not isinstance(self.metric_id, str)
            or not self.metric_id.strip()
        ):
            raise ValueError(
                "metric_id must be a non-empty string."
            )


@dataclass(frozen=True)
class BinaryMetricExpression:
    left: MetricReference
    operator: ArithmeticOperator
    right: MetricReference

    def __post_init__(self):
        if not isinstance(self.left, MetricReference):
            raise TypeError(
                "left must be a MetricReference instance."
            )

        if not isinstance(self.right, MetricReference):
            raise TypeError(
                "right must be a MetricReference instance."
            )

        if not isinstance(self.operator, ArithmeticOperator):
            raise TypeError(
                "operator must be an ArithmeticOperator value."
            )


@dataclass(frozen=True)
class DerivedMetricDefinition:
    metric_id: str
    name: str
    description: str
    expression: BinaryMetricExpression

    def __post_init__(self):
        for field_name in ("metric_id", "name", "description"):
            value = getattr(self, field_name)

            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(
            self.expression,
            BinaryMetricExpression
        ):
            raise TypeError(
                "expression must be a BinaryMetricExpression instance."
            )

@dataclass(frozen=True)
class MetricDefinition:
    """
    Defines a business metric independently of
    any physical database schema.
    """


    metric_id: str
    name: str
    description: str

    measure_concept_id: str
    aggregation: AggregationType

    grain: str

    date_concept_id: str | None = None
        
    filters: tuple[MetricFilter, ...] = ()

    def __post_init__(self):
        """Validate metric definition fields."""

        required_fields = {
            "metric_id": self.metric_id,
            "name": self.name,
            "description": self.description,
            "measure_concept_id": self.measure_concept_id,
            "grain": self.grain,
        }

        for field_name, value in required_fields.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"{field_name} must be a non-empty string."
                )

        if not isinstance(self.aggregation, AggregationType):
            raise TypeError(
                "aggregation must be an AggregationType value."
            )

        if (
            self.date_concept_id is not None
            and (
                not isinstance(self.date_concept_id, str)
                or not self.date_concept_id.strip()
            )
        ):
            raise ValueError(
                "date_concept_id must be a non-empty string or None."
            )

        if not isinstance(self.filters, (tuple, list)):
            raise TypeError(
                "filters must be a tuple or list of MetricFilter objects."
            )

        if not all(
            isinstance(metric_filter, MetricFilter)
            for metric_filter in self.filters
        ):
            raise TypeError(
                "Every filter must be a MetricFilter instance."
            )

        object.__setattr__(
            self,
            "filters",
            tuple(self.filters)
        )