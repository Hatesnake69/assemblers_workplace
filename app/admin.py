from django.contrib import admin
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import path

from .forms import MyCustomForm
from .models import WbSupplyModel, WbOrderModel, WbOrderProductModel, TaskModel
from django import forms


class WbSuppliesInline(admin.TabularInline):
    model = WbSupplyModel


@admin.register(TaskModel)
class TaskModelAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "amount",
        "business_account",
        "warehouse",
        "created_at",
        "updated_at",
    )
    search_fields = ("employee",)
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
