import os
import json



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
