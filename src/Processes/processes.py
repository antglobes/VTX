import asyncio
import datetime
import shlex
import time

import xmltodict as xml
from Utils.fileHandling import get_sound_files, parse_files, get_translation_results, lang_to_iso, file_exists, \
    create_id
import subprocess
from pathlib import Path
from collections import defaultdict
# AsyncIOScheduler, MemoryJobStore, ProcessPoolExecutor interval


class JobManager:
    def __init__(self, config):
        self.config = config
        self.scheduler = JobScheduler(self.config)
        self.job = None

    @staticmethod
    def run_condition(job):
        if not job.is_job_complete() and not job.is_active() and job.is_details_full() and job.is_details_non_null():
            return True
        return False

    def load_deepl_settings(self, job):
        job.add('API_KEY', self.config.get_setting('DeepL', 'API_KEY'))

    def load_system_settings(self, job):
        job.add('UNPACKED', self.config.get_setting('System', 'UNPACKED'))
        job.add('SAVE_DIR', self.config.get_setting('System', 'SAVE_DIR'))
        job.add('XML_BASE', self.config.get_setting('System', 'XML_BASE'))

    def load_att_settings(self, job):
        job.add('MODEL', self.config.get_setting('ATT', 'MODEL'))
        job.add('LANG_TO', self.config.get_setting('ATT', 'LANG_TO'))
        job.add('OUT_FILE', self.config.get_setting('ATT', 'OUT_FILE'))

    def build_additional_details(self, job):
        self.load_deepl_settings(job)
        self.load_system_settings(job)
        self.load_att_settings(job)
        return job

    def fill_details(self, values, suffix):
        keys = self.job.details.keys()
        for i in range(len(keys)):
            if 'deepl_task' not in keys:
                self.job.add('deepl_task', *values[f'LISTBOX_TARG_LANG{suffix}'])

            if 'ATT_task' not in keys:
                self.job.add('ATT_task', 'transcribe')

            if 'files' not in keys:
                self.job.add('files', values[f'JOBS_MENU_LIST_DIRS_INPUT{suffix}'])

            if 'file_type' not in keys:
                self.job.add('file_type', 'folder')

    def create_new_job(self):
        self.job = Job()
        return self.build_additional_details(self.job)

    def remove_job(self):
        self.job = None

    def check_run_condition(self):
        if not self.run_condition(self.job):
            return False, 'Failed to create new job'
        return True, 'Creating a new job'

    def start_job(self):
        for k, v in self.job.details.items():
            print(f'{k}:{v}')
        print("\n")
        self.job.id = create_id()
        self.job.set_status(True)
        self.job = self.scheduler.run_tasks(self.job)
        for k, v in self.job.details.items():
            print(f'{k}:{v}')


    def display_active(self):
        return [f"Active Job: {j.id}" for j in self.scheduler.active_job]

    def display_log(self):
        pass


def star(finished: int, total: int) -> None:
    print(f"{finished} of {total} tasks are complete")


class JobScheduler:
    def __init__(self, config):
        self.config = config
        self.results = {}
        self.active_job = []
        self.job = None


    def cleanup(self):
        if not self.job.is_active() and self.job.is_job_complete():
            for i in range(len(self.job.details)):
                self.job.details[i] = None
            self.job = None

    def run_tasks(self, job):
        self.active_job.append(job)
        job = self.sound_files_task(job)
        job = self.att_task(job)
        job = self.xml_task(job)
        job.set_status(False)
        self.active_job.remove(job)
        return job

    def sound_files_task(self, job):
        sound_folder = f"{job.get_details('UNPACKED')}\\sounds"
        target_folder = parse_files(sound_folder, job.get_details('files'))
        sound_files = get_sound_files(sound_folder, target_folder)
        job.add('sound_files', sound_files)
        return job

    def att_task(self, job):
        # ATT details
        task = job.get_details('ATT_task')
        model = job.get_details('MODEL')
        lang = job.get_details('LANG_TO')
        out_fmt = job.get_details('OUT_FILE')
        out_file = job.get_details('SAVE_DIR')
        job.add('out_file', out_file)
        # Deepl details
        targ_lang = job.get_details('deepl_task')
        audtotext = f"{Path(self.config.root).__str__()}\\audiototext.py"
        print(Path(audtotext).exists())
        job.add('start_time', int(time.time()))

        for obj in job.get_details('sound_files'):
            for lst in obj.values():
                for file in lst:
                    clf = ['python', f'{audtotext}', f'{file}', '--task', f'{task}', '--model', f'{model}',
                           '--language', f'{lang}', '--output_formats', f'{out_fmt}', '--output_dir', f'{out_file}',
                           '--deepl_api_key', f'{job.get_details("API_KEY")}',  '--deepl_target_language', f'{targ_lang}',
                           '--deepl_coherence_preference', f'{False}', '--skip-install']

                    print(clf)
                    subprocess.run(clf)

        job.add('att_results', get_translation_results(out_file, job))

        return job

    def xml_task(self, job):
        paths = []
        save_dir = job.get_details('SAVE_DIR')
        lang = job.get_details('deepl_task')
        path_to_locale = f"\\configs\\text\\{lang_to_iso(self.config.langs, lang)}"
        xml_base = job.get_details('XML_BASE')

        for sf_obj in job.get_details('sound_files'):
            for ar_obj in job.get_details('att_results'):

                for sound_folder, sound_file in sf_obj.items():
                    for sound_file_name, translation in ar_obj.items():

                        if Path(sound_file).name == sound_file_name:
                            string_id = f'{xml_base}_{sound_folder}_{sound_file_name}'
                            xml_format = {
                                f'string id="{string_id}"': {
                                    "text": f"{translation}"
                                }
                            }
                            paths.append({f"{save_dir}{path_to_locale}\\st_as_{sound_folder}.xml": xml_format})

        result = defaultdict(list)
        for i in range(len(paths)):
            current = paths[i]
            for key, value in current.items():
                for j in range(len(value)):
                    result[key].append(value) if value not in result[key] else None

        for path, xml_json in result.items():
            with open(path, 'w') as xml_file:
                line_start = 0
                if file_exists(path):
                    i = 0
                    xml_file.seek(0)
                    lines = xml_file.readlines()
                    for line in lines:
                        if i > 0 and line == f'<?xml version="1.0" encoding="utf-8"?>':
                            xml_file.write(" ")

                        if i == 1:
                            xml_file.write("<string_table>")
                            line_start = xml_file.tell()

                        i += 1

                for xjson in xml_json:
                    xml_file.seek(line_start + 1)
                    xml_file.write("\n")
                    xml_file.write(f"\t{xml.unparse(input_dict=xjson, encoding='windows-1251', pretty=True)}")
                    line_start = xml_file.tell()

                xml_file.write("\n</string_table>")

        job.add('xml_task', result.keys())

        return job


class Job:
    def __init__(self):
        self.details = {}
        self.details_full = None
        self.complete = False
        self.active = False
        self.id = None

    def is_job_complete(self):
        return self.complete

    def is_details_full(self):
        if len(self.details) > 7:
            self.details_full = True
        else:
            self.details_full = False
        return self.details_full

    def is_details_non_null(self):
        for value in self.details.values():
            if value is None:
                return False
        return True

    def is_active(self):
        return self.active

    def set_id(self, val):
        self.id = val

    def set_status(self, status):
        self.active = status

    def get_id(self):
        return self.id

    def get_details(self, key):
        return self.details[key]

    def add(self, key, value):
        self.details[key] = value
