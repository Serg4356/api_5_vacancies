import requests
import os



def sj_auth(client_id, redirect_uri, login, password):
    url = 'https://api.superjob.ru/2.0/oauth2/password'
    params = {
        'login': login,
        'password': password,
        'client_id': client_id,
        'client_secret': secret_key
    }
    response = requests.get(url, params)
    response.raise_for_status()
    return response


def get_vacancies_sj(access_token, secret_key, lang, page=None):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {
        'X-Api-App-Id': secret_key,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'keyword': lang,
        'town': 4, # Moscow
        'count': 100,
    }
    vacancies = []
    for page in range(5):
        params['page'] = page
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        vacancies += response.json()['objects']
    return response.json()['total'], vacancies


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])

