import os
import statistics
from itertools import count

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

LANGUAGES = [
    'JavaScript', 'Python', 'Java', 'TypeScript',
    'C#', 'PHP', 'C++', 'Kotlin', 'Swift', 'Go',
]


def get_vacancies_hh(language):
    vacancies = []
    url = 'https://api.hh.ru/vacancies'
    for page in count(0):
        params = {
            'text': f'Программист {language}',
            'specialization': '1.221',
            'area': 1,
            'period': 30,
            'only_with_salary': True,
            'page': page,
            'per_page': 100,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        some_vacancies = response.json()
        vacancies.extend(some_vacancies['items'])
        if page >= some_vacancies['pages']:
            break
    return vacancies


def predict_rub_salary_hh(vacancy):
    if vacancy['currency'] == 'RUR':
        if vacancy['from'] and vacancy['to']:
            return predict_salary(vacancy['from'], vacancy['to'])
        elif vacancy['from']:
            return vacancy['from'] * 1.2
        else:
            return vacancy['to'] * 0.8


def get_salary_statistics_hh(language):
    salaries_stats = {}
    salaries = []
    vacancies = get_vacancies_hh(language)
    for vacancy in vacancies:
        salary = predict_rub_salary_hh(vacancy['salary'])
        if salary:
            salaries.append(salary)
    salaries_stats['vacancies_found'] = len(vacancies)
    salaries_stats['vacancies_processed'] = len(salaries)
    salaries_stats['average_salary'] = int(statistics.mean(salaries))
    return salaries_stats


def get_table_statistics_hh():
    title = 'HeadHunter Moscow'
    stats = {}
    for language in LANGUAGES:
        stats[language] = get_salary_statistics_hh(language)
    get_terminaltables(stats, title)


def get_vacancies_sj(language, secret_key):
    vacancies = []
    url = 'https://api.superjob.ru/2.0/vacancies/'
    headers = {'X-Api-App-Id': secret_key}
    for page in count(1):
        params = {
            'keyword': f'Программист {language}',
            'town': 'Москва',
            'key': 48,
            'page': page,
        }
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        some_vacancies = response.json()
        vacancies.extend(some_vacancies['objects'])
        if len(vacancies) >= some_vacancies['total']:
            break
    return vacancies


def predict_rub_salary_sj(vacancy):
    if vacancy['currency'] == 'rub':
        is_payment_from = bool(vacancy['payment_from'])
        is_payment_to = bool(vacancy['payment_to'])
        if is_payment_from and is_payment_to:
            return predict_salary(
                vacancy['payment_from'],
                vacancy['payment_to']
            )
        elif is_payment_from:
            return vacancy['payment_from'] * 1.2
        elif is_payment_to:
            return vacancy['payment_to'] * 0.8


def get_salary_statistics_sj(language, secret_key):
    salaries_stats = {}
    salaries = []
    vacancies = get_vacancies_sj(language, secret_key)
    for vacancy in vacancies:
        salary = predict_rub_salary_sj(vacancy)
        if salary:
            salaries.append(salary)
    salaries_stats['vacancies_found'] = len(vacancies)
    salaries_stats['vacancies_processed'] = len(salaries)
    salaries_stats['average_salary'] = int(statistics.mean(salaries))
    return salaries_stats


def get_table_statistics_sj():
    load_dotenv()
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    title = 'SuperJob Moscow'
    stats = {}
    for language in LANGUAGES:
        stats[language] = get_salary_statistics_sj(language, secret_key)
    get_terminaltables(stats, title)


def predict_salary(salary_from, salary_to):
    return (salary_from + salary_to) / 2


def get_terminaltables(stats, title):
    title = title
    head = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата,'
    ]
    table = [head]
    for language in stats:
        line = []
        line.append(language)
        for key, item in stats[language].items():
            line.append(item)
        table.append(line)
    table_instance = AsciiTable(table, title)
    table_instance.justify_columns[2] = 'right'
    print(table_instance.table)


def main():
    get_table_statistics_hh()
    get_table_statistics_sj()


if __name__ == '__main__':
    main()
