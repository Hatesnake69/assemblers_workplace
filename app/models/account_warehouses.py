from django.db import models
from app.models.business_accounts import BusinessAccountModel


class AccountWarehouseModel(models.Model):
    objects = models.Manager()  # Add the default manager

    wb_id = models.PositiveIntegerField(null=True)
    ozon_id = models.PositiveIntegerField(null=True)

    warehouse = models.ForeignKey(
        "app.WarehouseModel",
        related_name="account_warehouses",
        blank=True,
        on_delete=models.CASCADE,
    )
    business_account = models.ForeignKey(
        BusinessAccountModel,
        on_delete=models.CASCADE,
        related_name="account_warehouses",
    )
    processing_flag = models.BooleanField(
        default=False
    )

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "account_warehouses"

    def __str__(self):
        return f"{self.business_account}, {self.warehouse}"

    def set_processing(self):
        self.processing_flag = True
        self.save()

    def set_idle(self):
        self.processing_flag = False
        self.save()
