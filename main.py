import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from sj import sj_auth, get_vacancies_sj
from hh import get_vacancies_hh



LANGUAGES = [
    'Java',
    'C++',
    'Python',
    'Kotlin',
    'Delphi',
    'Pascal',
    'Javascript',
    'Swift',
    'Ruby',
    'Php',
    'C',
    'C#',
    'Go',
    'Shell',
    'Objective-C',
    'Scala',
    'TypeScript'
]


def get_vacancies_hh(lang):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    params = {
            'text': f'(программист OR разработчик) AND {lang}',
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
            print(f'fetching {lang} {page}...')
            response = requests.get(url, params)
            response.raise_for_status()
            vacancies += response.json()['items']

    return response.json()['found'], vacancies


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)//2
    elif salary_from:
        return int(salary_from*1.2)
    elif salary_to:
        return int(salary_to*0.8)


def predict_site_salary(vacancy, site):
    if site == 'sj' and vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])
    elif site == 'hh' and vacancy['salary'] \
        and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def calculate_average_salary(**site_args):
    average_salaries = {}
    for language in LANGUAGES:
        if site_args['site'] == 'sj':
            vacancies_found, vacancies = get_vacancies_sj(site_args['access_token'],
                                                          site_args['secret_key'],
                                                          language)
        elif site_args['site'] == 'hh':
            vacancies_found, vacancies = get_vacancies_hh(language)
        else:
            print('Invalid function argument "site"')
            return
        salaries = [predict_site_salary(vacancy,
                                        site_args['site']) for vacancy in vacancies]
        salaries = [salary for salary in salaries if salary]
        if len(salaries):
            average_salary = int(sum(salaries)/len(salaries))
        else:
            average_salary = 0
        average_salaries[language] = {
            'vacancies_found': vacancies_found,
            'vacancies_proccessed': len(salaries),
            'average_salary': average_salary
        }
    return average_salaries


def make_table(average_salaries, table_title):
    table_data = []
    table_data.append(['Language',
                       'average_salary',
                       'vacancies_found',
                       'vacancies_proccessed'])
    for language, language_info in average_salaries.items():
        table_row = [language]
        for column in table_data[0][1:]:
            table_row.append(language_info[column])
        table_data.append(table_row)

    return AsciiTable(table_data, table_title).table



if __name__ == '__main__':
    load_dotenv()
    login = os.getenv('login')
    password = os.getenv('password')
    secret_key = os.getenv('secret_key')
    client_id = os.getenv('client_id')
    redirect_uri = os.getenv('redirect_uri')
    sj_access_token = sj_auth(client_id,
                          secret_key,
                          login,
                          password).json()['access_token']
    sj_table = make_table(calculate_average_salary(access_token=sj_access_token,
        secret_key=secret_key, site='sj'), 'SuperJob')
    hh_table = make_table(calculate_average_salary(site='hh'), 'HeadHunter')
    print(sj_table)
    print()
    print(hh_table)

