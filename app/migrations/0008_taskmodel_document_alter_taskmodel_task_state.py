# Generated by Django 4.2.5 on 2023-10-09 08:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0007_alter_taskmodel_task_state"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskmodel",
            name="document",
            field=models.FileField(blank=True, null=True, upload_to="files"),
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
