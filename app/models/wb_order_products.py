from django.db import models


class WbOrderProductModel(models.Model):
    objects = models.Manager()

    order = models.ForeignKey("app.WbOrderModel", on_delete=models.CASCADE)

    name = models.TextField(null=True, blank=True)
    quantity = models.IntegerField()
    barcode = models.TextField(null=True, blank=True)
    photo = models.TextField(null=True, blank=True)
    code = models.TextField(null=True, blank=True)
    storage_location = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "wb_order_products"
