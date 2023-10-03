from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver

from assemblers_workplace.settings import settings
from .models import TaskModel, WbSupplyModel, WbOrderModel
from .models.wb_account_warehouses import WbAccountWarehouseModel
from .services.api_request_service import RequestAPI
from .services.wb_orders_service import WbOrdersService


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
    if instance.task_state == "NEW":
        pass
    elif instance.task_state == "CREATE_SUPPLY":
        supply_name = f"{instance.employee} {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
        new_supply = wb_order_service.create_new_supply(
            name=supply_name, task=instance
        )
    elif instance.task_state == "ADD_ORDERS":
        supply = WbSupplyModel.objects.get(task=instance)
        new_orders = wb_order_service.get_new_orders(supply=supply)
    elif instance.task_state == "GET_ORDERS_STICKERS":
        supply = WbSupplyModel.objects.get(task=instance)
        new_orders = [
            order for order in WbOrderModel.objects.filter(supply=supply)
        ]
        wb_order_service.get_order_stickers(orders=new_orders)
    elif instance.task_state == "SEND_SUPPLY_TO_DELIVER":
        supply = WbSupplyModel.objects.get(task=instance)
        wb_order_service.send_supply_to_deliver(supply=supply)
    elif instance.task_state == "GET_SUPPLY_STICKER":
        supply = WbSupplyModel.objects.get(task=instance)
        wb_order_service.get_supply_sticker(supply=supply)
    elif instance.task_state == "CLOSE":
        instance.is_active = False
        instance.save()
