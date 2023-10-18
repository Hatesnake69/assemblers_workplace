# Generated by Django 4.2.5 on 2023-10-14 22:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0013_rename_stickers_document_taskmodel_stickers_pdf_doc_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="taskmodel",
            name="qr_document",
        ),
        migrations.RemoveField(
            model_name="taskmodel",
            name="stickers_pdf_doc",
        ),
        migrations.AddField(
            model_name="taskmodel",
            name="wb_order_qr_document",
            field=models.FileField(blank=True, null=True, upload_to="media/files/qr"),
        ),
        migrations.AddField(
            model_name="taskmodel",
            name="wb_order_stickers_pdf_doc",
            field=models.FileField(
                blank=True, null=True, upload_to="media/files/barcodes"
            ),
        ),
        migrations.AddField(
            model_name="taskmodel",
            name="wb_supply_qr_document",
            field=models.FileField(blank=True, null=True, upload_to="media/files/qr"),
        ),
        migrations.AlterField(
            model_name="taskmodel",
            name="task_state",
            field=models.CharField(
                choices=[
                    ("NEW", "New"),
                    ("CREATE_SUPPLY", "Create Supply"),
                    ("ADD_ORDERS", "Add Orders"),
                    ("GET_ORDERS_STICKERS", "Get Orders Stickers"),
                    ("SEND_SUPPLY_TO_DELIVER", "Send Supply To Deliver"),
                    ("GET_SUPPLY_STICKER", "Get Supply Sticker"),
                    ("CLOSE", "Close"),
                ],
                default="NEW",
                max_length=32,
            ),
        ),
    ]
