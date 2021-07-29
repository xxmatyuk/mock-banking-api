from decimal import Decimal

from django.test import TestCase
from rest_framework import status

from account.models import Customer, Transaction, BankAccount


class TestTransactionsViewSet(TestCase):
    """ Tests for TransactionsViewSet API """

    def setUp(self):
        sender = Customer(name="Test Sender")
        sender.save()

        sender_bank_account = BankAccount(owner=sender, balance=100.00)
        sender_bank_account.save()

        reciever = Customer(name="Test Reciever")
        reciever.save()

        reciever_bank_account = BankAccount(owner=reciever, balance=100.00)
        reciever_bank_account.save()

        self.default_sender = sender
        self.default_sender_bank_account = sender_bank_account
        self.default_reciever = reciever
        self.default_reciever_bank_account = reciever_bank_account

    def test_make_transaction_happy_path(self):
        """ Happy path transaction test """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": 50.01
        }

        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json["sender_account"], self.default_sender_bank_account.pk)
        self.assertEqual(response_json["recipient_account"], self.default_reciever_bank_account.pk)
        self.assertEqual(response_json["amount"], str(request_data["deposit_amount"]))

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('49.99'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('150.01'))

    def test_make_transaction_insufficient_funds(self):
        """ Checks it's impossible to transfer more than a current balance """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": 100.01
        }

        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()
        expected_response_json = {
            "non_field_errors":
                ["Insufficient funds"]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)
        
        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_unexistent_sender(self):
        """ Sender account does not exist """

        request_data = {
            "from_banking_account": 42,
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": 50.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "non_field_errors": [
                "Sender with id 42 does not exist"
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_unexistent_reciever(self):
        """ Receiver account does not exist """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": 42,
            "deposit_amount": 50.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "non_field_errors": [
                "Recipient with id 42 does not exist"
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_jumbo_amount(self):
        """ Unrealistic deposit amount"""

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": 500000000000000000.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "deposit_amount": [
                "Ensure that there are no more than 14 digits in total."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_missing_sender(self):
        """ Sender is missing in a request """

        request_data = {
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": 50.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "from_banking_account": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_missing_reciever(self):
        """ Reciever is missing in a request """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "deposit_amount": 50.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "to_banking_account": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_missing_deposit_amount(self):
        """ Deposit amount is missing in a request """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": self.default_reciever_bank_account.pk,
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "deposit_amount": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_empty_request(self):
        """ Deposit amount is missing in a request """

        request_data = {}
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        expected_response_json = {
            "deposit_amount": [
                "This field is required."
            ],
            "from_banking_account": [
                "This field is required."
            ],
            "to_banking_account": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_response_json)

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))

    def test_negative_deposit_amount(self):
        """ Negative deposit amount """

        request_data = {
            "from_banking_account": self.default_sender_bank_account.pk,
            "to_banking_account": self.default_reciever_bank_account.pk,
            "deposit_amount": -50.01
        }

        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        expected_response_json = {
            "deposit_amount": [
                "Ensure this value is greater than or equal to 0."
            ]
        }

        sender_bank_acc = BankAccount.objects.get(owner__pk=self.default_sender.pk)
        self.assertEqual(sender_bank_acc.balance.amount, Decimal('100.00'))

        reciever_bank_acc = BankAccount.objects.get(owner__pk=self.default_reciever.pk)
        self.assertEqual(reciever_bank_acc.balance.amount, Decimal('100.00'))
