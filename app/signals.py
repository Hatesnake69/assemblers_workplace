from django.core.files.base import ContentFile
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import TaskModel, WbSupplyModel, WbOrderModel
from .models.tasks import Status
from .models.wb_account_warehouses import WbAccountWarehouseModel
from .services.wb_orders_service import WbOrdersService
from .utils.assemblers_page import create_assemblers_page_html
from .utils.disable_signals import DisableSignals
from .utils.file_service import (
    create_wb_orders_qr_pdf,
    create_stickers_pdf,
    create_wb_supply_qr_pdf,
)


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
            supply_name = (
                f"{instance.employee} {instance.created_at.strftime('%Y-%m-%d %H:%M')}"
            )
            new_supply = wb_order_service.create_new_supply(name=supply_name, task=instance)
            instance.task_state = Status.CREATE_SUPPLY
            instance.save()
            print("new supply created")
            supply = WbSupplyModel.objects.get(task=instance)
            new_orders = wb_order_service.get_new_orders(supply=supply)
            instance.amount = len(new_orders)
            instance.task_state = Status.ADD_ORDERS
            instance.save()
            print("new orders added")
            supply = WbSupplyModel.objects.get(task=instance)
            new_orders = [order for order in WbOrderModel.objects.filter(supply=supply)]
            wb_order_service.get_order_stickers(orders=new_orders)
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
            document_pdf = create_assemblers_page_html(
                task_instance=instance, supply_instance=supply
            )
            instance.document.save(
                f"{instance.id}_document.pdf", ContentFile(document_pdf.read())
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
            instance.wb_order_stickers_pdf_doc.save(
                f"{instance.id}_sku_stickers_qr.pdf", ContentFile(barcodes_pdf.read())
            )
            instance.save()
            print("supply sent")
        if instance.task_state == Status.GET_SUPPLY_STICKER.value:
            instance.task_state = Status.CLOSE
            instance.is_active = False
            instance.save()
            print("task closed")
