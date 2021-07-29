from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import serializers
from rest_framework.exceptions import APIException

from djmoney.money import Money

from account.models import Customer, BankAccount, Transaction


class BaseBankingSerializer(serializers.Serializer):
    """ Base serializer class """

    deposit_amount = serializers.DecimalField(max_digits=14, decimal_places=2, min_value=0, required=True)


class CreateCustomerSerializer(BaseBankingSerializer):
    """ Serializer class for handling customer creation """

    name = serializers.CharField(max_length=1024, required=True)

    def create(self, validated_data):
        try:    
            customer = Customer(name=validated_data["name"])
            customer.save()

            bank_account = BankAccount(owner=customer, balance=validated_data["deposit_amount"])
            bank_account.save()

            return customer
        except IntegrityError:
            raise serializers.ValidationError("Customer '%s' already exists" % validated_data["name"])


class BankingAccountSerializer(BaseBankingSerializer):
    """ Serializer class for handling banking account creation """

    owner_id = serializers.IntegerField(required=True)

    def create(self, validated_data):
        try:
            customer = Customer.objects.get(id=validated_data["owner_id"])
            bank_account = BankAccount(owner=customer, balance=Money(validated_data["deposit_amount"], 'GBP'))
            bank_account.save()

            return bank_account
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Customer with id %s does not exist" % validated_data["owner_id"])


class NewTransactionSerializer(BaseBankingSerializer):
    """ Serializer class for handling a transaction """

    from_banking_account = serializers.IntegerField(required=True)
    to_banking_account = serializers.IntegerField(required=True)

    def validate(self, data):
        try:
            from_account = BankAccount.objects.get(id=data["from_banking_account"])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Sender with id %s does not exist" % data["from_banking_account"])

        try:
            to_acount = BankAccount.objects.get(id=data["to_banking_account"])
        except ObjectDoesNotExist:
            raise serializers.ValidationError("Recipient with id %s does not exist" % data["to_banking_account"])

        if from_account.balance.amount < data["deposit_amount"]:
            raise serializers.ValidationError("Insufficient funds")

        return data

    def create(self, validated_data):
        try:
            from_account = BankAccount.objects.get(id=validated_data["from_banking_account"])
            from_account.balance.amount -= validated_data["deposit_amount"]

            to_acount = BankAccount.objects.get(id=validated_data["to_banking_account"])
            to_acount.balance.amount += validated_data["deposit_amount"]

            transaction = Transaction(
                sender_account=from_account,
                recipient_account=to_acount,
                amount=validated_data["deposit_amount"]
            )
        except Exception as e:
            raise APIException("Unable to make a transaction")
        else:
            from_account.save()
            to_acount.save()
            transaction.save()
            return transaction


class CustomerResponseSerializer(serializers.ModelSerializer):
    """ Serializer class for customer creation response """

    class Meta:
        model = Customer
        fields = ["id", "name"]


class TransactionHistoryResponseSerializer(serializers.ModelSerializer):
    """ Serializer class for transaction history response """

    class Meta:
        model = Transaction
        fields = '__all__'


class BankingAccountResponseSerializer(serializers.ModelSerializer):
    """ Serizlier class banking account balance response """

    class Meta:
        model = BankAccount
        fields = '__all__'
