import pytest
from app.models.wb.wb_tasks import Status
from app.services.partition_service import get_orders_partitions, fill_task_with_orders
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
        order = generate_orders()

        partition = get_orders_partitions(order)
        assert len(partition) == 5
        assert len(partition[0]) == 7

        new_orders = fill_task_with_orders(partition, amount)

        assert len(new_orders) == expected

