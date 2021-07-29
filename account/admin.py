from django.contrib import admin

from account.models import Customer, BankAccount, Transaction


class CustomerAdmin(admin.ModelAdmin):
    pass


class BankAccountAdmin(admin.ModelAdmin):
    pass


class TransactionAdmin(admin.ModelAdmin):
    pass

admin.site.register(Customer, CustomerAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(Transaction, TransactionAdmin)
