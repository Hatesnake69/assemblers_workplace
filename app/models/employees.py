from django.db import models


class EmployeeModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=128)

    class Meta:
        # Указывает имя таблицы в базе данных
        db_table = "employees"

    def __str__(self):
        return self.name
