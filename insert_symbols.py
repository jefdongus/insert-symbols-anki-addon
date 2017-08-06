""" 
Current Status: Does not work if dropdown menu is clicked.
""" 
import sys
import os

from PyQt4 import QtCore

from aqt import editor, utils
from anki.hooks import addHook, wrap

from symbol_manager import *
from symbol_window import SymbolWindow

# Creates a match string
def make_match_string(self, match_list):
	output = '['
	for key, val in match_list:
		output += '{"key":"' + key + '","val":"' + val + '"},'
	return output[:-1] + ']'

# Setup function
def my_setup(self, note, hide=True, focus=False):
	if self.note:
		# Load list of matches
		match_str = make_match_string(self, DEFAULT_MATCHES)

		# Load JS file
		cur_dir = os.getcwd()
		idx = cur_dir.find("Anki2")
		if idx > -1:
			cur_dir = cur_dir[ : idx + 5]
		with open(cur_dir + "/addons/insert_symbols/init_script.js", "r") as js_file:
			js = js_file.read()
			self.web.eval(js % match_str)

		# js_file = QtCore.QFile(":/init_script")
		# o = js_file.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text)
		# sys.stderr.write(str(o))
		# if o:
		# 	js = QtCore.QTextStream(js_file).readAll()
		# 	js_file.close()
		# 	self.web.eval(js % match_str)
		# 	sys.stderr.write("WTF")

# Bridging function
def my_bridge(self, str, _old=None):
	if str.startswith("debug_err"):
		(_, value) = str.split(":", 1)
		sys.stderr.write(value)
	if str.startswith("debug_div"):
		(_, value) = str.split(":", 1)
		self.web.eval('$(".debug").html("%s")' % value)

    
def add_open_symbol_window(editor):
	editor.symbol_window = SymbolWindow(editor, editor.parentWindow)
	return editor._addButton(":/symbol_tmp", editor.symbol_window.open, _(""), _("Insert Symbol"))


editor.Editor.setNote = wrap(editor.Editor.setNote, my_setup, 'after')
editor.Editor.bridge = wrap(editor.Editor.bridge, my_bridge, 'before')

#addHook("setupEditorButtons", add_open_symbol_window)
