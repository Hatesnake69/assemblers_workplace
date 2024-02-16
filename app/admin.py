from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import (
    WbSupplyModel,
    WbOrderModel,
    WbOrderProductModel,
    TaskModel,
    AllowedIpModel,
    EmployeeModel,
    FailedNmIdProductModel,
    BusinessAccountModel
)


@admin.register(EmployeeModel)
class EmployeeModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


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

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            # Если не нажата кнопка "Save and add another" или "Save and continue editing"
            return HttpResponseRedirect(reverse('admin:%s_%s_change' % (
                obj._meta.app_label,
                obj._meta.model_name,
            ), args=[obj.pk]))
        return super().response_add(request, obj, post_url_continue)

    def response_change(self, request, obj, post_url_continue=None):
        return HttpResponseRedirect(reverse('admin:%s_%s_change' % (
            obj._meta.app_label,
            obj._meta.model_name,
        ), args=[obj.pk]))

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


@admin.register(AllowedIpModel)
class WbSupplyModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "ip",
        "created_at",
        "updated_at",
    )


@admin.register(BusinessAccountModel)
class BusinessAccountModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
    )


@admin.register(FailedNmIdProductModel)
class FailedNmIdProductModelAdmin(admin.ModelAdmin):
    list_display = (
        "nm_id",
        "name",
        "wb_order_id",
        "fixed",
        "created_at",
    )
    list_filter = ("fixed",)

