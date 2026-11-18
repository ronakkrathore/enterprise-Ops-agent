
from shared.semantic.models.metrics import MetricDefinition


class MetricCatalog:
    """
    Stores and retrieves business metric definitions.

    This initial implementation uses in-memory storage.
    """

    def __init__(self):
        self._metrics: dict[str, MetricDefinition] = {}

    def add_metric(self, metric: MetricDefinition) -> None:
        """Add a metric definition to the catalog."""

        if not isinstance(metric, MetricDefinition):
            raise TypeError(
                "metric must be a MetricDefinition instance."
            )

        existing = self._metrics.get(metric.metric_id)

        if existing is not None:
            if existing == metric:
                return

            raise ValueError(
                "A different metric with this metric_id already exists."
            )

        self._metrics[metric.metric_id] = metric

    def get_all_metrics(self) -> tuple[MetricDefinition, ...]:
        """Return all metrics as an immutable tuple."""

        return tuple(self._metrics.values())

    def get_metric(self, metric_id: str) -> MetricDefinition | None:
        """Retrieve a metric by its unique identifier."""

        return self._metrics.get(metric_id)
