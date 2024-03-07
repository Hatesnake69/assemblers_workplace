import datetime

import pytest

from app.models import WbSupplyModel
from app.models.wb.wb_tasks import Status
from app.services.partition_service import get_orders_partitions, fill_task_with_orders
from assemblers_workplace.settings import settings
from tests.test_utils import assert_task_fields, generate_orders


@pytest.mark.django_db
class TestCreateTask:
    def test_create_wb_task(self, mock_wb_task):
        assert_task_fields(mock_wb_task)

    @pytest.mark.parametrize(
        "status",
        [Status.GET_ORDERS_STICKERS.value, Status.SEND_SUPPLY_TO_DELIVER.value],
    )
    def test_wb_task_set_status_get_orders_stickers(self, mock_wb_task, status):
        mock_wb_task.task_state = status
        mock_wb_task.save()
        assert_task_fields(mock_wb_task)

    @pytest.mark.parametrize("amount, expected", [(5, 7), (10, 10)])
    def test_partitions(self, amount, expected):
        order = generate_orders(10)

        # Check that the orders are divided into partitions by date
        partitions = get_orders_partitions(order)
        for i in range(1, 5):
            assert len(partitions[i]) == 1
            created_date = datetime.datetime.fromisoformat(partitions[i][0].createdAt)
            expected_date = datetime.datetime.today() - datetime.timedelta(days=(4 - i))
            assert created_date.date() == expected_date.date()

        three_days_before_yesterday = datetime.datetime.today() - datetime.timedelta(
            days=3
        )
        for order in partitions[0]:
            created_day = datetime.datetime.fromisoformat(order.createdAt)
            assert three_days_before_yesterday.date() >= created_day.date()

        assert len(partitions) == 5
        assert len(partitions[0]) == 7

        new_orders = fill_task_with_orders(partitions, amount)

        assert len(new_orders) == expected

    def test_partitions_empty_rest_partition(self):
        orders = generate_orders(3)
        partitions = get_orders_partitions(orders)
        for partition in partitions:
            assert len(partition) == 1

        assert len(partitions) == 3

    def test_partitions_empty_orders(self):
        orders = generate_orders(0)
        partitions = get_orders_partitions(orders)
        assert len(partitions) == 0

    def test_partitions_amount(self):
        orders = generate_orders(3)
        partitions = get_orders_partitions(orders)
        orders_to_fill = fill_task_with_orders(partitions, 5)
        assert len(orders_to_fill) == 3

        orders = generate_orders(20)
        orders.orders = orders.orders[5:]
        partitions = get_orders_partitions(orders)
        assert len(partitions) == 1

        orders_to_fill = fill_task_with_orders(partitions, 3)
        assert len(orders_to_fill) == 15

    def test_create_new_supply(self, mock_api, mock_wb_task, wb_orders_service):
        mock_api.post(
            url=settings.post_wb_new_supply_url,
            json={"id": 2},
        )
        result = wb_orders_service.create_new_supply(
            name="test_supply", task=mock_wb_task
        )
        assert result.wb_id == 2
        assert isinstance(result, WbSupplyModel)
