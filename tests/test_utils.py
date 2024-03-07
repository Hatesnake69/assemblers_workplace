import datetime

from app.models import WbTaskModel, WbSupplyModel
from app.models.wb.wb_tasks import Status
from app.schemas.wb_order_schemas import OrdersResponseFromWb, OrderFromWb


def assert_task_fields(mock_wb_task: WbTaskModel):
    assert mock_wb_task.task_state == Status.GET_SUPPLY_STICKER

    assert WbSupplyModel.objects.filter(task=mock_wb_task).exists()

    assert mock_wb_task.assembler_document
    assert mock_wb_task.package_document
    assert mock_wb_task.wb_order_qr_document
    assert mock_wb_task.wb_supply_qr_document
    assert mock_wb_task.wb_order_stickers_document


def generate_orders(amount: int) -> OrdersResponseFromWb:
    orders: OrdersResponseFromWb = OrdersResponseFromWb(orders=[])
    for i in range(amount):
        orders.orders.append(
            OrderFromWb(
                id=i + 1,
                rid=f"dA.{i}.0",
                createdAt=(
                    datetime.datetime.today() - datetime.timedelta(days=i)
                ).strftime("%Y-%m-%dT%H:%M:%SZ"),
                warehouseId=1,
                supplyId="",
                offices=[],
                address={},
                user={},
                skus=[i],
                price=100,
                convertedPrice=100,
                currencyCode=100,
                convertedCurrencyCode=100,
                orderUid=f"uid.{i}.0",
                deliveryType="delivery",
                nmId=1,
                chrtId=1,
                article="article",
            )
        )
    return orders
