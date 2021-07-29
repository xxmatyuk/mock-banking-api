from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from drf_spectacular.utils import extend_schema

from account.models import BankAccount, Transaction, Customer
from account.serializers import CreateCustomerSerializer, CustomerResponseSerializer, BankingAccountSerializer,\
    TransactionHistoryResponseSerializer, NewTransactionSerializer, BankingAccountResponseSerializer


class BankingAccountsViewSet(ViewSet):

    """ API for getting account details """

    @extend_schema(responses={status.HTTP_200_OK:BankingAccountResponseSerializer})
    @action(methods=["GET"], detail=True, url_path="get-balance")
    def get_balance(self, request, pk):
        try:
            account = BankAccount.objects.get(id=pk)
            serializer = BankingAccountResponseSerializer(account)
            return Response(serializer.data)
        except ObjectDoesNotExist:
            return Response({"detail": "Banking account with id %s does not exist" % pk}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)

    @extend_schema(responses={status.HTTP_200_OK:TransactionHistoryResponseSerializer})
    @action(methods=["GET"], detail=True, url_path="get-history")
    def get_history(self, request, pk):
        try:
            transactions = Transaction.objects.filter(Q(sender_account__pk=pk) | Q(recipient_account__pk=pk))
            history = TransactionHistoryResponseSerializer(transactions, many=True)
            return Response(history.data)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)


class CustomersViewSet(ViewSet):

    """ API for adding new customer and banking account """
    
    @extend_schema(
        request=CreateCustomerSerializer,
        responses={status.HTTP_200_OK:CustomerResponseSerializer}
    )
    @action(methods=["POST"], detail=False, url_path="create-customer-account")
    def create_customer_account(self, request):
        try:
            serializer = CreateCustomerSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            customer = serializer.save()
            response_serializer = CustomerResponseSerializer(customer)
            return Response(response_serializer.data)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)

    @extend_schema(
        request=BankingAccountSerializer,
        responses={status.HTTP_200_OK:BankingAccountResponseSerializer}
    )
    @action(methods=["POST"], detail=False, url_path="add-banking-account")
    def add_banking_account(self, request):
        try:
            serializer = BankingAccountSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            banking_account = serializer.save()
            response_serializer = BankingAccountResponseSerializer(banking_account)
            return Response(response_serializer.data)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)

    @extend_schema(responses={status.HTTP_200_OK:BankingAccountResponseSerializer})
    @action(methods=["GET"], detail=True, url_path="accounts-balances")
    def get_balances(self, request, pk=None):
        # NOTE: BankAccount.objects.filter(owner__pk=pk) would make querying of a customer 
        #       to be unnecessary step, though trying to be verbose on a purpose to return
        #       a corresponding API error.
        try:
            owner = Customer.objects.get(pk=pk)
            accounts = BankAccount.objects.filter(owner=owner)
            balances = BankingAccountResponseSerializer(accounts, many=True)
            return Response(balances.data)
        except ObjectDoesNotExist:
            return Response({"detail": "Account with id %s does not exist" % pk}, status=status.HTTP_404_NOT_FOUND)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)


class TransactionsViewSet(ViewSet):

    """ API for manking transactions """
    
    @extend_schema(
        request=NewTransactionSerializer,
        responses={status.HTTP_200_OK:TransactionHistoryResponseSerializer}
    )
    @action(methods=["POST"], detail=False, url_path="make")
    def make_transaction(self, request):
        try:
            serializer = NewTransactionSerializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            transaction = serializer.save()
            response_serializer = TransactionHistoryResponseSerializer(transaction)
            return Response(response_serializer.data)
        except APIException as e:
            raise e
        except Exception as e:
            raise APIException(e)
