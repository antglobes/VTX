import sys
import traceback

import Utils.log
from GUI.views import MainMenu as mm
from GUI.views import JobsMenu as jm
from GUI.views import SettingsMenu as sm
from Processes.processes import Job
from Utils.log import LoggingUtilities as log
from Config.configManager import Config as cfg

import PySimpleGUI as sg


# @ps.snoop()
class Main:
    def __init__(self):
        self.theme = sg.theme('DarkBrown7')  # lightbrown8
        self.logger = log()
        self.config = cfg(self.logger)
        self.jobs = jm(self.config)
        self.settings = sm(self.config)
        self.main_menu = mm(self.config, self.logger, self.jobs, self.settings)
        self.window_num = 0
        self.job = None

    @staticmethod
    def hide_window(window: sg.Window, hide: bool):
        if hide:
            window.hide()
        else:
            window.un_hide()

    def manage_event(self, window, event, suffix, values):
        response = None
        if event == f'MAIN_MENU_EXIT_BUTTON{suffix}':
            return 'Exit'
        elif event == f'MAIN_MENU_JOBS_BUTTON{suffix}':
            response = self.run_jobs_menu(suffix)
        elif event == f'MAIN_MENU_SETTINGS_BUTTON{suffix}':
            response = self.run_settings_menu(suffix)

        return response

    def run_jobs_menu(self, suffix):
        window = self.jobs.create_new_window(suffix)
        self.job = Job(self.settings)
        response = None
        running = True
        while running:
            event, values = window.read()
            response = self.manage_jobs_event(window, event, suffix, values)
            match response:
                case None:
                    continue
                case 'Back' | 'Exit':
                    if not self.job.is_active():
                        self.job = None
                    running = False

        return response

    def manage_jobs_event(self, window, event, suffix, values):
        # Titlebar
        if event == f'JOBS_MENU_BACK_BUTTON{suffix}':
            window.close()
            return 'Back'
        elif event == f'JOBS_MENU_EXIT_BUTTON{suffix}':
            window.close()
            return 'Exit'

        # File Types
        elif event == f'RADIO_FILE_TYPE_SINGLE{suffix}':
            self.job.add('file_type', 'single')
            window[f'JOBS_MENU_LIST_FILES_TEXT{suffix}'].update(visible=True)
            window[f'JOBS_MENU_LIST_FILES_INPUT{suffix}'].update(visible=True)
            window[f'JOBS_MENU_FILE_SELECT_BUTTON{suffix}'].update(visible=True)
            window[f'JOBS_MENU_LIST_DIRS_TEXT{suffix}'].update(visible=False)
            window[f'JOBS_MENU_LIST_DIRS_INPUT{suffix}'].update(visible=False)
            window[f'JOBS_MENU_LIST_DIRS_SELECT_BUTTON{suffix}'].update(visible=False)
            window.refresh()

        elif event == f'RADIO_FILE_TYPE_FOLDER{suffix}':
            self.job.add('file_type', 'folder')
            window[f'JOBS_MENU_LIST_DIRS_TEXT{suffix}'].update(visible=True)
            window[f'JOBS_MENU_LIST_DIRS_INPUT{suffix}'].update(visible=True)
            window[f'JOBS_MENU_LIST_DIRS_SELECT_BUTTON{suffix}'].update(visible=True)
            window[f'JOBS_MENU_LIST_FILES_TEXT{suffix}'].update(visible=False)
            window[f'JOBS_MENU_LIST_FILES_INPUT{suffix}'].update(visible=False)
            window[f'JOBS_MENU_FILE_SELECT_BUTTON{suffix}'].update(visible=False)
            window.refresh()

        # Sound Filenames
        elif event == f'JOBS_MENU_FILE_SELECT_BUTTON{suffix}':
            file = self.jobs.select_file()
            self.job.add('files', [file])
            window[f'JOBS_MENU_LIST_FILES_INPUT{suffix}'].update(file)

        # Sound Directories
        elif event == f'JOBS_MENU_LIST_DIRS_SELECT_BUTTON{suffix}':
            folder = self.jobs.select_folder()
            self.job.add('files', [folder])
            window[f'JOBS_MENU_LIST_DIRS_INPUT{suffix}'].update(folder)


        # ATT Task Type
        elif event == f'RADIO_TASK_TYPE_TRANSCRIBE{suffix}':
            self.job.add('ATT_task', 'transcribe')
        elif event == f'RADIO_TASK_TYPE_TRANSLATE{suffix}':
            self.job.add('ATT_task', 'translate')

        # DeepL Translation Lang
        elif event == f'LISTBOX_TARG_LANG{suffix}':
            self.job.add('deepl_task', values[f'LISTBOX_TARG_LANG{suffix}'])

        # Job Buttons
        elif event == f'JOBS_MENU_NEW_JOB_BUTTON{suffix}':
            self.job_manager.add_to_broker()

        elif event == f'JOBS_MENU_VIEW_JOBS_BUTTON{suffix}':
            self.job_manager.display_active()

        elif event == f'JOBS_MENU_VIEW_LOG_BUTTON{suffix}':
            self.job_manager.display_log()



    def run_settings_menu(self, suffix):
        window = self.settings.create_new_window(suffix)
        response = None
        running = True
        while running:
            event, values = window.read()
            response = self.manage_settings_event(window, event, suffix, values)
            match response:
                case None:
                    continue
                case 'Back':
                    running = False
                case 'Exit':
                    running = False

        return response

    def manage_settings_event(self, window, event, suffix, values):
        # Titlebar
        if event == f'SETTINGS_MENU_BACK_BUTTON{suffix}':
            window.close()
            return 'Back'


        elif event == f'SETTINGS_MENU_EXIT_BUTTON{suffix}':
            window.close()
            return 'Exit'

        # DeepL Tab
        elif event == f'SETTINGS_LOAD_KEY_FILE_BUTTON{suffix}':
            file = self.settings.select_file()
            self.config.change_setting('DeepL', 'API_KEY', file if file else self.config.get_setting('DeepL', 'API_KEY')
                                       , 'file')

        elif event == f'SETTINGS_LOAD_KEY_ENV_BUTTON{suffix}':
            self.config.change_setting('DeepL', 'API_KEY', self.settings.load_env('VTX_DEEPL'), 'env')

        elif event == f'LISTBOX_DEEPL_LANG_FROM{suffix}':
            self.config.change_setting('DeepL', 'LANG_FROM', values[f'LISTBOX_DEEPL_LANG_FROM{suffix}'])
            window[f'LISTBOX_DEEPL_LANG_FROM{suffix}'].update(
                scroll_to_index=self.settings.langs.index(self.config.get_setting('DeepL', 'LANG_FROM')))

        elif event == f'LISTBOX_DEEPL_LANG_TO{suffix}':
            self.config.change_setting('DeepL', 'LANG_TO', values[f'LISTBOX_DEEPL_LANG_TO{suffix}'])
            window[f'LISTBOX_DEEPL_LANG_TO{suffix}'].update(
                scroll_to_index=self.settings.langs.index(self.config.get_setting('DeepL', 'LANG_TO')))

        # ATT Tab
        elif event == f'LISTBOX_ATT_LANG_TO{suffix}':
            self.config.change_setting('ATT', 'LANG_TO', values[f'LISTBOX_ATT_LANG_TO{suffix}'])
            window[f'LISTBOX_ATT_LANG_TO{suffix}'].update(
                scroll_to_index=self.settings.langs.index(self.config.get_setting('ATT', 'LANG_TO')))

        elif event == f'LISTBOX_ATT_MODELS{suffix}':
            self.config.change_setting('ATT', 'MODEL', values[f'LISTBOX_ATT_MODELS{suffix}'])
            window[f'LISTBOX_ATT_MODELS{suffix}'].update(
                scroll_to_index=self.settings.models.index(self.config.get_setting('ATT', 'MODEL')))

        elif event == f'LISTBOX_ATT_TASK_TYPE{suffix}':
            self.config.change_setting('ATT', 'TASK', values[f'LISTBOX_ATT_TASK_TYPE{suffix}'])
            window[f'LISTBOX_ATT_TASK_TYPE{suffix}'].update(
                scroll_to_index=self.settings.task_types.index(self.config.get_setting('ATT', 'TASK')))

        elif event == f'LISTBOX_ATT_OUT_FMT{suffix}':
            self.config.change_setting('ATT', 'OUT_FILE', values[f'LISTBOX_ATT_OUT_FMT{suffix}'])
            window[f'LISTBOX_ATT_OUT_FMT{suffix}'].update(
                scroll_to_index=self.settings.out_fmt.index(self.config.get_setting('ATT', 'OUT_FILE')))

        #System Tab
        elif event == f'SETTINGS_GAMEDATA_BUTTON{suffix}':
            folder = self.settings.select_folder()
            self.config.change_setting('System', 'GAMEDATA', folder)

        elif event == f'SETTINGS_SAVE_FOLDER_BUTTON{suffix}':
            folder = self.settings.select_folder()
            self.config.change_setting('System', 'SAVE_DIR', folder)


    def run(self):
        reload_window = False

        window = self.main_menu.create_new_window(suffix=f"_{self.window_num}")
        main_loop = True
        while main_loop:
            try:
                if reload_window:
                    self.window_num += 1
                    window = self.main_menu.create_new_window(suffix=f'_{self.window_num}')
                    reload_window = False

                suffix = f'_{self.window_num}'

                if not main_loop:
                    break

                run_event_loop = True
                while run_event_loop:
                    event, values = window.read()

                    if event in self.main_menu.element_keys(suffix):
                        window.close()
                        response = self.manage_event(window, event, suffix, values)
                        if response == 'Exit':
                            main_loop = False
                        elif response == 'Back':
                            reload_window = True
                        run_event_loop = False


            except Exception as e:
                sg.popup_error(e.with_traceback(traceback.print_exc(file=sys.stdout)),
                               auto_close=True, auto_close_duration=0.01)
                continue


if __name__ == "__main__":
    Main().run()
