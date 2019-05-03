import requests
import os
from terminaltables import AsciiTable
from dotenv import load_dotenv
from sj import sj_auth, get_vacancies_for_languages_sj
from hh import get_vacancies_for_languages_hh



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


def calculate_average_salary(vacancies, site):
    average_salaries = {}
    for language in vacancies.keys():
        salaries = [predict_site_salary(vacancy, site)\
                    for vacancy in vacancies[language][1]]
        salaries = [salary for salary in salaries if salary]
        if len(salaries):
            average_salary = int(sum(salaries)/len(salaries))
        else:
            average_salary = 0
        average_salaries[language] = {
            'vacancies_found': vacancies[language][0],
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
    sj_vacancies = get_vacancies_for_languages_sj(access_token=sj_access_token,
                                                  secret_key=secret_key,
                                                  languages=LANGUAGES)
    sj_table = make_table(calculate_average_salary(sj_vacancies, 'sj'),
                          'SuperJob')
    hh_vacancies = get_vacancies_for_languages_hh(LANGUAGES)
    hh_table = make_table(calculate_average_salary(hh_vacancies, 'hh'),
                          'HeadHunter')
    print(sj_table)
    print()
    print(hh_table)

