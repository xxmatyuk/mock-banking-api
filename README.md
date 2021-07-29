# Assumptions
- there was no requirement of a currency of an account, so assuming currency is all the same across the board and there's no need
  to solve convertion problem. I've used default currency, so it might be extended.
- assuming there's no limit for number of account for any given customer
- assuming there's no transactions limit (neither by their number per day, nor by the transactoin amount)
- banking has some strict precision rules, so assuming a transaction is no more than 14 digits in total with 2 decimal places after comma (i.e. 13.12)
- there was no requirement on session management and security, so assuming it's beyond the task goal. Session management is a separate task in and of
  itself, so the security is. There's multiple approaches on doing both tasks and each one depends on architechture and infrastructure. That said, in
  a trivial case both are coming almost for free by using cloud solutions. So not covering this part as part of this task, which would certainly do in
  a real life scenario.
- no CI process was required, though docker image and compose file have been intruduced to make it prod-like

# Local installation steps
1. `python3 -m venv <path_to_venv>`
2. `. <path_to_venv>/bin/activate`
3. `pip install -r requirements.txt`

# Running server locally 
`python manage.py runserver <local_port>`

# Running tests
`python manage.py test account.tests`

# Running tests with coverage report
1. `coverage run --source='.' manage.py test account`
2. `coverage report`

# Current coverage report
```
Name                                            Stmts   Miss  Cover
-------------------------------------------------------------------
account/__init__.py                                 0      0   100%
account/admin.py                                   11      0   100%
account/apps.py                                     4      0   100%
account/migrations/0001_initial.py                  7      0   100%
account/migrations/__init__.py                      0      0   100%
account/models.py                                  32      3    91%
account/serializers.py                             69      4    94%
account/tests/__init__.py                           0      0   100%
account/tests/test_banking_account_viewset.py      97      0   100%
account/tests/test_customer_viewset.py            129      0   100%
account/tests/test_transactions_viewset.py        128      0   100%
account/views.py                                   93     20    78%
manage.py                                          12      2    83%
mock_api/__init__.py                                0      0   100%
mock_api/asgi.py                                    4      4     0%
mock_api/settings.py                               23      0   100%
mock_api/urls.py                                   10      0   100%
mock_api/wsgi.py                                    4      4     0%
-------------------------------------------------------------------
TOTAL                                             623     37    94%
```

# Run app in a container
`docker-compose up -d --build`

# Stopping app
`docker-compose down -v --remove-orphans`

# API description

## Swagger spec

Just follow the URI `/api/schema/swagger-ui/`.

## Methods

When there is a request body, the following must be included in the header:

```json
 {"Content-Type": "application/json"}
```

## Create new customer

**PATH:** `/customers/create-customer-account/`

**Request Method:** POST

Sample POST payload:

```json
{
    "name": "Jane Air",
    "deposit_amount": 200
}
```

Sample response:

```json
{
    "id": 1,
    "name": "Jane Air"
}
```

## Add bankink account

**PATH:** `/customers/add-banking-account/`

**Request Method:** POST

Sample POST payload:

```json
{
    "owner_id": 1,
    "deposit_amount": 150
}
```

Sample response:

```json
{
    "id": 2,
    "balance_currency": "GBP",
    "balance": "150.00",
    "owner": 1
}
```

## Get all customer's wallers details

**PATH:** `/customers/<id:int>/accounts-balances/`

`<id:int>` is a customer id

**Request Method:** GET

Sample response:

```json
[
    {
        "id": 1,
        "balance_currency": "GBP",
        "balance": "186.88",
        "owner": 1
    },
    {
        "id": 2,
        "balance_currency": "GBP",
        "balance": "163.12",
        "owner": 1
    }
]
```

## Make a transaction

**PATH:** `/transactions/make/`

**Request Method:** POST

Sample POST payload:

```json
{
    "from_banking_account": 1,
    "to_banking_account": 2,
    "deposit_amount": 13.12
}
```

Sample response:

```json
{
    "id": 1,
    "amount_currency": "GBP",
    "amount": "13.12",
    "date": "2021-07-08T20:48:39.522406Z",
    "sender_account": 1,
    "recipient_account": 2
}
```

## Get details of a sinle banking account

**PATH:** `/accounts/<id:int>/get-balance/`

`<id:int>` is a wallet ID

**Request Method:** GET

Sample response:

```json
{
    "id": 1,
    "balance_currency": "GBP",
    "balance": "186.88",
    "owner": 1
}
```

## Get transactions hist

**PATH:**  `/accounts/<id:int>/get-history/`

**Request Method:** GET

`<id:int>` is a customer ID

```json
[
    {
        "id": 1,
        "amount_currency": "GBP",
        "amount": "13.12",
        "date": "2021-07-08T20:48:39.522406Z",
        "sender_account": 1,
        "recipient_account": 2
    }
]
```