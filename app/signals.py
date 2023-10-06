from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import TaskModel, WbSupplyModel, WbOrderModel
from .models.tasks import Status
from .models.wb_account_warehouses import WbAccountWarehouseModel
from .services.wb_orders_service import WbOrdersService
from .utils.disable_signals import DisableSignals


@receiver(post_save, sender=TaskModel)
def create_task(sender, instance: TaskModel, created, **kwargs):
    if created:
        return
    amount = instance.amount
    current_account = instance.business_account
    account_warehouse = WbAccountWarehouseModel.objects.get(
        business_account=instance.business_account,
        warehouse=instance.warehouse,
    )
    wb_token = current_account.wb_token
    wb_order_service = WbOrdersService(
        wb_token=wb_token, amount=amount, warehouse_id=account_warehouse.wb_id
    )
    if instance.task_state == Status.NEW.value:
        supply_name = (
            f"{instance.employee} {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
        )
        new_supply = wb_order_service.create_new_supply(name=supply_name, task=instance)
        print("new_supply")
        with DisableSignals():
            instance.task_state = Status.CREATE_SUPPLY
            instance.save()

    elif instance.task_state == Status.CREATE_SUPPLY.value:
        supply = WbSupplyModel.objects.get(task=instance)
        new_orders = wb_order_service.get_new_orders(supply=supply)
        print("new_orders")
        with DisableSignals():
            instance.task_state = Status.ADD_ORDERS
            instance.save()
    elif instance.task_state == Status.ADD_ORDERS.value:
        supply = WbSupplyModel.objects.get(task=instance)
        new_orders = [order for order in WbOrderModel.objects.filter(supply=supply)]
        wb_order_service.get_order_stickers(orders=new_orders)
        print("orders_added to supply")
        with DisableSignals():
            instance.task_state = Status.GET_ORDERS_STICKERS
            instance.save()
    elif instance.task_state == Status.GET_ORDERS_STICKERS.value:
        supply = WbSupplyModel.objects.get(task=instance)
        wb_order_service.send_supply_to_deliver(supply=supply)
        print("orders stickers received")
        with DisableSignals():
            instance.task_state = Status.SEND_SUPPLY_TO_DELIVER
            instance.save()
    elif instance.task_state == Status.SEND_SUPPLY_TO_DELIVER.value:
        supply = WbSupplyModel.objects.get(task=instance)
        wb_order_service.get_supply_sticker(supply=supply)
        print("supply sent")

        with DisableSignals():
            instance.task_state = Status.GET_SUPPLY_STICKER
            instance.save()
    elif instance.task_state == Status.GET_SUPPLY_STICKER.value:
        print("task closed")
        with DisableSignals():
            instance.task_state = Status.CLOSE
            instance.is_active = False
            instance.save()
