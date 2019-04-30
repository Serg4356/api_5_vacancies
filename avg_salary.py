import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv


LANGS = [
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


def get_vacancies_sj(access_token, secret_key, lang):
    url = 'https://api.superjob.ru/2.0/vacancies'
    headers = {
        'X-Api-App-Id': secret_key,
        'Authorization': f'Bearer {access_token}'
    }
    params = {
        'keyword': lang,
        'town': 4,
        'count': 100,
    }
    vacancies = []
    for page in range(5):
        params['page'] = page
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        vacancies += response.json()['objects']
    return response.json()['total'], vacancies


def get_vacancies_hh(lang):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    params = {
            'text': f'(программист OR разработчик) AND {lang}',
            'area': 1,
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


def get_vacancies_count_per_lang_hh():
    vacancies_count = {}
    url = 'https://api.hh.ru/vacancies'
    for lang in LANGS:
        params = {
            'text': f'(Программист OR Разработчик) AND {lang}',
            'area': 1,
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


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        return predict_salary(vacancy['payment_from'], vacancy['payment_to'])


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


def calc_lang_avg_salary_hh():
    lang_avg_salary = {}
    for lang in LANGS:
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


def calc_lang_avg_salary_sj(access_token, secret_key):
    lang_avg_salary = {}
    for lang in LANGS:
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

    sj_table = make_table(calc_lang_avg_salary_sj(sj_access_token,
                                                    secret_key), 'SuperJob')
    hh_table = make_table(calc_lang_avg_salary_hh(), 'HeadHunter')
    print(sj_table)
    print()
    print(hh_table)

