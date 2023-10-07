from django.contrib import admin
from nested_admin.nested import NestedModelAdmin, NestedTabularInline

from .models import WbSupplyModel, WbOrderModel, WbOrderProductModel, TaskModel


class WbOrderProductInline(NestedTabularInline):
    model = WbOrderProductModel
    readonly_fields = (
        "name",
        "quantity",
        "barcode",
        "photo",
        "packaging_class",
        "code",
        "storage_location",
    )
    max_num = 0
    extra = 0


class WbOrderInline(NestedTabularInline):
    model = WbOrderModel
    extra = 0
    readonly_fields = (
        "order_products",
        "wb_id",
        "wb_rid",
        "wb_created_at",
        "wb_warehouse_id",
        "wb_supply_id",
        "wb_offices",
        "wb_address",
        "wb_user",
        "wb_skus",
        "wb_price",
        "wb_converted_price",
        "wb_currency_code",
        "wb_converted_currency_code",
        "wb_order_uid",
        "wb_delivery_type",
        "wb_nm_id",
        "wb_chrt_id",
        "wb_article",
        "wb_is_large_cargo",
        "partA",
        "partB",
        "barcode",
        "svg_file",
    )
    fields = (
        "wb_id",
        "wb_article",
        "wb_rid",
        "wb_skus",
        "wb_price",
        "svg_file",
    )
    max_num = 0
    inlines = [WbOrderProductInline]


class WbSupplyInline(NestedTabularInline):
    model = WbSupplyModel
    readonly_fields = (
        "wb_id",
        "wb_name",
        "wb_done",
        "created_at",
        "closed_at",
        "deleted_at",
        "svg_file",
        "wb_orders",
    )
    max_num = 0
    inlines = [WbOrderInline]
    fields = (
        "wb_id",
        "wb_name",
        "svg_file",
    )


@admin.register(TaskModel)
class TaskModelAdmin(NestedModelAdmin):
    list_display = (
        "employee",
        "amount",
        "business_account",
        "warehouse",
        "task_state",
        "is_active",
    )
    readonly_fields = (
        "employee",
        "amount",
        "business_account",
        "warehouse",
        "task_state",
        "is_active",
    )
    inlines = [WbSupplyInline]

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
