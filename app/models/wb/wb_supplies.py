from django.db import models


class WbSupplyModel(models.Model):
    objects = models.Manager()  # Add the default manager

    task = models.ForeignKey(
        "app.WbTaskModel", on_delete=models.CASCADE, null=True, blank=True
    )

    wb_id = models.CharField(max_length=128, unique=True)
    wb_name = models.CharField(max_length=128)
    wb_done = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    svg_file = models.TextField(null=True, blank=True)

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "wb_supplies"
