import logging
from pathlib import Path
from configupdater import ConfigUpdater
from CustomTypes.types import Section, PathType, IconType
import Utils.fileHandling as utils
import PySimpleGUI as sg


#@sp.snoop()
class Config:
    def __init__(self, logger):
        self.logger = logger
        root = Path().resolve().parent.as_posix()
        self.root = root
        self.config_path = root + '/config.ini'
        self.data_folder = root + '/data'
        self.icon_folder = self.data_folder + '/icons'
        self.files_folder = self.data_folder + '/files'

        self.updater = ConfigUpdater()
        self.deepl = {}
        self.att = {}
        self.sys_vars = {}
        self.langs = {}
        self.timezones = {}



        self.load()
        self.load_langs()

    def load(self):
        self.read()
        for section in self.updater.sections():
            match section:
                case 'DeepL':
                    self.deepl = self.get_section(section)
                case 'ATT':
                    self.att = self.get_section(section)
                case 'System':
                    self.sys_vars = self.get_section(section)


    def write(self):
        with open(self.config_path, 'w') as config_file:
            self.updater.write(config_file)


    def load_langs(self):
        self.langs = utils.load_json_file(self.files_folder + '/ISO_639-1_langs.json')

    def load_timezones(self):
        self.timezones = utils.load_json_file(self.files_folder + '/timezones.json')

    def read(self):
        self.updater.read(self.config_path)

    def get_section(self, section: str) -> dict[str, str | None]:
        self.read()
        return self.updater.get_section(section).to_dict()

    @staticmethod
    def get_icons(path: str):
        contents = []
        paths = utils.get_folder_contents(path)
        for path in paths:
            contents.append({Path(path).name: path})

        return contents

    def get_icon(self, name: str) -> IconType:
        icons = self.get_icons(self.icon_folder)
        if not name:
            return icons
        for obj in icons:
            for k, v in obj.items():
                if k == f"{name}.png":
                    return v
        return False

    def app_icon(self):
        return self.get_icon('app')

    def get_default_lang(self):
        return self.att['lang_to'].capitalize()

    def get_langs(self):
        langs = []
        for obj in self.langs:
            for k in obj.keys():
                langs.append(obj[k]) if k == 'name' else None
        return langs

    def get_default_model(self):
        return self.att['model']

    @staticmethod
    def get_models():
        return ['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2']

    def get_default_task_type(self):
        return self.att['task']

    @staticmethod
    def get_task_types():
        return ['Transcribe', 'Translate']

    def get_default_out_fmt(self):
        return self.att['out_file']

    @staticmethod
    def get_output_format():
        return ['txt', 'srt', 'vtt', 'json', 'tsv']


    def get_deep_lang_from(self):
        return self.deepl['lang_from'].capitalize()

    def get_deep_lang_to(self):
        return self.deepl['lang_to'].capitalize()

    def get_timezone(self):
        return self.timezones[self.get_setting('System', 'Zone').capitalize()]

    def change_setting(self, section, option, val, typ=None):
        if isinstance(val, list):
            val = str(val)
            val = val[2:len(val)-2]
        match section:
            case 'DeepL':
                if option == 'API_KEY':
                    if typ == 'file':
                        self.updater[section][option].value = utils.file_to_api_key(val)
                    elif typ == 'env':
                        self.updater[section][option].value = val
                elif option == 'LANG_FROM' or 'LANG_TO':
                    self.updater[section][option].value = val
            case 'ATT' | 'System':
                self.updater[section][option].value = val


        self.write()
        self.load()

    def get_setting(self, section, option):
        option = option.lower()
        match section:
            case 'DeepL':
                return self.deepl[option]
            case 'ATT':
                return self.att[option]
            case 'System':
                return self.sys_vars[option]
