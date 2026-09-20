"""Load/save for the vacancy listings shown on the Vacancy page."""

from config import VACANCY_FILE
from utils.file_utils import read_json_list, write_json_list


def load_vacancies():
    return read_json_list(VACANCY_FILE)


def save_vacancies(vacancies):
    write_json_list(VACANCY_FILE, vacancies)
