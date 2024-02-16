from django.db import models


class BusinessAccountModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=128)
    wb_token = models.TextField(null=True)
    ozon_client_id = models.TextField(null=True)
    ozon_api_token = models.TextField(null=True)

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "business_accounts"

    def __str__(self):
        return self.name
