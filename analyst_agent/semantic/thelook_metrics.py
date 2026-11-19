from shared.semantic.models.metrics import (
    MetricDefinition,
    DerivedMetricDefinition,
    MetricFilter,
    AggregationType,
    FilterOperator,
    ArithmeticOperator,
    MetricReference,
    BinaryMetricExpression
)

from shared.semantic.catalog.metric_catalog import MetricCatalog

TOTAL_ORDERS = MetricDefinition(
    metric_id="total_orders",
    name="Total Orders",
    description="Distinct count of all orders across every status.",
    measure_concept_id="order.id",
    aggregation=AggregationType.COUNT_DISTINCT,
    grain="order",
)

TOTAL_ORDER_ITEMS = MetricDefinition(
    metric_id="total_order_items",
    name="Total Order Items",
    description="Distinct count of all order items across every status.",
    measure_concept_id="order_item.id",
    aggregation=AggregationType.COUNT_DISTINCT,
    grain="order_item",
)

GROSS_ITEM_SALES = MetricDefinition(
    metric_id="gross_item_sales",
    name="Gross Item Sales",
    description=(
        "Sum of recorded item sale prices across all item statuses. "
        "This is not accounting-recognized revenue."
    ),
    measure_concept_id="order_item.sale_price",
    aggregation=AggregationType.SUM,
    grain="order_item",
)

COMPLETED_ITEM_SALES = MetricDefinition(
    metric_id="completed_item_sales",
    name="Completed Item Sales",
    description="Sum of sale prices for completed order items.",
    measure_concept_id="order_item.sale_price",
    aggregation=AggregationType.SUM,
    grain="order_item",
    filters=(
        MetricFilter(
            concept_id="order_item.status",
            operator=FilterOperator.EQUAL,
            value="Complete",
        ),
    ),
)

RETURNED_ITEM_VALUE = MetricDefinition(
    metric_id="returned_item_value",
    name="Returned Item Value",
    description="Sum of sale prices for returned order items.",
    measure_concept_id="order_item.sale_price",
    aggregation=AggregationType.SUM,
    grain="order_item",
    filters=(
        MetricFilter(
            concept_id="order_item.status",
            operator=FilterOperator.EQUAL,
            value="Returned",
        ),
    ),
)

AVERAGE_SELLING_PRICE = MetricDefinition(
    metric_id="average_selling_price",
    name="Average Selling Price",
    description="Average recorded sale price per order item.",
    measure_concept_id="order_item.sale_price",
    aggregation=AggregationType.AVERAGE,
    grain="order_item",
)

AVERAGE_ORDER_VALUE = DerivedMetricDefinition(
    metric_id="average_order_value",
    name="Average Order Value",
    description=(
        "Completed item sales divided by the number "
        "of completed orders."
    ),
    expression=BinaryMetricExpression(
        left=MetricReference("completed_item_sales"),
        operator=ArithmeticOperator.DIVIDE,
        right=MetricReference("completed_orders"),
    ),
)

COMPLETED_ORDERS = MetricDefinition(
    metric_id="completed_orders",
    name="Completed Orders",
    description="Distinct count of orders with completed status.",
    measure_concept_id="order.id",
    aggregation=AggregationType.COUNT_DISTINCT,
    grain="order",
    filters=(
        MetricFilter(
            concept_id="order.status",
            operator=FilterOperator.EQUAL,
            value="Complete",
        ),
    ),
)

RETURN_RATE = DerivedMetricDefinition(
    metric_id="return_rate",
    name="Return Rate",
    description="Returned order items divided by all order items.",
    expression=BinaryMetricExpression(
        left=MetricReference("returned_item_count"),
        operator=ArithmeticOperator.DIVIDE,
        right=MetricReference("total_order_items"),
    ),
)

RETURNED_ITEM_COUNT = MetricDefinition(
    metric_id="returned_item_count",
    name="Returned Item Count",
    description="Distinct count of returned order items.",
    measure_concept_id="order_item.id",
    aggregation=AggregationType.COUNT_DISTINCT,
    grain="order_item",
    filters=(
        MetricFilter(
            concept_id="order_item.status",
            operator=FilterOperator.EQUAL,
            value="Returned",
        ),
    ),
)

def build_thelook_metric_catalog() -> MetricCatalog:
    """Build and return the initial TheLook metric catalogue."""

    catalog = MetricCatalog()

    atomic_metrics = (
        TOTAL_ORDERS,
        TOTAL_ORDER_ITEMS,
        GROSS_ITEM_SALES,
        COMPLETED_ITEM_SALES,
        RETURNED_ITEM_VALUE,
        AVERAGE_SELLING_PRICE,
        COMPLETED_ORDERS,
        RETURNED_ITEM_COUNT,
    )

    for metric in atomic_metrics:
        catalog.add_metric(metric)

    catalog.add_metric(AVERAGE_ORDER_VALUE)
    catalog.add_metric(RETURN_RATE)

    return catalog