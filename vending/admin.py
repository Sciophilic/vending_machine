from django.contrib import admin
from .models import Product, Transaction, DenominationLog

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['product_id', 'name', 'product_type', 'price', 'quantity', 'is_available']
    list_filter = ['product_type']
    search_fields = ['name', 'product_id']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['timestamp', 'total_amount_inserted', 'amount_required', 'change_returned']
    readonly_fields = ['timestamp']

@admin.register(DenominationLog)
class DenominationLogAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'denomination', 'quantity_inserted', 'quantity_returned']
    list_filter = ['denomination']