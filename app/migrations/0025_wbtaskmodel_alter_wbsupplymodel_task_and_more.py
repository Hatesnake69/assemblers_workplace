# Generated by Django 4.2.5 on 2024-02-16 11:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0024_accountwarehousemodel_ozon_id_and_more"),
    ]

    operations = [
        migrations.RenameModel('TaskModel', 'WbTaskModel'),
        migrations.AlterModelTable(
            name='WbTaskModel',
            table='wb_tasks',
        ),
        migrations.AlterField(
            model_name="wbsupplymodel",
            name="task",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="app.wbtaskmodel",
            ),
        ),
        migrations.AlterModelOptions(
            name="wbtaskmodel",
            options={
                "verbose_name": "Сборочное задание WB",
                "verbose_name_plural": "Сборочные задания WB",
            },
        ),
    ]
