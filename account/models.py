from django.db import models

from djmoney.models.fields import MoneyField
from django.conf import settings


class Customer(models.Model):
    """ Model represents customer """

    name = models.CharField(max_length=1024, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Customer"
        verbose_name_plural = "Customers"
        ordering = ['id']


class BankAccount(models.Model):
    """ Model represents customer's bank account """

    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='%(class)s_owner')
    balance = MoneyField(max_digits=19, decimal_places=2, default_currency='GBP')

    def __str__(self):
        return "{} bank account: {}".format(self.owner.name, self.id)

    class Meta:
        verbose_name = "Bank account"
        verbose_name_plural = "Bank accounts"
        ordering = ['id']


class Transaction(models.Model):
    """ Model represents banking transaction """

    sender_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='%(class)s_sender_account')
    recipient_account = models.ForeignKey(BankAccount, on_delete=models.CASCADE, related_name='%(class)s_recipient_account')
    amount = MoneyField(max_digits=19, decimal_places=2, default_currency='GBP')
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Tx: {} Rx: {} Amount: {}".format(self.sender_account.owner, self.recipient_account.owner, self.amount)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ['date']
