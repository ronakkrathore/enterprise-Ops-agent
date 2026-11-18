
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
