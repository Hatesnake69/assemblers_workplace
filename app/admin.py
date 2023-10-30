from django.contrib import admin

from .models import WbSupplyModel, WbOrderModel, WbOrderProductModel, TaskModel


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
        "is_active",
        "package_document",
        "assembler_document",
        "wb_order_qr_document",
        "wb_supply_qr_document",
        "wb_order_stickers_document",
    )

    exclude = (
        "task_state",
    )

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
