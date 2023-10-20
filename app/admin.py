from django.contrib import admin
from django.db import models
from django.forms import FileField
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import WbSupplyModel, WbOrderModel, WbOrderProductModel, TaskModel


class FileLinkWidget(FileField):
    def render(self, name, value, attrs=None, renderer=None):
        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        # Определяем URL для просмотра файла
        file_url = reverse(
            "admin:%s_%s_download"
            % (self.model._meta.app_label, self.model._meta.model_name),
            args=[str(value)],
        )

        # Создаем HTML для ссылки, которая откроется в новой вкладке
        link = f'<a href="{file_url}" target="_blank">{value}</a>'

        return mark_safe(link)


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "amount",
        "business_account",
        "warehouse",
        "is_active",
    )
    readonly_fields = (
        # "employee",
        # "amount",
        # "business_account",
        # "warehouse",
        "is_active",
        "document",
        "wb_order_qr_document",
        "wb_supply_qr_document",
        "wb_order_stickers_pdf_doc",
    )

    exclude = (
        "task_state",
    )

    formfield_overrides = {
        models.FileField: {"widget": FileLinkWidget},
        # Пример изменения виджета для текстового поля
        # Другие поля и виджеты
    }

    def change_view(self, request, object_id, form_url="", extra_context=None):
        extra_context = extra_context or {}
        placeholder = {
            "NEW": "СОЗДАТЬ ПОСТАВКУ",
            "CREATE_SUPPLY": "ДОБАВИТЬ ЗАКАЗЫ",
            "ADD_ORDERS": "ПОЛУЧИТЬ СТИКЕРЫ НА ЗАКАЗЫ",
            "GET_ORDERS_STICKERS": "ОТПРАВИТЬ ПОСТАВКУ В ДОСТАВКУ",
            "SEND_SUPPLY_TO_DELIVER": "ПОЛУЧИТЬ СТИКЕР ПОСТАВКИ",
            "GET_SUPPLY_STICKER": "ЗАКРЫТЬ",
            "CLOSE": "ЗАКРЫТО",
        }
        key = self.model.objects.get(pk=object_id).task_state
        extra_context["task_state"] = placeholder.get(key)

        return super().change_view(
            request,
            object_id,
            form_url,
            extra_context=extra_context,
        )

    # change_form_template = "custom_change_form.html"
    # inlines = [WbSuppliesInline]

    # list_display = ('wb_id', 'wb_name', 'wb_done', 'created_at', 'closed_at', 'deleted_at')
    # list_filter = ('wb_done',)
    # search_fields = ('wb_id', 'wb_name')
    # readonly_fields = ('created_at', 'closed_at', 'deleted_at')
    # fieldsets = (
    #     (None, {'fields': ()}),  # Установите пустые скобки для отображения всех полей из формы
    #     ('Timestamps', {'fields': ('wb_id', 'wb_name', 'wb_done', 'created_at', 'closed_at', 'deleted_at'), 'classes': ('collapse',)}),
    # )


@admin.register(WbOrderModel)
class WbOrderModelAdmin(admin.ModelAdmin):
    list_display = ("wb_id", "wb_rid", "wb_created_at", "wb_price", "svg_file")


@admin.register(WbOrderProductModel)
class WbOrderProductModelAdmin(admin.ModelAdmin):
    list_display = ("name", "quantity", "barcode", "code")


@admin.register(WbSupplyModel)
class WbSupplyModelAdmin(admin.ModelAdmin):
    list_display = (
        "wb_id",
        "wb_name",
        "wb_done",
        "created_at",
        "closed_at",
        "deleted_at",
        "svg_file",
    )
