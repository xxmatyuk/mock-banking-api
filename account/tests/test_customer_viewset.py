from django.test import TestCase
from rest_framework import status

from account.models import Customer, BankAccount


class TestAccountViewSet(TestCase):
    """ Tests for CustomersViewSet API """

    def setUp(self):
        customer = Customer(name="Test Test Jr.")
        customer.save()

        bank_account = BankAccount(owner=customer, balance=100.00)
        bank_account.save()

        self.default_customer = customer

    def test_create_customer_happy_path(self):
        """ Tests initial customer creation """

        request_data = {
            "name": "Test Test",
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json["name"], request_data["name"])
        self.assertIn("id", response_json)

        customer = Customer.objects.get(pk=response_json["id"])
        self.assertEqual(request_data["name"], customer.name)

        bank_account = BankAccount.objects.get(owner__pk=response_json["id"])
        self.assertEqual(request_data["deposit_amount"], bank_account.balance.amount)

    def test_add_banking_account_happy_path(self):
        """ Tests addition of a banking account """

        request_data = {
            "owner_id": self.default_customer.pk,
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/add-banking-account/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json["owner"], self.default_customer.pk)
        self.assertIn("id", response_json)

        bank_account = BankAccount.objects.get(pk=response_json["id"])
        self.assertEqual(request_data["deposit_amount"], bank_account.balance.amount)
        self.assertEqual(self.default_customer, bank_account.owner)

    def test_add_multiple_banking_accounts_happy_path(self):
        """ Tests ensures a customer may have multiple banking accounts """

        request_data = {
            "owner_id": self.default_customer.pk,
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/add-banking-account/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json["owner"], self.default_customer.pk)
        self.assertIn("id", response_json)

        response = self.client.post('/customers/add-banking-account/', request_data)
        response_json = response.json()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json["owner"], self.default_customer.pk)
        self.assertIn("id", response_json)

    def test_get_balances_happy_path_single_banking_acc(self):
        """ Tests getting customer's accounts' balances (single banking account)"""

        uri = '/customers/{}/accounts-balances/'.format(self.default_customer.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = [
            {
                "id": 1,
                "balance_currency": "GBP",
                "balance": "100.00",
                "owner": self.default_customer.pk
            }
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        banking_account = BankAccount.objects.get(owner__pk=self.default_customer.pk)
        self.assertEqual(response_json[0]["balance_currency"], "GBP")
        self.assertEqual(response_json[0]["balance"], str(banking_account.balance.amount))

    def test_get_balances_happy_path_multiple_banking_accs(self):
        """ Tests getting customer's accounts' balances (multiple banking accounts)"""

        second_bank_account = BankAccount(owner=self.default_customer, balance=150.00)
        second_bank_account.save()

        uri = '/customers/{}/accounts-balances/'.format(self.default_customer.pk)
        response = self.client.get(uri)
        response_json = response.json()
        expected_response_json = [
            {
                "id": 1,
                "balance_currency": "GBP",
                "balance": "100.00",
                "owner": self.default_customer.pk
            },
            {
                "id": 2,
                "balance_currency": "GBP",
                "balance": "150.00",
                "owner": self.default_customer.pk
            },
            
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response_json, expected_response_json)

        banking_accounts = BankAccount.objects.filter(owner__pk=self.default_customer.pk).order_by("id")
        self.assertEqual(response_json[0]["balance_currency"], "GBP")
        self.assertEqual(response_json[0]["balance"], "100.00")
        self.assertEqual(response_json[1]["balance_currency"], "GBP")
        self.assertEqual(response_json[1]["balance"], "150.00")

    def test_get_balances_cutomer_does_not_exist(self):
        """ Verify it's not possible to get the balance of an unexistent entity """
        response = self.client.get('/customers/42/accounts-balances/')
        response_json = response.json()

        expected_error_json = {
            "detail": "Account with id 42 does not exist"
        }

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_missing_name(self):
        """ Missing customer name """

        request_data = {
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "name": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_empty_name(self):
        """ Empty customer name """

        request_data = {
            "name": "",
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "name": [
                "This field may not be blank."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_missing_deposit(self):
        """ Missing deposit """

        request_data = {
            "name": "Test Test II"
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "deposit_amount": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_empty_deposit(self):
        """ Empty deposit """

        request_data = {
            "name": "Test Test II",
            "deposit_amount": ""
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "deposit_amount": [
                "A valid number is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_negative_deposit(self):
        """ Negative deposit """

        request_data = {
            "name": "Test Test II",
            "deposit_amount": -100
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "deposit_amount": [
                "Ensure this value is greater than or equal to 0."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)
        
    def test_create_customer_rubbish_deposit(self):
        """ Rubbush deposit """

        request_data = {
            "name": "Test Test II",
            "deposit_amount": "rubbish"
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "deposit_amount": [
                "A valid number is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_empty_request(self):
        """ Empty request """

        request_data = {}

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = {
            "deposit_amount": [
                "This field is required."
            ],
            "name": [
                "This field is required."
            ]
        }

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)

    def test_create_customer_already_exists(self):
        """ Customer already exists """

        request_data = {
            "name": self.default_customer.name,
            "deposit_amount": 1000.00
        }

        response = self.client.post('/customers/create-customer-account/', request_data)
        response_json = response.json()

        expected_error_json = [
            "Customer '%s' already exists" % self.default_customer.name
        ]

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response_json, expected_error_json)
