from django.db import models

from assemblers_workplace.settings import settings


class Status(models.Choices):
    NEW = "NEW"
    CREATE_SUPPLY = "CREATE_SUPPLY"
    ADD_ORDERS = "ADD_ORDERS"
    GET_ORDERS_STICKERS = "GET_ORDERS_STICKERS"
    SEND_SUPPLY_TO_DELIVER = "SEND_SUPPLY_TO_DELIVER"
    GET_SUPPLY_STICKER = "GET_SUPPLY_STICKER"
    CLOSE = "CLOSE"


class TaskModel(models.Model):
    objects = models.Manager()  # Add the default manager

    employee = models.ForeignKey(
        "app.EmployeeModel", on_delete=models.CASCADE, verbose_name="Сотрудник",
    )
    amount = models.PositiveIntegerField(
        default=1, verbose_name="Количество",
    )
    business_account = models.ForeignKey(
        "app.WbBusinessAccountModel", on_delete=models.CASCADE, verbose_name="Аккаунт",
    )
    warehouse = models.ForeignKey(
        "app.WbWarehouseModel", on_delete=models.CASCADE, verbose_name="Склад",
    )
    created_at = models.DateTimeField(
        auto_created=True, auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True, blank=True)
    task_state = models.CharField(
        max_length=32, choices=Status.choices, default=Status.NEW
    )
    package_document = models.FileField(
        upload_to="files/package_doc", null=True, blank=True, verbose_name="Упаковочный лист",
    )
    assembler_document = models.FileField(
        upload_to="files/assemblers_doc", null=True, blank=True, verbose_name="Сборочный лист",
    )
    wb_order_qr_document = models.FileField(
        upload_to="files/orders_qr", null=True, blank=True, verbose_name="Лист WB qr-кодов",
    )
    wb_supply_qr_document = models.FileField(
        upload_to="files/supply_qr", null=True, blank=True, verbose_name="Qr-код поставки",
    )
    wb_order_stickers_document = models.FileField(
        upload_to="files/barcodes", null=True, blank=True, verbose_name="Лист WB штрихкодов",
    )
    is_active = models.BooleanField(
        default=True, verbose_name="Активно",
    )

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "tasks"
        verbose_name = "Сборочное задание"  # Название модели в единственном числе
        verbose_name_plural = "Сборочные задания"  # Название модели во множественном числе

    def __str__(self):
        return f"{self.employee} {self.created_at.astimezone(settings.timezone).strftime('%Y-%m-%d %H:%M')}"
