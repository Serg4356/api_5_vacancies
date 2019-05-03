import requests
import os



def get_vacancies_hh(language):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    params = {
            'text': f'(программист OR разработчик) AND {language}',
            'area': 1, # Moscow
            'period': 30,
            'page': 0,
            'per_page': 100
        }
    response = requests.get(url, params)
    response.raise_for_status()
    pages = response.json()['pages']
    vacancies += response.json()['items']
    if pages:
        for page in range(1, pages):
            params['page'] = page
            print(f'fetching {language} {page}...')
            response = requests.get(url, params)
            response.raise_for_status()
            vacancies += response.json()['items']

    return response.json()['found'], vacancies


def get_vacancies_for_languages_hh(languages):
    vacancies = {}
    for language in languages:
        vacancies[language] = get_vacancies_hh(language)
    return vacancies
