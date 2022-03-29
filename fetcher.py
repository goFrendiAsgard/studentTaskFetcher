from typing import List, Mapping, Tuple

import csv
import json
import os
import re
import sys


def camel_case(s:str)->str:
  s = re.sub(r"(_|-)+", " ", s).title().replace(" ", "")
  return ''.join([s[0].lower(), s[1:]])


def extract_row(row:List[str]) -> Tuple[str, str]:
    raw_name = row[0] if len(row) > 0 else ''
    git_url = row[1] if len(row) > 1 else ''
    name = raw_name.title()
    return (name, git_url)


def clone_or_pull(git_url, repo_name, result_dir_name: str):
    repo_dir_name = os.path.join(result_dir_name, repo_name)
    if os.path.isdir(repo_dir_name):
        exit_code = os.system('cd {repo_dir_name} && git pull origin main'.format(repo_dir_name=repo_dir_name))
        if exit_code != 0:
            exit_code = os.system('cd {repo_dir_name} && git pull origin master'.format(repo_dir_name=repo_dir_name))
            if exit_code != 1:
                print('[ERROR] Failed to pull {repo_name}'.format(repo_name=repo_name))
        return
    os.makedirs(result_dir_name, exist_ok=True)  
    exit_code = os.system('cd {result_dir_name} && git clone {git_url} {repo_name}'.format(result_dir_name=result_dir_name, git_url=git_url, repo_name=repo_name))
    if exit_code != 0:
        print('[ERROR] Failed to clone {git_url} to {repo_dir_name}'.format(git_url=git_url, repo_dir_name=repo_dir_name))


def main(config: Mapping[str, str]):
    csv_file_name = config.get('csv_file_name', 'data.csv')
    result_dir_name = config.get('result_dir_name', 'data')
    new_line = config.get('new_line', '')
    delimiter = config.get('delimiter', ',')
    quote_char = config.get('quote_char', "'")
    with open(csv_file_name, newline=new_line) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=delimiter, quotechar=quote_char)
        for row in csv_reader:
            name, git_url = extract_row(row)
            if name == '' or git_url == '':
                continue
            repo_name=camel_case(name)
            clone_or_pull(git_url, repo_name, result_dir_name)


if __name__ == '__main__':
    default_config_file_name:str = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'config.json')
    config_file_name:str = sys.argv[1] if len(sys.argv) > 1 else default_config_file_name
    with open(config_file_name) as config_file:
        config:Mapping[str, str] = json.load(config_file)
        main(config)