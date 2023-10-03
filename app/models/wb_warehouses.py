from django.db import models

from app.models.wb_account_warehouses import WbAccountWarehouseModel
from app.models.wb_business_accounts import WbBusinessAccountModel


class WbWarehouseModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=128)

    # wb_account_warehouses = models.ManyToManyField(
    #     WbBusinessAccountModel, related_name="wb_warehouses"
    # )

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "wb_warehouses"

    def __str__(self):
        return self.name
