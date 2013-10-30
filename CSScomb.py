# coding: utf-8

import sys
import sublime
import sublime_plugin
import subprocess
# import json
from os import path, name

__file__ = path.normpath(path.abspath(__file__))
__path__ = path.dirname(__file__)
node_modules_path = path.join(__path__, 'node_modules', '.bin')
csscomb_path = path.join(node_modules_path, 'csscomb')
# is_python3 = sys.version_info[0] > 2

configname = '.csscomb.json'
possibleconfigs = sublime.find_resources(configname)
guessedconfig = path.abspath( path.relpath(possibleconfigs[0], 'Packages') )
builtinconfig = path.join(__path__, 'node_modules', 'csscomb', configname)
globalconfig = '~/'+configname

class CssComb(sublime_plugin.TextCommand):

    def __init__(self, view):
        self.view = view
        self.startupinfo = None
        self.error = False
        if name == 'nt':
            self.startupinfo = subprocess.STARTUPINFO()
            self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.startupinfo.wShowWindow = subprocess.SW_HIDE


    def run(self, edit):
        self.check_for_node()

        # self.sortorder = False
        # self.order_settings = sublime.load_settings('CSScomb.sublime-settings')
        # if self.order_settings.has('custom_sort_order') and self.order_settings.get('custom_sort_order') is True:
        #     self.sortorder = json.dumps(self.order_settings.get('sort_order'))
        #     sublime.status_message('Sorting with custom sort order...')
        # else:
        #     self.sortorder = ''

        filepath = self.view.file_name()

        projectconfig = path.join( path.dirname(self.view.window().project_file_name() ), configname)

        print(guessedconfig)
        print(projectconfig)
        print(builtinconfig)
        print(globalconfig)
        configpath = guessedconfig

        sublime.status_message('csscomb.js config used for sorting: '+ configpath)
        myprocess = subprocess.Popen(['node', csscomb_path, filepath, '--config', configpath], shell=False, stdout=subprocess.PIPE, startupinfo=self.startupinfo)
        (sout, serr) = myprocess.communicate()
        myprocess.wait()

        if serr:
            sublime.error_message(self.status)
            return
        elif sout is None:
            sublime.error_message('There was an error sorting CSS.')
            return

        sublime.set_timeout(self.reload_, 500)

    def check_for_node(self):
        try:
            subprocess.call(['node', '-v'], shell=False, startupinfo=self.startupinfo)
        except (OSError):
            sublime.error_message('Unable to find Node.JS. Make sure it is available in your PATH.')
            return

    def reload_(self):
        self.view.run_command('revert')

class CssCombNewConfig(sublime_plugin.WindowCommand):
    def run(self):
        window = self.window
        newview = window.new_file()
        newview.run_command('css_comb_insert_config');

class CssCombInsertConfig(sublime_plugin.TextCommand):
    def run(self, edit):
        with open(builtinconfig, 'r') as content_file:
            content = content_file.read()
            self.view.insert(edit, 0, content)
            self.view.set_name(configname)
            self.view.set_syntax_file('Packages/JavaScript/JSON.tmLanguage')