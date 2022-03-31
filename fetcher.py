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


def get_task_names(checkers: Mapping[str, Any], min_index: int, max_index: int) -> List[str]:
    seen: Mapping[str, bool] = {}
    task_names: List[str] = []
    for index in range(min_index, max_index+1):
        for checker in checkers:
            task_name = checker["name"].format(index=index)
            if task_name in seen:
                continue
            seen[task_name] = True
            task_names.append(task_name)
    return task_names


def get_file_created_at(file_path, repo_name, result_dir_name: str) -> str:
    if file_path == '':
        return ''
    rel_path =  os.path.relpath(file_path, repo_name)
    repo_path = os.path.join(result_dir_name, repo_name)
    command = "cd {repo_path} && git log --format=%aD '{rel_path}'".format(rel_path=rel_path, repo_path=repo_path)
    return ', '.join(subprocess.check_output(command, shell=True, text=True).split('\n')).strip()


def get_markdown_report(class_submission: Mapping[str, Mapping[str, List[str]]], checkers: Mapping[str, Any], min_index: int, max_index: int, result_dir_name: str) -> str:
    lines: List[str] = ['# Report']
    task_names = get_task_names(checkers, min_index, max_index)
    for task_name in task_names:
        lines.append('## {task_name}'.format(task_name=task_name))
        for student_name, student_submissions in class_submission.items():
            repo_name = camel_case(student_name)
            lines.append('* {student_name}'.format(student_name=student_name))
            submission_items = student_submissions[task_name]
            for submission_item in submission_items:
                lines.append('  - [{submission_item}]({url}), Created at: {created_at}'.format(
                    submission_item=submission_item, 
                    url=submission_item.replace(' ', '%20'),
                    created_at=get_file_created_at(submission_item, repo_name, result_dir_name)
                ))
    return '\n'.join(lines)


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
        markdown = get_markdown_report(class_submission, checkers, min_index, max_index, result_dir_name)
        with open(os.path.join(result_dir_name, 'README.md'), 'w') as report_file:
            report_file.write(markdown)


if __name__ == '__main__':
    default_config_file_name:str = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')
    config_file_name: str = sys.argv[1] if len(sys.argv) > 1 else default_config_file_name
    with open(config_file_name) as config_file:
        config:Mapping[str, Any] = json.load(config_file)
        main(config)