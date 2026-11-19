
from shared.semantic.models.metrics import (
    MetricDefinition,
    DerivedMetricDefinition
)


MetricType = MetricDefinition | DerivedMetricDefinition


class MetricCatalog:
    """
    Stores and retrieves atomic and derived metric definitions.

    This initial implementation uses in-memory storage.
    """

    def __init__(self):
        self._metrics: dict[str, MetricType] = {}

    def add_metric(self, metric: MetricType) -> None:
        """Add an atomic or derived metric definition."""

        if not isinstance(
            metric,
            (MetricDefinition, DerivedMetricDefinition)
        ):
            raise TypeError(
                "metric must be a MetricDefinition or "
                "DerivedMetricDefinition instance."
            )

        existing = self._metrics.get(metric.metric_id)

        if existing is not None:
            if existing == metric:
                return

            raise ValueError(
                "A different metric with this metric_id already exists."
            )

        self._metrics[metric.metric_id] = metric

    def get_all_metrics(self) -> tuple[MetricType, ...]:
        """Return all metrics as an immutable tuple."""

        return tuple(self._metrics.values())

    def get_metric(self, metric_id: str) -> MetricType | None:
        """Retrieve a metric by its unique identifier."""

        return self._metrics.get(metric_id)
