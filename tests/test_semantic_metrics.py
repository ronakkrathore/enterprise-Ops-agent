
import pytest
from dataclasses import FrozenInstanceError

from shared.semantic.models.metrics import (
    AggregationType,
    FilterOperator,
    MetricFilter,
    MetricDefinition
)
from shared.semantic.models.metrics import (
    ArithmeticOperator,
    MetricReference,
    BinaryMetricExpression,
    DerivedMetricDefinition
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

def test_create_valid_metric_filter():
    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.EQUAL,
        value="Complete"
    )

    assert metric_filter.concept_id == "order_item.status"
    assert metric_filter.operator == FilterOperator.EQUAL
    assert metric_filter.value == "Complete"


def test_metric_filter_is_immutable():
    from dataclasses import FrozenInstanceError

    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.EQUAL,
        value="Complete"
    )

    with pytest.raises(FrozenInstanceError):
        metric_filter.value = "Returned"


def test_metric_filter_requires_concept_id():
    with pytest.raises(ValueError):
        MetricFilter(
            concept_id=" ",
            operator=FilterOperator.EQUAL,
            value="Complete"
        )


def test_metric_filter_requires_valid_operator():
    with pytest.raises(TypeError):
        MetricFilter(
            concept_id="order_item.status",
            operator="equal",
            value="Complete"
        )


@pytest.mark.parametrize(
    "operator",
    [
        FilterOperator.IS_NULL,
        FilterOperator.IS_NOT_NULL
    ]
)
def test_null_operators_do_not_accept_values(operator):
    with pytest.raises(ValueError):
        MetricFilter(
            concept_id="order_item.status",
            operator=operator,
            value="Complete"
        )


def test_null_operator_accepts_none():
    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.IS_NULL
    )

    assert metric_filter.value is None


@pytest.mark.parametrize(
    "operator",
    [
        FilterOperator.IN,
        FilterOperator.NOT_IN
    ]
)
def test_membership_operators_require_non_empty_values(operator):
    with pytest.raises(ValueError):
        MetricFilter(
            concept_id="order_item.status",
            operator=operator,
            value=[]
        )


def test_membership_operator_accepts_multiple_values():
    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.IN,
        value=("Complete", "Shipped")
    )

    assert metric_filter.value == ("Complete", "Shipped")


def test_comparison_operators_require_values():
    with pytest.raises(ValueError):
        MetricFilter(
            concept_id="order_item.status",
            operator=FilterOperator.EQUAL,
            value=None
        )

def test_metric_accepts_filters():
    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.EQUAL,
        value="Complete"
    )

    metric = create_metric(filters=(metric_filter,))

    assert len(metric.filters) == 1
    assert metric.filters[0] == metric_filter


def test_metric_without_filters():
    metric = create_metric()

    assert metric.filters == ()


def test_metric_filters_are_immutable():
    metric_filter = MetricFilter(
        concept_id="order_item.status",
        operator=FilterOperator.EQUAL,
        value="Complete"
    )

    metric = create_metric(filters=[metric_filter])

    assert isinstance(metric.filters, tuple)

    with pytest.raises(FrozenInstanceError):
        metric.filters = ()


def test_metric_rejects_invalid_filters_container():
    with pytest.raises(TypeError):
        create_metric(filters="invalid")


def test_metric_rejects_invalid_filter_objects():
    with pytest.raises(TypeError):
        create_metric(filters=("invalid",))

def test_create_metric_reference():
    reference = MetricReference(metric_id="completed_sales")

    assert reference.metric_id == "completed_sales"


def test_reject_empty_metric_reference():
    with pytest.raises(ValueError):
        MetricReference(metric_id=" ")


def test_create_binary_metric_expression():
    expression = BinaryMetricExpression(
        left=MetricReference("completed_sales"),
        operator=ArithmeticOperator.DIVIDE,
        right=MetricReference("completed_orders")
    )

    assert expression.operator == ArithmeticOperator.DIVIDE


def test_reject_invalid_expression_operands():
    with pytest.raises(TypeError):
        BinaryMetricExpression(
            left="completed_sales",
            operator=ArithmeticOperator.DIVIDE,
            right=MetricReference("completed_orders")
        )


def test_create_derived_metric_definition():
    expression = BinaryMetricExpression(
        left=MetricReference("completed_sales"),
        operator=ArithmeticOperator.DIVIDE,
        right=MetricReference("completed_orders")
    )

    metric = DerivedMetricDefinition(
        metric_id="average_order_value",
        name="Average Order Value",
        description="Completed item sales divided by completed orders.",
        expression=expression
    )

    assert metric.metric_id == "average_order_value"


def test_reject_derived_metric_with_invalid_expression():
    with pytest.raises(TypeError):
        DerivedMetricDefinition(
            metric_id="average_order_value",
            name="Average Order Value",
            description="Average order value.",
            expression="completed_sales / completed_orders"
        )