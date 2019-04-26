import requests
import json
import simplejson
from pprint import pprint
import datetime


LANGS = [
    'Java',
    'C++',
    'Python',
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


def save_to_file(name, data):
    with open(name, 'w') as file:
        file.write(data)


def get_all_vacancies(pages):
    result = []
    url = 'https://api.hh.ru/vacancies'
    for page in range(1, pages+1):
        params = {
            'text': 'Программист',
            'area': 1,
            'pages': f'{page}',
            'per_page': 100,
        }
        response = requests.get(url, params)
        response.raise_for_status()
        result.append(response.json())
    return simplejson.dumps(result, indent=4, sort_keys=True, ensure_ascii=False)


def get_all_vacancies_from_page(page):
    url = 'https://api.hh.ru/vacancies'
    params = {
        'text': 'программист Java',
        'area': 1,
        'period': 30,
        'pages': f'{page}',
        'per_page': 100
    }
    response = requests.get(url, params)
    response.raise_for_status()
    return response.json()


def get_vacancies(lang):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    for page in range(20):
        params = {
            'text': f'(программист OR разработчик) AND {lang}',
            'area': 1,
            'period': 30,
            'pages': f'{page}',
            'per_page': 100
        }
        print(f'fetching {lang} {page}...')
        response = requests.get(url, params)
        response.raise_for_status()
        print('pages: {}'.format(response.json()['pages']))
        print('vacancies found: {}'.format(response.json()['found']))
        print('len of vacancies on the current page: {}'.format(len(response.json()['items'])))
        print('len of vacancies list {}'.format(len(vacancies)))
        vacancies += response.json()['items']

    return response.json()['found'], vacancies


def get_vacancies_count_per_lang():
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


def save_preproc(json_data):
    return simplejson.dumps(json_data, indent=4, sort_keys=True, ensure_ascii=False)


def predict_rub_salary(vacancy):
    if vacancy['salary'] and vacancy['salary']['currency'] == 'RUR':
        if vacancy['salary']['from'] and vacancy['salary']['to']:
            return (vacancy['salary']['from'] + vacancy['salary']['to'])//2
        elif vacancy['salary']['from']:
            return int(vacancy['salary']['from'] * 1.2)
        else:
            return int(vacancy['salary']['to'] * 0.8)


def get_salaries_list(vacancies):
    return [predict_rub_salary(vacancy) for vacancy in vacancies]


def calc_lang_avg_salary():
    lang_avg_salary = {}
    for lang in LANGS:
        try:
            vacancies_found, lang_vacancies = get_vacancies(lang)
            print('len of vacancies: {}|| languge: {}'.format(len(lang_vacancies), lang))
            lang_salaries = [salary for salary in get_salaries_list(lang_vacancies) if salary]
            lang_avg_salary[lang] = {
                'vacancies_found': vacancies_found,
                'vacancies_proccessed': len(lang_salaries),
                'average_salary': int(sum(lang_salaries)/len(lang_salaries))
            }
        except requests.exceptions.HTTPError:
            print(f'Warning! Server sent bad response, while fetching {lang} vacancies')
    return lang_avg_salary



if __name__ == '__main__':
    #save_to_file('test2.json', save_preproc(get_vacancies('python')))
    #pprint(get_vacancies('python'))
    pprint(calc_lang_avg_salary())
    #pprint(get_vacancies_count_per_lang())
