# coding: utf-8

import sys
import sublime
import sublime_plugin
import subprocess
from os import name
from os.path import abspath, dirname, exists, join, normpath, expanduser

__file__ = normpath(abspath(__file__))
__path__ = dirname(__file__)

MODULES_PATH = join(__path__, 'node_modules')
BIN_PATH = join(MODULES_PATH, '.bin', 'csscomb')
CONFIG_NAME = '.csscomb.json'
DEFAULT_CONFIG = join(MODULES_PATH, 'csscomb', CONFIG_NAME)
USERS_FOLDER = dirname(expanduser("~"))

is_python3 = sys.version_info[0] > 2
startupinfo = None
if name == 'nt':
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE


class Utils():
    def check_for_node(self, config={}):
        try:
            return True if subprocess.call(['node', '-v'], shell=False, startupinfo=startupinfo) == 0 else False
        except Exception as e:
            if config.run_by_user:
                sublime.error_message('CSScomb\nWasn\'t able to find Node.JS.\nMake sure it is available in your PATH.\n\n%s' % e)
            return

    def get_config_path(self):
        view = sublime.active_window().active_view()

        # projectconfig = self.get_project_config(view)

        # if projectconfig and exists(projectconfig):
        #     path = projectconfig
        #     print('projectconfig', projectconfig)
        # else:
        foundconfig = self.find_config(view)
        if (foundconfig):
            path = foundconfig
            print('found config', foundconfig)
        else:
            path = DEFAULT_CONFIG
            print('using default config', DEFAULT_CONFIG)

        sublime.status_message('csscomb.js config: %s' % path)
        return path

    # def get_project_config(self, view):
    #     project_file_name = view.window().project_file_name()
    #     print('project_file_name', project_file_name)
    #     return join(dirname(project_file_name), CONFIG_NAME) if project_file_name else None

    def find_config(self, view):
        cur_dir = dirname(view.file_name())
        cur_config = join(cur_dir, CONFIG_NAME)
        if exists(cur_config):
            print('found_path', cur_config)
            return cur_config
        else:
            while cur_dir != USERS_FOLDER:
                print('cur_dir', cur_dir)
                cur_dir = dirname(cur_dir)
                cur_config = join(cur_dir, CONFIG_NAME)
                if(exists(cur_config)):
                    print('recursively found config', cur_config)
                    return cur_config
                    break
                pass
        return None

utils = Utils()
is_node_available = utils.check_for_node()


class CssComb(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view
        self.error = False

    def run(self, edit):
        # skip check to speed things up assuming
        # that people much more often install nodejs then remove
        if is_node_available is False:
            utils.check_for_node({"run_by_user": True})

        file_path = self.view.file_name()
        config_path = utils.get_config_path()

        self.sort(file_path, config_path)

    def sort(self, file_path, config_path):
        myprocess = subprocess.Popen(['node', BIN_PATH, file_path, '--config', config_path], shell=False, stdout=subprocess.PIPE, startupinfo=startupinfo)
        (sout, serr) = myprocess.communicate()
        myprocess.wait()

        if serr:
            sublime.error_message(self.status)
            return
        elif sout is None:
            sublime.error_message('There was an error sorting CSS.')
            return

        sublime.set_timeout(self._reload, 500)

    def _reload(self):
        self.view.run_command('revert')


class CssCombNewConfig(sublime_plugin.WindowCommand):
    def run(self):
        self.window.new_file().run_command('css_comb_insert_config')


class CssCombInsertConfig(sublime_plugin.TextCommand):
    def run(self, edit):
        with open(DEFAULT_CONFIG, 'r') as content_file:
            content = content_file.read()
            self.view.insert(edit, 0, content)
            self.view.set_name(CONFIG_NAME)
            self.view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')
