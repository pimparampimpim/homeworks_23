"""This module include function process_data, which writes statistics to a file."""


import json
import os
from datetime import date, datetime

MAIL = 'email'
REGISTER = 'registered'


class InvalidDate(Exception):
    """Error for date in not format YYYY-MM-DD."""

    def __init__(self, invalid_date: str) -> None:
        """Create error message.

        Args:
            invalid_date: date in uncorrect format or time
        """
        super().__init__(f'{invalid_date} in uncorrect format YYYY-MM-DD or time')


def to_datetime(regisrated: str, last_login: str) -> datetime | None:
    """Check if the date is in the format and lower then today date and last login date.

    Args:
        regisrated: string with user regisrated date
        last_login: string with user last login

    Raises:
        InvalidDate: if date in not format YYYY-MM-DD

    Returns:
        Object datetime type.
    """
    try:
        regisrated, last_login = date.fromisoformat(regisrated), date.fromisoformat(last_login)
    except ValueError:
        raise InvalidDate(regisrated)
    if regisrated <= datetime.now().date() and regisrated <= last_login:
        return regisrated
    raise InvalidDate(regisrated)


def make_path(path: list) -> None:
    """Make path to output file.

    Args:
        path: list with name of directory and output filename as last element

    Returns:
        None or self without the first element.
    """
    if len(path) == 1:
        return None
    if not os.path.isdir(path[0]):
        os.mkdir(path[0])
    os.chdir(path[0])
    return make_path(path[1:])


def file_found(in_path: str, out_path: str) -> None:
    """Check if the arguments are files.

    Args:
        in_path: path to json file with data on site clients
        out_path: path to json output file

    Raises:
        FileNotFoundError: If in_path is not file
    """
    pwd = os.getcwd()
    if not os.path.isfile(in_path):
        raise FileNotFoundError('Is not a file path')
    if not os.path.isfile(out_path):
        out_path = out_path.replace(pwd, '')
        make_path(out_path.split('/'))
        os.chdir(pwd)


def dict_path(count_dct: dict[datetime, dict]) -> dict[str, dict]:
    """Take a set and two lists and returns a dictionary with statistics.

    Args:
        count_dct:dict with counts

    Returns:
        A dictionary with statistics.
    """
    res_dict = {MAIL: {}, REGISTER: {}}
    regist_len = len(count_dct[REGISTER]) if count_dct[REGISTER] else 1
    email_len = len(count_dct[MAIL]) if count_dct[MAIL] else 1

    for register, mail_host in zip(sorted(count_dct[REGISTER]), count_dct[MAIL]):
        new_register = register.strftime('%Y-%m-%d')
        res_dict[REGISTER][new_register] = round((
            count_dct[REGISTER][register]/regist_len
        )*100, 2,
        )
        res_dict[MAIL][mail_host] = round((count_dct[MAIL][mail_host]/email_len)*100, 2)
    return res_dict


def process_data(input_filepath: str, output_filepath: str) -> None:
    """Take json file and returns emailing and registration statiatic.

    Args:
        input_filepath: path to json file with data on site clients
        output_filepath: path to json output file

    Returns:
        None or error message.

    """
    file_found(input_filepath, output_filepath)
    with open(input_filepath, 'r') as input_file:
        res_dict = {MAIL: {}, REGISTER: {}}
        try:
            data_files = json.load(input_file)
        except json.decoder.JSONDecodeError:
            return 'Input file is empty'

        for user in data_files.values():
            if user.get(REGISTER):
                reg_date = to_datetime(user.get(REGISTER), user.get(
                    'last_login', datetime.now().strftime('%Y-%m-%d'),
                    ))
                res_dict[REGISTER][reg_date] = res_dict.get(reg_date, 0)+1
            if user.get(MAIL):
                user_mail = user.get(MAIL)
                mail_host = user_mail[user_mail.find('@')+1:]
                res_dict[MAIL][mail_host] = res_dict.get(mail_host, 0)+1
        res_dict = dict_path(res_dict)
    with open(output_filepath, 'w') as output_file:
        json.dump(res_dict, output_file, indent=3)
