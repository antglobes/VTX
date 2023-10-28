import asyncio
import shlex
import time
import xmltodict as xml
from scheduler.Scheduler import Scheduler
from Utils.fileHandling import get_sound_files, parse_files, get_translation_results, lang_to_iso, file_exists
import subprocess
from pathlib import Path
from collections import defaultdict
from multiprocess import queues, process


def job_complete_num(finished: int, total: int) -> None:
    print(f"{finished} of {total} tasks are complete")


class JobManager:
    def __init__(self, config, settings):
        self.config = config
        self.settings = settings
        self.scheduler = JobScheduler(self.config)
        self.job = None

    @staticmethod
    def run_condition(job):
        if not (job.is_job_complete() and job.is_active()) and job.is_details_full() and job.is_details_non_null():
            return True
        return False

    def load_deepl_settings(self, job):
        job.add('API_KEY', self.settings.get_setting('API_KEY'))

    def load_system_settings(self, job):
        job.add('GAMEDATA', self.settings.get_setting('GAMEDATA'))
        job.add('SAVE_DIR', self.settings.get_setting('SAVE_DIR'))
        job.add('XML_BASE', self.settings.get_setting('XML_BASE'))

    def build_additional_details(self, job):
        self.load_deepl_settings(job)
        self.load_system_settings(job)
        return job

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
        self.job.set_status(True)
        self.scheduler.schedule_job(self.job)
        self.scheduler.start_job()
        self.scheduler.run_scheduler()

    def display_active(self):
        pass

    def display_log(self):
        pass


class JobScheduler:
    def __init__(self, config):
        self.scheduler = Scheduler(job_complete_num)
        self.config = config
        self.results = {}
        self.job = None

    def run_tasks(self, job):
        job = self.sound_files_task(job)
        job = self.att_task(job)
        job, results = self.xml_task(job)
        job.set_status(False)
        return results

    def schedule_job(self, job):
        self.scheduler.add(target=self.run_tasks,
                           args=job,
                           subtasks=10,
                           process_type=process.BaseProcess,
                           queue_type=queues.Queue)
        self.job = job

    async def start_job(self):
        self.results[self.job.id] = await self.scheduler.run()
        self.cleanup()

    def run_scheduler(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.start_job())

    def cancel_jobs(self):
        self.scheduler.terminate()

    def cleanup(self):
        if not self.job.is_active() and self.job.is_job_complete():
            for i in range(len(self.job.details)):
                self.job.details[i] = None
            self.job = None

    def sound_files_task(self, job):
        gamedata_folder = self.config.get_setting('System', 'GAMEDATA')
        target_folder = parse_files(job.get_details('files'))
        sound_files = get_sound_files(gamedata_folder, target_folder)
        job.add('sound_files', sound_files)
        return job

    def att_task(self, job):
        # ATT details
        task = job.get_details('ATT_task')
        model = self.config.get_setting('ATT', 'MODEL')
        lang = self.config.get_setting('ATT', 'LANG_TO')
        out_fmt = self.config.get_setting('ATT', 'OUT_FILE')
        out_file = self.config.get_setting('System', 'SAVE_DIR')
        job.add('out_file', out_file)
        # Deepl details
        targ_lang = job.get_details('deepl_task')

        start_time = int(time.time())
        job.add('start time', start_time)

        for obj in job.get_details('sound_files'):
            for file in obj.values():
                subprocess.run(shlex.split(
                    f"""python audiototext.py {file} 
                    --task {task} --model {model}  --language {lang} 
                    --output_formats {out_fmt} --output_dir {out_file} --deepl_api_key {job.get_details('API_KEY')}
                    --deepl_target_language {targ_lang} --deepl_coherence_preference {False}
                     """
                ))

        job.add('att_results', get_translation_results(out_file, job))

        return job

    def xml_task(self, job):
        paths = []
        gamedata = self.config.get_setting('System', 'GAMEDATA')
        lang_list = self.config.langs
        lang = self.config.get_settings('DeepL', 'LANG_TO')
        path_to_locale = f"\\configs\\text\\{lang_to_iso(lang_list, lang)}"
        xml_base = self.config.get_setting('System', 'XML_BASE')

        for sf_obj in job.get_details('sound_files'):
            for ar_obj in job.get_details('att_results'):

                for sound_folder, sound_file in sf_obj.items():
                    for sound_file_name, translation in ar_obj.items():

                        if Path(sound_file).name == sound_file_name:
                            string_id = f'{xml_base}{sound_folder}{sound_file_name}'
                            xml_format = {
                                f'string id="{string_id}"': {
                                    "text": f"{translation}"
                                }
                            }
                            paths.append({f"{gamedata}{path_to_locale}\\st_as_{sound_folder}.xml": xml_format})

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

        return job, result.keys()


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
        if len(self.details) == 8:
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
