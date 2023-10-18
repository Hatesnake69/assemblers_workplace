import io
from io import BytesIO

import openpyxl
from django.core.files import File
from django.core.files.base import ContentFile
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from fpdf import FPDF
from openpyxl import load_workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from .models import TaskModel, WbSupplyModel, WbOrderModel
from .models.tasks import Status
from .models.wb_account_warehouses import WbAccountWarehouseModel
from .services.wb_orders_service import WbOrdersService
from .utils.assemblers_page import create_assemblers_page_html
from .utils.disable_signals import DisableSignals
from .utils.file_service import create_wb_orders_qr_pdf, \
    create_stickers_document, create_wb_supply_qr_pdf


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
            supply = WbSupplyModel.objects.get(task=instance)
            document_pdf = create_assemblers_page_html(task_instance=instance, supply_instance=supply)
            instance.document.save(
                f'{instance.id}_document.pdf', ContentFile(document_pdf.read())
            )
            qr_document = create_wb_orders_qr_pdf(task_instance=instance)
            instance.wb_order_qr_document.save(
                f'{instance.id}_qr_stickers.pdf', ContentFile(qr_document.read())
            )
            supply_qr = create_wb_supply_qr_pdf(task_instance=instance)
            instance.wb_supply_qr_document.save(
                f'{instance.id}_supply_qr.pdf', ContentFile(supply_qr.read())
            )
            barcodes_pdf = create_stickers_document(task_instance=instance)
            instance.wb_order_stickers_pdf_doc.save(
                f'{instance.id}_sku_stickers_qr.pdf', ContentFile(barcodes_pdf.read())
            )

            instance.task_state = Status.CLOSE
            instance.is_active = False
            instance.save()
