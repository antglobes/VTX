import PySimpleGUI as sg
from CustomTypes.types import WindowLayout


class MainMenu:
    def __init__(self, config, logger, jobs, settings):
        self.config = config
        self.logger = logger
        self.app_icon = self.config.get_icon('app_icon')
        self.info_icon = self.config.get_icon('info_icon')
        self.jobs = jobs
        self.settings = settings

    @staticmethod
    def get_title():
        return 'VTX'

    def create_new_window(self, suffix: str, new_theme=None, keep_on_top: bool = None) -> sg.Window:
        sg.theme(new_theme)
        layout = [
            [sg.Image(filename=self.app_icon, background_color=sg.theme_background_color(), expand_x=True)],
            [sg.HSeparator()],
            [sg.Button(tooltip='Jobs', button_color=sg.theme_button_color(),
                       button_text='JOBS', size=(30, 2), key=f'MAIN_MENU_JOBS_BUTTON{suffix}')],
            [sg.Button(tooltip='Settings', button_color=sg.theme_button_color(),
                       button_text='SETTINGS', size=(30, 2), key=f'MAIN_MENU_SETTINGS_BUTTON{suffix}')],
            [sg.Button(tooltip='Exit', button_color=sg.theme_button_color(),
                       button_text='EXIT', size=(60, 2), key=f'MAIN_MENU_EXIT_BUTTON{suffix}')],
            [sg.HSeparator()],
            [sg.Image(filename=self.info_icon, background_color=sg.theme_background_color(), expand_x=True)]

        ]

        return sg.Window(title=f'{self.get_title()}{suffix}', layout=layout, size=(200, 300), no_titlebar=True,
                         resizable=True, grab_anywhere=True, keep_on_top=(keep_on_top if keep_on_top else True),
                         modal=True, finalize=True, use_default_focus=False)

    @staticmethod
    def element_keys(suffix):
        return [f'MAIN_MENU_JOBS_BUTTON{suffix}', f'MAIN_MENU_SETTINGS_BUTTON{suffix}',
                f'MAIN_MENU_EXIT_BUTTON{suffix}']

    @staticmethod
    def close_program(window: sg.Window):
        window.close()
        del [window]


class JobsMenu:
    def __init__(self, config):
        self.config = config
        self.default_lang = self.config.get_default_lang()
        self.langs = self.config.get_langs()

    @staticmethod
    def get_title():
        return 'VTX Jobs'

    def create_new_window(self, suffix, new_theme=None, keep_on_top=None):
        sg.theme(new_theme)
        layout = [
            [sg.Text('JOBS', expand_x=True),
             sg.Button(tooltip='Back', button_color=sg.theme_button_color(), key=f'JOBS_MENU_BACK_BUTTON{suffix}',
                       button_text='Back'),
             sg.Button(tooltip='Exit', button_color=sg.theme_button_color(), key=f'JOBS_MENU_EXIT_BUTTON{suffix}',
                       button_text='Exit')],
            [sg.Text('Choose file type:'), sg.Radio('Single', 'file_type', key=f'RADIO_FILE_TYPE_SINGLE{suffix}'),
             sg.Radio('Multiple', 'file_type', key=f'RADIO_FILE_TYPE_MULTIPLE{suffix}'),
             sg.Radio('Folder', 'file_type', key=f'RADIO_FILE_TYPE_FOLDER{suffix}')],
            [sg.Text('List file(s):', tooltip='e.g. bar_hunter_1.ogg, bar_hunter_2.ogg, ... etc'),
             sg.Input(key=f'JOBS_MENU_LIST_FILES_INPUT{suffix}', expand_x=True),
             sg.Button(button_text='Select', button_color=sg.theme_button_color(),
                       key=f'JOBS_MENU_FILE_SELECT_BUTTON{suffix}')],
            [sg.Text('List directories(s):', tooltip='e.g. characters_phrases, dialogs'),
             sg.Input(key=f'JOBS_MENU_LIST_DIRS_INPUT{suffix}'),
             sg.Button(button_text='Select', button_color=sg.theme_button_color(),
                       key=f'JOBS_MENU_DIRS_SELECT_BUTTON{suffix}', expand_x=True)],
            [sg.Text('Select Task Type:'),
             sg.Radio('Transcribe', 'task_type', key=f'RADIO_TASK_TYPE_TRANSCRIBE{suffix}'),
             sg.Radio('Translate', 'task_type', key=f'RADIO_TASK_TYPE_TRANSLATE{suffix}')],
            [sg.Text('Select Target Language:'),
             sg.Listbox(self.langs, default_values=self.default_lang, size=(21, 2), expand_x=True,
                        select_mode=sg.SELECT_MODE_SINGLE, key=f'LISTBOX_TARG_LANG{suffix}')],
            [sg.HSeparator()],
            [sg.Button('Create New Job', button_color=sg.theme_button_color(),
                       expand_x=True, key=f'JOBS_MENU_NEW_JOB_BUTTON{suffix}'),
             sg.Button('View Jobs', button_color=sg.theme_button_color(),
                       expand_x=True, key=f'JOBS_MENU_VIEW_JOBS_BUTTON{suffix}'),
             sg.Button('View Log', button_color=sg.theme_button_color(),
                       expand_x=True, key=f'JOBS_MENU_VIEW_LOG_BUTTON{suffix}')]
        ]
        return sg.Window(title=f'{self.get_title()}{suffix}',
                         layout=layout,
                         size=(650, 300),
                         no_titlebar=True,
                         grab_anywhere=True,
                         keep_on_top=(True if not keep_on_top else keep_on_top),
                         modal=True)

    @staticmethod
    def element_keys(suffix):
        return [f'JOBS_MENU_BACK_BUTTON{suffix}', f'RADIO_FILE_TYPE_SINGLE{suffix}',
                f'RADIO_FILE_TYPE_MULTIPLE{suffix}', f'RADIO_FILE_TYPE_MULTIPLE{suffix}',
                f'RADIO_FILE_TYPE_FOLDER{suffix}', f'JOBS_MENU_LIST_FILES_INPUT{suffix}',
                f'JOBS_MENU_LIST_DIRS_INPUT{suffix}', f'RADIO_TASK_TYPE_TRANSCRIBE{suffix}',
                f'RADIO_TASK_TYPE_TRANSLATE{suffix}', f'LISTBOX_TARG_LANG{suffix}',
                f'JOBS_MENU_NEW_JOB_BUTTON{suffix}', f'JOBS_MENU_VIEW_JOBS_BUTTON{suffix}',
                f'JOBS_MENU_VIEW_LOG_BUTTON{suffix}', f'JOBS_MENU_EXIT_BUTTON{suffix}']


