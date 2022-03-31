from typing import Any, List, Mapping, Tuple

import csv
import json
import os
import re
import subprocess
import sys


def camel_case(s:str)->str:
  s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])


def extract_row(row: List[str]) -> Tuple[str, str]:
    raw_name = row[0] if len(row) > 0 else ''
    git_url = row[1] if len(row) > 1 else ''
    name = raw_name.title()
    return (name, git_url)


def get_repo_dir_name(result_dir_name, repo_name: str) -> str:
    return os.path.join(result_dir_name, repo_name)


def clone_or_pull(git_url, repo_name, result_dir_name: str):
    repo_dir_name = get_repo_dir_name(result_dir_name, repo_name)
    if os.path.isdir(repo_dir_name):
        exit_code = os.system('cd {repo_dir_name} && git pull origin main'.format(repo_dir_name=repo_dir_name))
        if exit_code != 0:
            exit_code = os.system('cd {repo_dir_name} && git pull origin master'.format(repo_dir_name=repo_dir_name))
            if exit_code != 0:
                print('[❌ERROR] Failed to pull {repo_name}'.format(repo_name=repo_name))
        return
    os.makedirs(result_dir_name, exist_ok=True)  
    exit_code = os.system('cd {result_dir_name} && git clone {git_url} {repo_name}'.format(result_dir_name=result_dir_name, git_url=git_url, repo_name=repo_name))
    if exit_code != 0:
        print('[❌ERROR] Failed to clone {git_url} to {repo_dir_name}'.format(git_url=git_url, repo_dir_name=repo_dir_name))


def _get_submissions(file_names: List[str], checkers: List[Mapping[str, Any]], min_index: int, max_index: int) -> Mapping[str, List[str]]:
    submissions: Mapping[str, List[str]] = {}
    for checker in checkers:
        for index in range(min_index, max_index+1):
            task_name = checker["name"].format(index=index)
            if task_name in submissions:
                continue
            submissions[task_name] = []
            patterns = checker["patterns"]
            for pattern in patterns:
                re_pattern = re.compile(pattern.format(index=index), re.IGNORECASE)
                for file_name in file_names:
                    if re.match(re_pattern, file_name):
                        submissions[task_name].append(file_name)
    return submissions


def get_submissions(repo_name, result_dir_name: str, checkers: List[Mapping[str, Any]], min_index:int, max_index: int) -> Mapping[str, List[str]]:
    repo_dir_name = get_repo_dir_name(result_dir_name, repo_name)
    file_names: List[str] = []
    for root, dirs, files in os.walk(repo_dir_name, topdown=False):
        for name in files:
            full_name =  os.path.relpath(os.path.join(root, name), result_dir_name)
            file_names.append(full_name)
        for name in dirs:
            full_name =  os.path.relpath(os.path.join(root, name), result_dir_name)
            file_names.append(full_name)
    return _get_submissions(file_names, checkers, min_index, max_index)


def get_column_names(checkers: Mapping[str, Any], min_index: int, max_index: int) -> List[str]:
    seen: Mapping[str, bool] = {}
    column_names: List[str] = []
    for checker in checkers:
        for index in range(min_index, max_index+1):
            name = checker["name"].format(index=index)
            if name in seen:
                continue
            seen[name] = True
            column_names.append(name)
    return column_names


def get_file_created_at(file_path, repo_name, result_dir_name: str) -> str:
    if file_path == '':
        return ''
    rel_path =  os.path.relpath(file_path, repo_name)
    repo_path = os.path.join(result_dir_name, repo_name)
    command = "cd {repo_path} && git log --format=%aD '{rel_path}'".format(rel_path=rel_path, repo_path=repo_path)
    return ', '.join(subprocess.check_output(command, shell=True, text=True).split('\n')).strip()
    # TODO: git log --format=%aD '2_Version Control and Branch Management (Git)/Summary.md' | tail -1


def get_markdown_table(class_submission: Mapping[str, Mapping[str, List[str]]], checkers: Mapping[str, Any], min_index: int, max_index: int, result_dir_name: str) -> str:
    column_names = get_column_names(checkers, min_index, max_index)
    header_row = '|'.join(['{column_name}|Created at'.format(column_name=column_name) for column_name in column_names])
    separator_row = '|'.join(['---|---' for _ in column_names])
    body_rows: List[str] = []
    for student_name, student_task in class_submission.items():
        repo_name=camel_case(student_name)
        cells:List[List[str]] = []
        for column_index, column_name in enumerate(column_names):
            tasks = student_task[column_name]
            for row_index, task in enumerate(tasks):
                if row_index >= len(cells):
                    cells.append([''] * len(column_names))
                cells[row_index][column_index] = task
        for row_index, row in enumerate(cells):
            first_column = student_name if row_index == 0 else ''
            body_row = '|{first_column}|{task_row}'.format(
                first_column=first_column,
                task_row='|'.join([
                    '[{task_file_caption}]({task_file_link})|{created_at}'.format(
                        task_file_caption=task_file,
                        task_file_link=task_file.replace(' ', '%20'),
                        created_at=get_file_created_at(task_file, repo_name, result_dir_name)
                    ) for task_file in row
                ])
            )
            body_rows.append(body_row)
    markdown = '|Name|{header_row}\n|---|{separator_row}\n{body_rows}'.format(
        header_row=header_row,
        separator_row=separator_row,
        body_rows='\n'.join(body_rows)
    )
    return markdown


def main(config: Mapping[str, Any]):
    csv_file_name: str = config.get('csv_file_name', 'data.csv')
    result_dir_name: str = config.get('result_dir_name', 'data')
    new_line: str = config.get('new_line', '')
    delimiter: str = config.get('delimiter', ',')
    quote_char: str = config.get('quote_char', "'")
    min_index: int = config.get('min_index', 0)
    max_index: int = config.get('max_index', 0)
    checkers: List[Mapping[str, Any]] = config.get('checkers', [])
    with open(csv_file_name, newline=new_line) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter, quotechar=quote_char)
        class_submission: Mapping[str, Mapping[str, List[str]]] = {}
        for row in csv_reader:
            name, git_url = extract_row(row)
            if name == '' or git_url == '':
                continue
            repo_name=camel_case(name)
            clone_or_pull(git_url, repo_name, result_dir_name)
            student_submission = get_submissions(repo_name, result_dir_name, checkers, min_index, max_index)
            class_submission[name] = student_submission
        markdown_table = get_markdown_table(class_submission, checkers, min_index, max_index, result_dir_name)
        with open(os.path.join(result_dir_name, 'README.md'), 'w') as report_file:
            report_file.write('# Report\n')
            report_file.write(markdown_table)


if __name__ == '__main__':
    default_config_file_name:str = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')
    config_file_name: str = sys.argv[1] if len(sys.argv) > 1 else default_config_file_name
    with open(config_file_name) as config_file:
        config:Mapping[str, Any] = json.load(config_file)
        main(config)