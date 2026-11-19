from analyst_agent.semantic.thelook_metrics import (
    build_thelook_metric_catalog,
)

from shared.semantic.models.metrics import (
    MetricDefinition,
    DerivedMetricDefinition,
)

from shared.semantic.validator import (
    validate_metric_definition,
    validate_derived_metric_definition,
)


def test_build_thelook_metric_catalog():
    catalog = build_thelook_metric_catalog()

    assert len(catalog.get_all_metrics()) == 10


def test_thelook_catalog_contains_eight_business_metrics_and_supporting_metrics():
    catalog = build_thelook_metric_catalog()

    expected_ids = {
        "total_orders",
        "total_order_items",
        "gross_item_sales",
        "completed_item_sales",
        "returned_item_value",
        "average_order_value",
        "return_rate",
        "average_selling_price",
        "completed_orders",
        "returned_item_count",
    }

    actual_ids = {
        metric.metric_id
        for metric in catalog.get_all_metrics()
    }

    assert actual_ids == expected_ids


def test_all_thelook_atomic_metrics_are_valid():
    catalog = build_thelook_metric_catalog()

    atomic_metrics = [
        metric
        for metric in catalog.get_all_metrics()
        if isinstance(metric, MetricDefinition)
    ]

    assert len(atomic_metrics) == 8

    for metric in atomic_metrics:
        assert validate_metric_definition(metric) is None


def test_all_thelook_derived_metrics_are_valid():
    catalog = build_thelook_metric_catalog()

    derived_metrics = [
        metric
        for metric in catalog.get_all_metrics()
        if isinstance(metric, DerivedMetricDefinition)
    ]

    assert len(derived_metrics) == 2

    for metric in derived_metrics:
        assert validate_derived_metric_definition(
            metric,
            catalog
        ) is None

def test_item_price_metrics_use_sale_price_concept():
    catalog = build_thelook_metric_catalog()

    item_price_metric_ids = (
        "gross_item_sales",
        "completed_item_sales",
        "returned_item_value",
        "average_selling_price",
    )

    for metric_id in item_price_metric_ids:
        metric = catalog.get_metric(metric_id)

        assert metric.measure_concept_id == "order_item.sale_price"