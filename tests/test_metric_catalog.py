
import pytest

from shared.semantic.models.metrics import (
    AggregationType,
    MetricDefinition
)

from shared.semantic.catalog.metric_catalog import MetricCatalog


def create_metric(**overrides):
    values = {
        "metric_id": "gross_revenue",
        "name": "Gross Revenue",
        "description": "Total revenue before deductions.",
        "measure_concept_id": "revenue.amount",
        "aggregation": AggregationType.SUM,
        "grain": "order_item",
        "date_concept_id": "order.created_at"
    }

    values.update(overrides)

    return MetricDefinition(**values)


def test_add_metric():
    catalog = MetricCatalog()
    metric = create_metric()

    catalog.add_metric(metric)

    assert catalog.get_metric("gross_revenue") == metric


def test_add_duplicate_metric():
    catalog = MetricCatalog()
    metric = create_metric()

    catalog.add_metric(metric)
    catalog.add_metric(metric)

    assert len(catalog.get_all_metrics()) == 1


def test_reject_conflicting_metric_id():
    catalog = MetricCatalog()

    first = create_metric()
    second = create_metric(
        name="Net Revenue",
        description="Revenue after deductions."
    )

    catalog.add_metric(first)

    with pytest.raises(
        ValueError,
        match="different metric"
    ):
        catalog.add_metric(second)


def test_get_nonexistent_metric():
    catalog = MetricCatalog()

    assert catalog.get_metric("unknown_metric") is None


def test_get_all_metrics():
    catalog = MetricCatalog()

    first = create_metric()

    second = create_metric(
        metric_id="total_orders",
        name="Total Orders",
        measure_concept_id="order.id",
        aggregation=AggregationType.COUNT_DISTINCT,
        grain="order"
    )

    catalog.add_metric(first)
    catalog.add_metric(second)

    metrics = catalog.get_all_metrics()

    assert len(metrics) == 2
    assert first in metrics
    assert second in metrics


def test_get_all_metrics_returns_tuple():
    catalog = MetricCatalog()

    catalog.add_metric(create_metric())

    assert isinstance(catalog.get_all_metrics(), tuple)


def test_reject_invalid_metric():
    catalog = MetricCatalog()

    with pytest.raises(TypeError):
        catalog.add_metric("not a metric")


def test_catalogs_are_independent():
    first_catalog = MetricCatalog()
    second_catalog = MetricCatalog()

    first_catalog.add_metric(create_metric())

    assert len(first_catalog.get_all_metrics()) == 1
    assert len(second_catalog.get_all_metrics()) == 0
