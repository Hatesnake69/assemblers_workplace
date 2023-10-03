from django.db import models
from app.models.wb_business_accounts import WbBusinessAccountModel


class WbAccountWarehouseModel(models.Model):
    objects = models.Manager()  # Add the default manager

    wb_id = models.PositiveIntegerField()

    warehouse = models.ForeignKey(
        "app.WbWarehouseModel",
        related_name="wb_account_warehouses",
        blank=True,
        on_delete=models.CASCADE,
    )
    business_account = models.ForeignKey(
        WbBusinessAccountModel,
        on_delete=models.CASCADE,
        related_name="wb_account_warehouses",
    )

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "wb_account_warehouses"

    def __str__(self):
        return f"{self.business_account}, {self.warehouse}"
