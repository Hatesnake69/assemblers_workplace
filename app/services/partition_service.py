import datetime

from app.schemas.order_schemas import OrdersResponseFromWb, OrderFromWb
from assemblers_workplace.settings import settings

map_of_intervals = {
    "today_00-24": (datetime.time(0, 0), datetime.time(23, 59, 59)),
    "yesterday_00-24": (datetime.time(0, 0), datetime.time(23, 59, 59)),
    "day_before_yesterday_00-24": (datetime.time(0, 0), datetime.time(23, 59, 59)),
    "rest": (datetime.time(0, 0), datetime.time(23, 59, 59)),
}


def form_partition(interval_name: str, orders_from_wb_resp: OrdersResponseFromWb) -> list[OrderFromWb]:
    start_time, end_time = map_of_intervals.get(
        interval_name, (datetime.time(0, 0), datetime.time(23, 59, 59))
    )
    today = datetime.datetime.now(tz=settings.timezone).replace(
        hour=0, minute=0, second=0
    )
    yesterday = today - datetime.timedelta(days=1)
    day_before_yesterday = today - datetime.timedelta(days=2)

    if "today" in interval_name:
        date_to_compare = today
    elif "day_before_yesterday" in interval_name:
        date_to_compare = day_before_yesterday
    elif "yesterday" in interval_name:
        date_to_compare = yesterday
    elif "rest" in interval_name:
        date_to_compare = day_before_yesterday

        return [order for order in orders_from_wb_resp.orders if (
            date_to_compare.date() >= datetime.datetime.fromisoformat(order.createdAt).date()
        )]
    else:
        raise ValueError("Invalid interval_name")
    return [
        order for order in orders_from_wb_resp.orders if all((
            date_to_compare.date() == datetime.datetime.fromisoformat(order.createdAt).date(),
            start_time <= datetime.datetime.fromisoformat(order.createdAt).time() <= end_time
        ))
    ]


def get_orders_partitions(orders_from_wb_resp: OrdersResponseFromWb) -> list[list[OrderFromWb]]:
    intervals_list = [
        key for key in map_of_intervals.keys().__reversed__()
    ]
    res = []
    for interval in intervals_list:
        orders = form_partition(
            interval_name=interval,
            orders_from_wb_resp=orders_from_wb_resp
        )
        if orders:
            res.append(orders)
    return res


def fill_task_with_orders(
    orders_partitions: list[list[OrderFromWb]], amount: int
) -> list[OrderFromWb]:
    index = 0
    res = []
    while amount > 0:
        try:
            res += orders_partitions[index][0:amount]
            amount -= len(orders_partitions[index])
            index += 1
        except IndexError:
            return res
    return res
