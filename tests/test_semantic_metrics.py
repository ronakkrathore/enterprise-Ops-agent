
import pytest
from dataclasses import FrozenInstanceError

from shared.semantic.models.metrics import (
    AggregationType,
    MetricDefinition
)


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


def test_create_valid_metric():
    metric = create_metric()

    assert metric.metric_id == "gross_revenue"
    assert metric.aggregation == AggregationType.SUM


def test_metric_without_date_concept():
    metric = create_metric(date_concept_id=None)

    assert metric.date_concept_id is None


def test_supported_aggregation_types():
    assert len(AggregationType) == 6


@pytest.mark.parametrize(
    "field",
    [
        "metric_id",
        "name",
        "description",
        "measure_concept_id",
        "grain"
    ]
)
def test_required_fields_cannot_be_empty(field):
    with pytest.raises(ValueError):
        create_metric(**{field: "  "})


def test_invalid_aggregation_type():
    with pytest.raises(TypeError):
        create_metric(aggregation="sum")


@pytest.mark.parametrize(
    "date_concept_id",
    ["", "   "]
)
def test_invalid_date_concept(date_concept_id):
    with pytest.raises(ValueError):
        create_metric(date_concept_id=date_concept_id)


def test_date_concept_must_be_string_or_none():
    with pytest.raises(ValueError):
        create_metric(date_concept_id=123)


def test_metric_is_immutable():
    metric = create_metric()

    with pytest.raises(FrozenInstanceError):
        metric.name = "Net Revenue"
