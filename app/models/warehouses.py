from django.db import models


class WarehouseModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=128)

    class Meta:
        db_table = "warehouses"

    def __str__(self):
        return self.name
