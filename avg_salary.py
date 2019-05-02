import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from sj import sj_auth, get_vacancies_sj, predict_rub_salary_sj


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


def get_vacancies_count_per_language_hh():
    vacancies_count = {}
    url = 'https://api.hh.ru/vacancies'
    for lang in LANGUAGES:
        params = {
            'text': f'(Программист OR Разработчик) AND {lang}',
            'area': 1, # Moscow
            'period': 30,
            'pages': 2,
            'per_page': 100
        }
        response = requests.get(url, params)
        response.raise_for_status()
        vacancies_count[lang] = response.json()['found']
    vacancies_count = sorted(vacancies_count.items(),
                                key=lambda item: item[1],
                                reverse=True)
    return vacancies_count


def predict_salary(salary_from, salary_to):
    if salary_from and salary_to:
        return (salary_from + salary_to)//2
    elif salary_from:
        return int(salary_from*1.2)
    elif salary_to:
        return int(salary_to*0.8)


def predict_rub_salary_hh(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        return predict_salary(vacancy['salary']['from'], vacancy['salary']['to'])


def predict_rub_salary(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        if vacancy['salary']['from'] and vacancy['salary']['to']:
            return (vacancy['salary']['from'] + vacancy['salary']['to'])//2
        elif vacancy['salary']['from']:
            return int(vacancy['salary']['from'] * 1.2)
        else:
            return int(vacancy['salary']['to'] * 0.8)


def get_salaries_list(vacancies, site):
    if site == 'hh':
        return [predict_rub_salary_hh(vacancy) for vacancy in vacancies]
    elif site == 'sj':
        return [predict_rub_salary_sj(vacancy) for vacancy in vacancies]


def calculate_average_salary_hh():
    lang_avg_salary = {}
    for lang in LANGUAGES:
        try:
            vacancies_found, lang_vacancies = get_vacancies_hh(lang)
            lang_salaries = [salary for salary in get_salaries_list(lang_vacancies, 'hh') if salary]
            if len(lang_salaries):
                avg_salary = int(sum(lang_salaries)/len(lang_salaries))
            else:
                avg_salary = 0

            lang_avg_salary[lang] = {
                'vacancies_found': vacancies_found,
                'vacancies_proccessed': len(lang_salaries),
                'average_salary': avg_salary
            }
        except requests.exceptions.HTTPError:
            print(f'Warning! Server sent bad response, while fetching {lang} vacancies')
    return lang_avg_salary


def calculate_average_salary(**kwargs):
    lang_avg_salary = {}
    for lang in LANGUAGES:
        try:
            if kwargs['site'] == 'sj':
                vacancies_found, lang_vacancies = get_vacancies_sj(kwargs['access_token'],
                                                                   kwargs['secret_key'],
                                                                   lang)
            elif kwargs['site'] == 'hh':
                vacancies_found, lang_vacancies = get_vacancies_hh(lang)
            else:
                print('Invalid function argument "site"')
                return

            lang_salaries = [salary for salary in get_salaries_list(lang_vacancies,
                                                                    kwargs['site']) if salary]
            if len(lang_salaries):
                avg_salary = int(sum(lang_salaries)/len(lang_salaries))
            else:
                avg_salary = 0
            lang_avg_salary[lang] = {
                'vacancies_found': vacancies_found,
                'vacancies_proccessed': len(lang_salaries),
                'average_salary': avg_salary
            }
        except requests.exceptions.HTTPError:
            print(f'Warning! Server sent bad response, while fetching {lang} vacancies')
    return lang_avg_salary

def calculate_average_salary_sj(access_token, secret_key):
    lang_avg_salary = {}
    for lang in LANGUAGES:
        try:
            vacancies_found, lang_vacancies = get_vacancies_sj(access_token,
                                                               secret_key,
                                                               lang)
            lang_salaries = [salary for salary in get_salaries_list(lang_vacancies,
                                                                    'sj') if salary]
            if len(lang_salaries):
                avg_salary = int(sum(lang_salaries)/len(lang_salaries))
            else:
                avg_salary = 0
            lang_avg_salary[lang] = {
                'vacancies_found': vacancies_found,
                'vacancies_proccessed': len(lang_salaries),
                'average_salary': avg_salary
            }
        except requests.exceptions.HTTPError:
            print(f'Warning! Server sent bad response, while fetching {lang} vacancies')
    return lang_avg_salary


def make_table(lang_avg_salary, table_title):
    table_data = []
    table_data.append(['Language',
                       'average_salary',
                       'vacancies_found',
                       'vacancies_proccessed'])
    for lang, lang_info in lang_avg_salary.items():
        table_row = [lang]
        for column in table_data[0][1:]:
            table_row.append(lang_info[column])
        table_data.append(table_row)

    return AsciiTable(table_data, table_title).table



if __name__ == '__main__':
    load_dotenv()
    login = os.getenv('login')
    password = os.getenv('password')
    secret_key = os.getenv('secret_key')
    client_id = os.getenv('client_id')
    redirect_uri = os.getenv('redirect_uri')
    try:
        sj_access_token = sj_auth(client_id,
                                  redirect_uri,
                                  login,
                                  password).json()['access_token']
    except requests.exceptions.HTTPError:
        print('Warning! Returned bad response')

    sj_table = make_table(calculate_average_salary(access_token=sj_access_token,
        secret_key=secret_key, site='sj'), 'SuperJob')
    hh_table = make_table(calc_average_salary(site='hh'), 'HeadHunter')
    print(sj_table)
    print()
    print(hh_table)

