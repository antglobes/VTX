import datetime
import os
import json
from pathlib import Path


def get_folder_contents(folder):
    contents = []
    for dirname, dirpath, filenames in os.walk(folder):
        for file in filenames:
            contents.append(f"{dirname}/{file}")

    return contents


def get_directories_files(folder):
    directories = []
    files = []
    for dirname, dirpath, filename in os.walk(folder):
        directories.extend(dirpath)
        files.extend(filename)
    return


def load_json_file(path):
    jsonObject = {}
    with open(path, "r", encoding='utf-8') as file:
        jsonObject = json.load(file)
    return jsonObject


def file_to_api_key(path):
    print(path)
    with open(path, 'r') as file:
        for line in file.readlines():
            print(line)
            if line.startswith('API_KEY'):
                return line[line.find('=') + 1:len(line)]


def get_sound_files(gamedata_folder, target_folder, sound_files=None):
    sound_files = sound_files if sound_files else []
    for root, dirs, files in os.walk(Path(gamedata_folder)):
        for folder in target_folder:
            if root.endswith(folder):
                sound_files.extend({folder: files})
                target_folder.remove(folder)
                if len(target_folder) > 1 and len(target_folder) != 0:
                    get_sound_files(gamedata_folder, target_folder[1:], sound_files)

    return sound_files


def parse_files(files):
    return files


def lang_to_iso(lang_list, lang):
    for obj in lang_list:
        for k, v in obj.items():
            if v.lower() == lang.lower():
                return k.lower()
    return 'eng'


def get_translation_results(save_dir, job):
    start_time = job.get_details('start_time')

    results = []
    for root, dirs, files in os.walk(Path(save_dir)):
        for file in files:
            path = root + file
            if start_time < os.path.getmtime(path):
                with open(path, 'r', encoding='utf-8') as trans_file:
                    results.append({Path(file).name: trans_file.readlines()})

    return results


def file_exists(path):
    return Path(path).exists()


def valid_path_format(path):
    return Path(path).is_file() or Path(path).is_dir()
