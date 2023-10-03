from django.db import models


class WbOrderModel(models.Model):
    objects = models.Manager()  # Add the default manager

    supply = models.ForeignKey(
        "app.WbSupplyModel", on_delete=models.CASCADE, null=True, blank=True
    )

    order_products = models.ManyToManyField(
        "app.WbOrderProductModel",
        related_name="orders",
        blank=True,
    )

    wb_id = models.IntegerField(unique=True)
    wb_rid = models.CharField(max_length=128)
    wb_created_at = models.CharField(max_length=128)
    wb_warehouse_id = models.IntegerField()
    wb_supply_id = models.CharField(max_length=128, null=True, blank=True)
    wb_offices = models.CharField(max_length=128)
    wb_address = models.CharField(max_length=128)
    wb_user = models.CharField(max_length=128)
    wb_skus = models.CharField(max_length=128)
    wb_price = models.IntegerField()
    wb_converted_price = models.IntegerField()
    wb_currency_code = models.IntegerField()
    wb_converted_currency_code = models.IntegerField()
    wb_order_uid = models.CharField(max_length=128)
    wb_delivery_type = models.CharField(max_length=128)
    wb_nm_id = models.IntegerField()
    wb_chrt_id = models.IntegerField()
    wb_article = models.CharField(max_length=128)
    wb_is_large_cargo = models.BooleanField()

    partA = models.IntegerField(null=True, blank=True)
    partB = models.IntegerField(null=True, blank=True)
    barcode = models.TextField(null=True, blank=True)
    svg_file = models.TextField(null=True, blank=True)

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "wb_orders"
