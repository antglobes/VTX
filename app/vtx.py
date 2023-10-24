import sys
import traceback

import Utils.log
from GUI.views import MainMenu as mm
from GUI.views import JobsMenu as jm
from GUI.views import SettingsMenu as sm
from Utils.log import LoggingUtilities as log
from Config.configManager import Config as cfg

import PySimpleGUI as sg


#@ps.snoop()
class Main:
    def __init__(self):
        self.theme = sg.theme('DarkBrown7') #lightbrown8
        self.logger = log()
        self.config = cfg(self.logger)
        self.jobs = jm(self.config)
        self.settings = sm(self.config)
        self.main_menu = mm(self.config, self.logger, self.jobs, self.settings)
        self.window_num = 0

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
        response = None
        running = True
        while running:
            event, values = window.read()
            response = self.manage_jobs_event(window, event, suffix, values)
            match response:
                case None:
                    continue
                case 'Back':
                    running = False
                case 'Exit':
                    running = False

        return response

    def manage_jobs_event(self, window, event, suffix, values):
        if event == f'JOBS_MENU_BACK_BUTTON{suffix}':
            window.close()
            return 'Back'
        elif event == f'JOBS_MENU_EXIT_BUTTON{suffix}':
            window.close()
            return 'Exit'

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
        if event == f'SETTINGS_MENU_BACK_BUTTON{suffix}':
            window.close()
            return 'Back'
        elif event == f'SETTINGS_MENU_EXIT_BUTTON{suffix}':
            window.close()
            return 'Exit'
        elif event == f'SETTINGS_LOAD_KEY_FILE_BUTTON{suffix}':
            file = self.settings.select_file()
            self.config.change_setting('DeepL', 'API_KEY', file if file else self.config.get_setting('DeepL', 'API_KEY'))

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
