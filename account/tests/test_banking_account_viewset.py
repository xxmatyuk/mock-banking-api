from django.test import TestCase
from rest_framework import status

from account.models import Customer, Transaction, BankAccount


from freezegun import freeze_time

class TestBakingAccountVieSet(TestCase):
    """ Tests for TransactionsViewSet API """

    def setUp(self):
        sender = Customer(name="Test Sender")
        sender.save()

        sender_bank_account_one = BankAccount(owner=sender, balance=100.00)
        sender_bank_account_one.save()

        sender_bank_account_two = BankAccount(owner=sender, balance=150.00)
        sender_bank_account_two.save()

        reciever_one = Customer(name="Test Reciever")
        reciever_one.save()

        reciever_one_bank_account = BankAccount(owner=reciever_one, balance=200.00)
        reciever_one_bank_account.save()

        reciever_two = Customer(name="Test Reciever II")
        reciever_two.save()

        reciever_two_bank_account = BankAccount(owner=reciever_two, balance=200.00)
        reciever_two_bank_account.save()

        self.default_sender = sender
        self.default_sender_bank_account_one = sender_bank_account_one
        self.default_sender_bank_account_two = sender_bank_account_two
        self.default_reciever_one = reciever_one
        self.default_reciever_one_bank_account = reciever_one_bank_account
        self.default_reciever_two = reciever_two
        self.default_reciever_two_bank_account = reciever_two_bank_account

    def test_get_balance_happy_path(self):
        """ Tests getting banking account balance details """

        uri = '/accounts/{}/get-balance/'.format(self.default_sender_bank_account_one.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = {
            "id": 1,
            "balance_currency": "GBP",
            "balance": "100.00",
            "owner": self.default_sender_bank_account_one.pk
        }

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        bank_acc = BankAccount.objects.get(pk=self.default_sender_bank_account_one.pk)
        self.assertEqual(response_json["balance"], str(bank_acc.balance.amount))

    @freeze_time("2021-07-08 12:00:00")
    def test_get_account_history_happy_path(self):
        """ Verifies it's possible to get transactions history """

        # Make a bunch of transactions between three customers and four wallets
        request_data = {
            "from_banking_account": self.default_sender_bank_account_one.pk,
            "to_banking_account": self.default_reciever_one_bank_account.pk,
            "deposit_amount": 50.01
        }

        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request_data = {
            "from_banking_account": self.default_sender_bank_account_one.pk,
            "to_banking_account": self.default_reciever_two_bank_account.pk,
            "deposit_amount": 13.12
        }

        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request_data = {
            "from_banking_account": self.default_sender_bank_account_two.pk,
            "to_banking_account": self.default_reciever_one_bank_account.pk,
            "deposit_amount": 5.01
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        request_data = {
            "from_banking_account": self.default_reciever_one_bank_account.pk,
            "to_banking_account": self.default_sender_bank_account_two.pk,
            "deposit_amount": 4.99
        }
        response = self.client.post('/transactions/make/', request_data)
        response_json = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check the first wallet transaction history (the first customer)
        uri = "/accounts/{}/get-history/".format(self.default_sender_bank_account_one.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = [
            {
                "id": 1,
                "amount_currency": "GBP",
                "amount": "50.01",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_one.pk,
                "recipient_account": self.default_reciever_one_bank_account.pk
            },
            {
                "id": 2,
                "amount_currency": "GBP",
                "amount": "13.12",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_one.pk,
                "recipient_account": self.default_reciever_two_bank_account.pk
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        # Check the second wallet transaction history (the first customer)
        uri = "/accounts/{}/get-history/".format(self.default_sender_bank_account_two.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = [
            {
                "id": 3,
                "amount_currency": "GBP",
                "amount": "5.01",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_two.pk,
                "recipient_account": self.default_reciever_one_bank_account.pk
            },
            {
                "id": 4,
                "amount_currency": "GBP",
                "amount": "4.99",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_reciever_one_bank_account.pk,
                "recipient_account": self.default_sender_bank_account_two.pk
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        # Check the third wallet transaction history (the second customer)
        uri = "/accounts/{}/get-history/".format(self.default_reciever_one_bank_account.pk)
        response = self.client.get(uri)
        response_json = response.json()        
        expected_response_json = [
            {
                "id": 4,
                "amount_currency": "GBP",
                "amount": "4.99",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_reciever_one_bank_account.pk,
                "recipient_account": self.default_sender_bank_account_two.pk
            },
            {
                "id": 1,
                "amount_currency": "GBP",
                "amount": "50.01",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_one.pk,
                "recipient_account": self.default_reciever_one_bank_account.pk
            },
            {
                "id": 3,
                "amount_currency": "GBP",
                "amount": "5.01",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_two.pk,
                "recipient_account": self.default_reciever_one_bank_account.pk
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        # Check the fourth wallet transaction history (the third customer)
        uri = "/accounts/{}/get-history/".format(self.default_reciever_two_bank_account.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = [
            {
                "id": 2,
                "amount_currency": "GBP",
                "amount": "13.12",
                "date": "2021-07-08T12:00:00Z",
                "sender_account": self.default_sender_bank_account_one.pk,
                "recipient_account": self.default_reciever_two_bank_account.pk
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

    def test_get_account_empty_history_happy_path(self):
        """ Checks if empty list is returned in case of no transactions have been made """

        uri = "/accounts/{}/get-history/".format(self.default_reciever_two_bank_account.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = []

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

    def test_unexistent_account_balance(self):
        """ Verify it's not possible to get balance of unexistent account """
        response = self.client.get('/accounts/42/get-balance/')
        response_json = response.json()
        expected_response_json = {
            "detail": "Banking account with id 42 does not exist"
        }

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, expected_response_json)

    def test_invalid_string_acc_id(self):
        """ Tests getting single banking account balance details """
        
        response = self.client.get('/accounts/one/get-balance/')
        response_json = response.json()
        expected_error_json = {
            "detail": "Field 'id' expected a number but got 'one'."
        }
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response_json, expected_error_json)
