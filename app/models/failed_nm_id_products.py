from django.db import models


class FailedNmIdProductModel(models.Model):
    objects = models.Manager()  # Add the default manager

    nm_id = models.CharField(255, unique=True)
    name = models.TextField(null=True, blank=True)
    wb_order_id = models.CharField(255)
    fixed = models.BooleanField(default=False)
    created_at = models.DateTimeField()

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "failed_nm_id_products"
        verbose_name = "Продукт с проблемным nm_id"  # Название модели в единственном числе
        verbose_name_plural = "Продукты с проблемными nm_id"  # Название модели во множественном числе

    def __str__(self):
        return f"nm_id: {self.nm_id}, name: {self.name}"
