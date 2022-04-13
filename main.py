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


def predict_rub_salary_hh(currency, payment_from, payment_to):
    if currency == 'RUR':
        if payment_from and payment_to:
            return predict_salary(payment_from, payment_to)
        elif payment_from:
            return payment_from * 1.2
        else:
            return payment_to * 0.8


def get_salary_statistics_hh(language):
    salaries_stats = {}
    salaries = []
    vacancies = get_vacancies_hh(language)
    for vacancy in vacancies:
        currency = vacancy['salary']['currency']
        payment_from = vacancy['salary']['from']
        payment_to = vacancy['salary']['to']
        salary = predict_rub_salary_hh(currency, payment_from, payment_to)
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
    print_terminaltables(stats, title)


def get_vacancies_sj(language):
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
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


def predict_rub_salary_sj(currency, payment_from, payment_to):
    if currency == 'rub':
        is_payment_from = bool(payment_from)
        is_payment_to = bool(payment_to)
        if is_payment_from and is_payment_to:
            return predict_salary(
                payment_from,
                payment_to
            )
        elif is_payment_from:
            return payment_from * 1.2
        elif is_payment_to:
            return payment_to * 0.8


def get_salary_statistics_sj(language):
    salaries_stats = {}
    salaries = []
    vacancies = get_vacancies_sj(language)
    for vacancy in vacancies:
        currency = vacancy['currency']
        payment_from = vacancy['payment_from']
        payment_to = vacancy['payment_to']
        salary = predict_rub_salary_sj(currency, payment_from, payment_to)
        if salary:
            salaries.append(salary)
    salaries_stats['vacancies_found'] = len(vacancies)
    salaries_stats['vacancies_processed'] = len(salaries)
    salaries_stats['average_salary'] = int(statistics.mean(salaries))
    return salaries_stats


def get_table_statistics_sj():
    title = 'SuperJob Moscow'
    stats = {}
    for language in LANGUAGES:
        stats[language] = get_salary_statistics_sj(language)
    print_terminaltables(stats, title)


def predict_salary(salary_from, salary_to):
    return (salary_from + salary_to) / 2


def print_terminaltables(stats, title):
    title = title
    head = [
        'Язык программирования',
        'Вакансий найдено',
        'Вакансий обработано',
        'Средняя зарплата'
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
    load_dotenv()
    get_table_statistics_hh()
    get_table_statistics_sj()


if __name__ == '__main__':
    main()
