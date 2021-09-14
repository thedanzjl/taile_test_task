from django.contrib import admin
from .models import Transaction, Account


class AccountAdmin(admin.ModelAdmin):
    search_fields = ('user__username', 'user__first_name', 'user__last_name')


class TransactionAdmin(admin.ModelAdmin):
    ...


admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Account, AccountAdmin)
