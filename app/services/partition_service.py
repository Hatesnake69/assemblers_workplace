import datetime

from app.schemas.order_schemas import OrdersResponseFromWb, OrderFromWb
from assemblers_workplace.settings import settings

map_of_intervals = {
    "today_16-24": (datetime.time(16, 0), datetime.time(23, 59, 59)),
    "today_00-16": (datetime.time(0, 0), datetime.time(15, 59, 59)),
    "yesterday_16-24": (datetime.time(16, 0), datetime.time(23, 59, 59)),
    "yesterday_00-16": (datetime.time(0, 0), datetime.time(15, 59, 59)),
    "day_before_yesterday_16-24": (datetime.time(16, 0), datetime.time(23, 59, 59)),
    "day_before_yesterday_00-16": (datetime.time(0, 0), datetime.time(15, 59, 59)),
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
        print("hey")
        print(date_to_compare)
        print("hey")
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


def get_prior_partition(orders_from_wb_resp: OrdersResponseFromWb) -> list[OrderFromWb]:
    intervals_tuple = [
        "rest",
        "today_16-24",
        "today_00-16",
        "yesterday_16-24",
        "yesterday_00-16",
        "day_before_yesterday_16-24",
        "day_before_yesterday_00-16",
    ]
    for interval in intervals_tuple:
        orders = form_partition(
            interval_name=interval, orders_from_wb_resp=orders_from_wb_resp
        )
        if orders:
            return orders
    return []


