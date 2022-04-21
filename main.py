import os
import statistics
from itertools import count

import requests
from dotenv import load_dotenv
from terminaltables import AsciiTable

LANGUAGES = [
    'JavaScript', 'Python', 'Java', 'TypeScript',
    'C#', 'PHP', 'C++', 'Kotlin', 'Swift', 'Go', 'Cobol',
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


def get_salary_statistics_hh(vacancies):
    salaries_stats = {}
    salaries = []
    for vacancy in vacancies:
        currency = vacancy['salary']['currency']
        payment_from = vacancy['salary']['from']
        payment_to = vacancy['salary']['to']
        salary = predict_rub_salary(currency, payment_from, payment_to)
        if salary:
            salaries.append(salary)
    salaries_stats['vacancies_found'] = len(vacancies)
    salaries_stats['vacancies_processed'] = len(salaries)
    try:
        salaries_stats['average_salary'] = int(statistics.mean(salaries))
    except statistics.StatisticsError:
        salaries_stats['average_salary'] = 'not found'
    return salaries_stats


def get_vacancies_sj(secret_key, language):
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


def get_salary_statistics_sj(vacancies):
    salaries_stats = {}
    salaries = []
    for vacancy in vacancies:
        currency = vacancy['currency']
        payment_from = vacancy['payment_from']
        payment_to = vacancy['payment_to']
        salary = predict_rub_salary(currency, payment_from, payment_to)
        if salary:
            salaries.append(salary)
    salaries_stats['vacancies_found'] = len(vacancies)
    salaries_stats['vacancies_processed'] = len(salaries)
    try:
        salaries_stats['average_salary'] = int(statistics.mean(salaries))
    except statistics.StatisticsError:
        salaries_stats['average_salary'] = 'not found'
    return salaries_stats


def predict_rub_salary(currency, payment_from, payment_to):
    if currency not in ['rub', 'RUR']:
        return None
    if payment_from and payment_to:
        return (payment_from + payment_to) / 2
    elif payment_from:
        return payment_from * 1.2
    elif payment_to:
        return payment_to * 0.8


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
    secret_key = os.getenv("SUPERJOB_SECRET_KEY")
    hh_stats = {}
    sj_stats = {}
    for language in LANGUAGES:
        hh_vacancies = get_vacancies_hh(language)
        hh_stats[language] = get_salary_statistics_hh(hh_vacancies)
        sj_vacancies = get_vacancies_sj(secret_key, language)
        sj_stats[language] = get_salary_statistics_sj(sj_vacancies)
    print_terminaltables(hh_stats, 'HeadHunter Moscow')
    print_terminaltables(sj_stats, 'SuperJob Moscow')


if __name__ == '__main__':
    main()
