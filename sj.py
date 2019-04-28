import requests

from pprint import pprint


secret_key = 'v3.r.14163687.6076adaf8c8f1e6ced6f6d8021b49249b1080c6f.d9c90ea99d6ecbfca72d7f1383978120d0805ecb'


def sj_access_token():
    url = 'https://api.superjob.ru/2.0/oauth2/access_token/'
    headers = {
        'X-Api-App_Id': secret_key,
    }
    params = {
        'code': 'c907a',
        'redirect_uri': 'http://www.google.com',
        'client_id': 1062,
        'client_secret': secret_key
    }
    response = requests.post(url, json=params, headers=headers)
    pprint(response.json())


def sj_auth(client_id, redirect_uri):
    url = 'https://api.superjob.ru/2.0/authorize'
    headers = {
        'X-Api-App_Id': secret_key,
    }
    return requests.post(url, json={'client_id': client_id, 'redirect_uri': redirect_uri}, headers= headers)



if __name__ == '__main__':
    client_id = 1062
    redirect_uri = 'http://www.google.com'
    pprint(sj_auth(client_id, redirect_uri).json())
