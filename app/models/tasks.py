from django.db import models


class TaskModel(models.Model):

    class Status(models.Choices):
        NEW = "NEW"
        CREATE_SUPPLY = "CREATE_SUPPLY"
        ADD_ORDERS = "ADD_ORDERS"
        GET_ORDERS_STICKERS = "GET_ORDERS_STICKERS"
        SEND_SUPPLY_TO_DELIVER = "SEND_SUPPLY_TO_DELIVER"
        GET_SUPPLY_STICKER = "GET_SUPPLY_STICKER"
        CLOSE = "CLOSE"

    objects = models.Manager()  # Add the default manager

    employee = models.ForeignKey("app.EmployeeModel", on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(default=10)
    business_account = models.ForeignKey(
        "app.WbBusinessAccountModel", on_delete=models.CASCADE
    )
    warehouse = models.ForeignKey("app.WbWarehouseModel", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_created=True, auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)
    task_state = models.CharField(max_length=32, choices=Status.choices, default=Status.NEW)
    is_active = models.BooleanField(default=True)

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "tasks"

    def __str__(self):
        return f"{self.employee} {self.created_at.strftime('%Y-%m-%d %H:%M')}"
