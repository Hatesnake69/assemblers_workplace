from django.db import models


class WbBusinessAccountModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=128)
    wb_token = models.TextField()

    # wb_account_warehouses = models.ManyToManyField(
    #     "app.WbWarehouseModel", related_name="wb_business_accounts", blank=True
    # )

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "wb_business_accounts"

    def __str__(self):
        return self.name
