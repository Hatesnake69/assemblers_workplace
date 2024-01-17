from django.db import models


class AllowedIpModel(models.Model):
    objects = models.Manager()  # Add the default manager

    name = models.CharField(max_length=256)
    ip = models.CharField(max_length=256)
    created_at = models.DateTimeField(
        auto_created=True, auto_now_add=True
    )
    updated_at = models.DateTimeField(
        auto_now=True, blank=True
    )

    def __str__(self):
        return f"{self.name} {self.ip}"

    class Meta:
        db_table = "allowed_ips"