class SettingsMenu:
    def __init__(self, config):
        self.config = config
        self.default_lang = self.config.get_default_lang()
        self.langs = self.config.get_langs()
        self.default_model = self.config.get_default_model()
        self.models = self.config.get_models()
        self.default_model_size = self.config.get_default_model_size()
        self.model_sizes = self.config.get_model_sizes()
        self.default_task_type = self.config.get_default_task_type()
        self.task_types = self.config.get_task_types()
        self.default_out_fmt = self.config.get_default_out_fmt()
        self.out_fmt = self.config.get_output_format()
        self.deepl_lang_from = self.config.get_deep_lang_from()
        self.deepl_lang_to = self.config.get_deep_lang_to()

    @staticmethod
    def get_title():
        return 'VTX Settings'

    def create_new_window(self, suffix, new_theme=None, keep_on_top=None):
        sg.theme(new_theme)
        api_tab = sg.Tab('DeepL', layout=[
            [sg.Button('Load from file', expand_x=True, key=f'SETTINGS_LOAD_KEY_FILE_BUTTON{suffix}'),
             sg.Button('Load from Env', expand_x=True, key=f'SETTINGS_LOAD_KEY_ENV_BUTTON{suffix}')],
            [sg.Text('Language from:'), sg.Listbox(self.langs, default_values=self.deepl_lang_from, size=(21, 2),
                                                   select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                                   key=f'LISTBOX_DEEPL_LANG_FROM{suffix}')],
            [sg.Text('Language to:'), sg.Listbox(self.langs, default_values=self.deepl_lang_to, size=(21, 2),
                                                 select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                                 key=f'LISTBOX_DEEPL_LANG_TO{suffix}')]
        ], key=f"SETTINGS_MENU_DEEPL_TAB{suffix}")

        config_tab = sg.Tab('Buzz', layout=[
            [sg.Text('Language to:'), sg.Listbox(self.langs, default_values=self.default_lang, size=(21, 2),
                                                 select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                                 key=f'LISTBOX_BUZZ_LANG_TO{suffix}')],
            [sg.Text('Model:'), sg.Listbox(self.models, default_values=self.default_model, size=(21, 2), expand_x=True,
                                           select_mode=sg.SELECT_MODE_SINGLE, key=f'LISTBOX_BUZZ_MODELS{suffix}')],
            [sg.Text('Model Size:'), sg.Listbox(self.model_sizes, default_values=self.default_model_size, size=(21, 2),
                                                select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                                key=f'LISTBOX_BUZZ_MODEL_SIZE{suffix}')],
            [sg.Text('Task Type:'), sg.Listbox(self.task_types, default_values=self.default_task_type, size=(21, 2),
                                               select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                               key=f'LISTBOX_BUZZ_TASK_TYPE{suffix}')],
            [sg.Text('Output Format:'), sg.Listbox(self.out_fmt, default_values=self.default_out_fmt, size=(21, 3),
                                                   select_mode=sg.SELECT_MODE_SINGLE, expand_x=True,
                                                   key=f'LISTBOX_BUZZ_OUT_FMT{suffix}')]
        ], key=f"SETTINGS_MENU_BUZZ_TAB{suffix}")

        system_tab = sg.Tab('System', layout=[
            [sg.Text('Gamedata Folder:'),
             sg.Button('Select', key=f'LISTBOX_SYSTEM_GAMEDATA{suffix}', expand_x=True)],
            [sg.Text('Save Folder:'),
             sg.Button('Select', key=f'LISTBOX_SYSTEM_SAVE_FOLDER{suffix}', expand_x=True)],
        ], key=f"SETTINGS_MENU_SYSTEM_TAB{suffix}")

        help_tab = sg.Tab('Help', layout=[
            []
        ], key=f"SETTINGS_MENU_HELP_TAB{suffix}")

        tab_layout = [[api_tab], [config_tab], [system_tab], [help_tab]]
        layout = [
            [sg.Text('Settings', expand_x=True),
             sg.Button(tooltip='Back', button_color=sg.theme_button_color(),
                       key=f'SETTINGS_MENU_BACK_BUTTON{suffix}',
                       button_text='Back'),
             sg.Button(tooltip='Exit', button_color=sg.theme_button_color(),
                       key=f'SETTINGS_MENU_EXIT_BUTTON{suffix}',
                       button_text='Exit')
             ],
            [sg.TabGroup(layout=tab_layout, tab_location='righttop', expand_x=True, expand_y=True)],
            [sg.Sizegrip()]
        ]
        return sg.Window(title=f'{self.get_title()}{suffix}',
                         layout=layout,
                         size=(350, 500),
                         no_titlebar=True,
                         grab_anywhere=True,
                         keep_on_top=(True if not keep_on_top else keep_on_top),
                         modal=True)

    @staticmethod
    def element_keys(suffix):
        return [f'LISTBOX_DEEPL_LANG_FROM{suffix}', f'LISTBOX_DEEPL_LANG_TO{suffix}',
                f'LISTBOX_BUZZ_LANG_TO{suffix}', f'LISTBOX_BUZZ_MODELS{suffix}',
                f'LISTBOX_BUZZ_MODEL_SIZE{suffix}', f'LISTBOX_BUZZ_TASK_TYPE{suffix}',
                f'LISTBOX_BUZZ_OUT_FMT{suffix}', f'LISTBOX_SYSTEM_GAMEDATA{suffix}',
                f'LISTBOX_SYSTEM_SAVE_FOLDER{suffix}', f"SETTINGS_MENU_DEEPL_TAB{suffix}",
                f"SETTINGS_MENU_BUZZ_TAB{suffix}", f"SETTINGS_MENU_HELP_TAB{suffix}",
                f'SETTINGS_MENU_EXIT_BUTTON{suffix}', f'SETTINGS_LOAD_KEY_FILE_BUTTON{suffix},'
                                                      f'SETTINGS_LOAD_KEY_ENV_BUTTON{suffix}']

    @staticmethod
    def select_folder():
        background_color = sg.theme_input_background_color()
        layout = [
            [sg.Text('Select a folder:', background_color=background_color)],
            [sg.FolderBrowse('Browse', size=(18, 1), auto_size_button=True, key='folder_input')],
            [sg.Button('Exit', expand_x=True)]
        ]

        window = sg.Window('folder_browser', layout=layout, background_color=background_color,
                           no_titlebar=True, grab_anywhere=True, keep_on_top=True, modal=True)

        while True:
            event, values = window.read()
            if event in 'Exit':
                window.close()
                return None if values['folder_input'] is None else values['folder_input']

    @staticmethod
    def select_file():
        background_color = sg.theme_input_background_color()
        layout = [
            [sg.Text('Select a file:', background_color=background_color)],
            [sg.FileBrowse('Browse', size=(18, 1), auto_size_button=True, key='file_input')],
            [sg.Button('Exit', expand_x=True)]
        ]

        window = sg.Window('file_browser', layout=layout, background_color=background_color,
                           no_titlebar=True, grab_anywhere=True, keep_on_top=True, modal=True)

        while True:
            event, values = window.read()
            if event in 'Exit':
                window.close()
                return None if values['file_input'] is None else values['file_input']

