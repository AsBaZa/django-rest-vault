# django-rest-vault

[![repo-size](https://img.shields.io/github/repo-size/AsBaZa/django-rest-vault?style=for-the-badge&logo=appveyor)](https://img.shields.io/github/repo-size/AsBaZa/django-rest-vault?style=for-the-badge&logo=appveyor) 

This code sample uses [Django REST framework](https://www.django-rest-framework.org/)
for building a Web API and [Vault HashiCorp](https://www.vaultproject.io/) for authentication.
The objective of this code is to share a straightforward example on how to use an external
service (with [Django REST framework](https://www.django-rest-framework.org/)) 
to verify authorization for each request.

1. [Architecture](#architecture)
    1. [Vault HashiCorp](#vault-hashicorp)
1. [Usage](#usage)
    1. [Installation](#installation)
    1. [Run the server](#run-the-server)
    1. [Testing the functionality](#testing-the-functionality)
1. [How it works](#how-it-works)


## Architecture

The architecture of this piece of code is pretty simple.

![django-rest-vault](https://user-images.githubusercontent.com/40063730/107853797-4886db00-6e18-11eb-9a45-3b37db9cfc9e.jpg)

### Vault HashiCorp

Vault is deployed in Heroku using the next repository:

https://github.com/jace-ys/heroku-vault

And is available in the next server:

https://vault-heroku.herokuapp.com/

> Note: probably the first request requires a bit of time to have a response due to use
> of a [free dyno on Heroku](https://devcenter.heroku.com/articles/free-dyno-hours)

## Usage

### Installation

First, clone the repository:

```shell
git clone https://github.com/AsBaZa/django-rest-vault.git
```

There are 2 options to execute the Django server:

 1. Running locally using `master` branch
 1. Running in Heroku using `heroku` branch

> Note: Each branch has specific `Readme.md` file with its specific configuration steps.

Once the repository has been cloned, install the required Python modules using 
[pipenv](https://pipenv.pypa.io/en/latest/):

```shell
pipenv install
```

### Run the server

Before running the server, specify a `SECRET_KEY` for the Django server, for example:

```shell
export SECRET_KEY="yb=T8zDMp=m-z>rC2rRcx*RP:pDHae~6jN=(Gqp"
```

And run the server:

```shell
python manage.py runserver
```

### Testing the functionality

Now that the server is running make a `request` to it:

```shell
curl http://127.0.0.1:8000/
```

The expected response is:

```json
{
    "Error 401": "Invalid Token"
}
```

With status `401: Unauthorized`. That it is because we have not provide a valid `Token`.
In order to get a valid `Token`, login against Vault. For that purpose, use the default
User/Password:

 - User: Test
 - Password: User

> **Important Note:** _Vault is deployed in a free Heroku server, so it takes almost a minute
> to unseal. Please go to the next URL and check that Vault is unsealed before Login._
> 
> https://vault-heroku.herokuapp.com
>
> ![image](https://user-images.githubusercontent.com/40063730/107856513-ee424600-6e28-11eb-96f3-6c59aa510fda.png)

```shell
curl --request POST 'https://vault-heroku.herokuapp.com/v1/auth/userpass/login/Test' \
     --data-raw '{"password": "User"}'
```

![Diagrama sin títuldo](https://user-images.githubusercontent.com/40063730/107853604-42dcc580-6e17-11eb-9ac5-171c459d16d5.jpg)

That request will have a response similar to this one:

```json
{
    "request_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
    "lease_id": "",
    "renewable": false,
    "lease_duration": 0,
    "data": null,
    "wrap_info": null,
    "warnings": null,
    "auth": {
        "client_token": "X.XXXXXXXXXXXXXXXXXXXXXXXX",
        "accessor": "XXXXXXXXXXXXXXXXXXXXXXXX",
        "policies": [
            "default"
        ],
        "token_policies": [
            "default"
        ],
        "metadata": {
            "username": "test"
        },
        "lease_duration": 2764800,
        "renewable": true,
        "entity_id": "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX",
        "token_type": "service",
        "orphan": true
    }
}
```

Copy the `client_token` field and `request` again using that value replacing it in the 
next command (delete both `<` and `>` symbols):

```shell
curl --request GET 'http://127.0.0.1:8000/' \
     --header 'X-Vault-Token: <client_token>'
```

If the `Token` is valid, the response should be:

```json
{
    "Hello": "World!"
}
```

## How it works

Lastly, let's explain the functionality of this basic Django REST server. 

The objective of this code was to check the authorization of each `request` against Vault,
using [Django Signals](https://docs.djangoproject.com/en/3.1/topics/signals/) for that
purpose (I recommend this article https://simpleisbetterthancomplex.com/tutorial/2016/07/28/how-to-create-django-signals.html).

Using Django signals, the server gets the `Header` `X-Vault-Token` data of the `request` and 
verifies the Token validation against Vault before a view is called:

```python
# core/signals

import requests
from django.conf import settings


def check_vault_token(sender, environ, **kwargs):
    _ = kwargs
    _ = sender

    # Get Token sent on header `X-Vault-Token`
    x_vault_token = environ.get('HTTP_X_VAULT_TOKEN')

    if x_vault_token:
        # Check Token validation
        r = requests.get(settings.VAULT_TOKEN_LOOKUP_SELF,
                         headers={'X-Vault-Token': x_vault_token})

        # Save the response of Vault using the environ variable `VAULT_TOKEN_RESPONSE`
        environ['VAULT_TOKEN_VALIDATION'] = r.status_code
```

Once the Token validation has been checked, a Python decorator is used to have a `401` or 
`200` response:

```python
# core/decorators

from rest_framework.response import Response
from rest_framework import status


def check_vault_authorization():
    """ Check authorization using Vault Token """

    def decorator(view_func):
        def _wrapped_view(class_django, request, *args, **kwargs):
            # Get Vault Token metadata
            vault_token_response = request.META.get('VAULT_TOKEN_VALIDATION')

            # If status code is not 200, unauthorized
            if vault_token_response != 200:
                response_text = {'Error 401': 'Invalid Token'}

                return Response(data=response_text, status=status.HTTP_401_UNAUTHORIZED)

            return view_func(class_django, request, *args, **kwargs)
        return _wrapped_view
    return decorator
```
