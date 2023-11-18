import datetime

from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TaskModel, WbSupplyModel, WbOrderModel
from .models.tasks import Status
from .models.wb_account_warehouses import WbAccountWarehouseModel
from .services.wb_orders_service import WbOrdersService
from .utils.assemble_doc import create_assemble_doc
from .utils.disable_signals import DisableSignals
from .utils.file_service import (
    create_wb_orders_qr_pdf,
    create_stickers_pdf,
    create_wb_supply_qr_pdf,
)
from .utils.package_doc import create_package_doc


@receiver(post_save, sender=TaskModel)
def create_task(sender, instance: TaskModel, created, **kwargs):
    with DisableSignals():
        if created:
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
            moscow_time = instance.created_at + datetime.timedelta(hours=3)
            supply_name = (
                f"{instance.employee} {moscow_time.strftime('%Y-%m-%d %H:%M')}"
            )
            new_supply = wb_order_service.create_new_supply(name=supply_name, task=instance)
            instance.task_state = Status.CREATE_SUPPLY
            instance.save()
            print("new supply created")
            supply = WbSupplyModel.objects.get(task=instance)
            new_orders = wb_order_service.get_new_orders(supply=supply)
            instance.amount = len(new_orders)
            if not new_orders:
                raise Exception("На данном аккаунте пока нет заказов :-(")
            instance.task_state = Status.ADD_ORDERS
            instance.save()
            print("new orders added")
            supply = WbSupplyModel.objects.get(task=instance)
            new_orders = [order for order in WbOrderModel.objects.filter(supply=supply)]
            batch_size = 100
            for orders_batch in (new_orders[i:i + batch_size] for i in range(0, len(new_orders), batch_size)):
                wb_order_service.get_order_stickers(orders=orders_batch)
            instance.task_state = Status.GET_ORDERS_STICKERS
            instance.save()
            print("orders added to supply")
            supply = WbSupplyModel.objects.get(task=instance)
            wb_order_service.send_supply_to_deliver(supply=supply)
            instance.task_state = Status.SEND_SUPPLY_TO_DELIVER
            instance.save()
            print("orders stickers received")
            supply = WbSupplyModel.objects.get(task=instance)
            wb_order_service.get_supply_sticker(supply=supply)
            instance.task_state = Status.GET_SUPPLY_STICKER
            instance.save()
            supply = WbSupplyModel.objects.get(task=instance)
            assembler_document_pdf = create_assemble_doc(
                task_instance=instance, supply_instance=supply
            )
            instance.assembler_document.save(
                f"{instance.id}_assemble_document.pdf", ContentFile(assembler_document_pdf.read())
            )
            package_document_pdf = create_package_doc(
                task_instance=instance, supply_instance=supply
            )
            instance.package_document.save(
                f"{instance.id}_package_document.pdf", ContentFile(package_document_pdf.read())
            )
            qr_pdf = create_wb_orders_qr_pdf(task_instance=instance)
            instance.wb_order_qr_document.save(
                f"{instance.id}_qr_stickers.pdf", ContentFile(qr_pdf.read())
            )
            supply_qr = create_wb_supply_qr_pdf(task_instance=instance)
            instance.wb_supply_qr_document.save(
                f"{instance.id}_supply_qr.pdf", ContentFile(supply_qr.read())
            )
            barcodes_pdf = create_stickers_pdf(task_instance=instance)
            instance.wb_order_stickers_document.save(
                f"{instance.id}_sku_stickers_qr.pdf", ContentFile(barcodes_pdf.read())
            )
            instance.save()
            print("supply sent")
        if instance.task_state == Status.GET_SUPPLY_STICKER.value:
            instance.task_state = Status.CLOSE
            instance.is_active = False
            instance.save()
            print("task closed")
