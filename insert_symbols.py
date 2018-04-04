""" 
Current Status: Does not work if dropdown menu is clicked.
""" 
import sys
import os

from PyQt4 import QtCore

from aqt import editor, utils, mw
from anki.hooks import addHook, wrap

from symbol_manager import *
from symbol_window import SymbolWindow

PLUGIN_NAME = 'insert_symbols'

# load profile
def on_profile_loaded():
	mw.ins_sym_manager = SymbolManager(mw, on_update_symbols)
	mw.ins_sym_window = SymbolWindow(mw, mw.ins_sym_manager)
	mw.ins_sym_manager.on_profile_loaded()

# Setup function
def on_editor_setup(self, note, hide=True, focus=False):
	if self.note:
		with open(mw.pm.addonFolder() + '/' + PLUGIN_NAME + '/init_script.js', 'r') as js_file:
			js = js_file.read()
			self.web.eval(js % mw.ins_sym_manager.get_JSON())

# Update callback
def on_update_symbols(self):
	# call self.web.eval
	return

# Bridging function --For debugging
def on_editor_bridge(self, string, _old=None):
	if string == "load":
		on_update_symbols()
	elif string.startswith("debug_err"):
		(_, value) = string.split(":", 1)
		sys.stderr.write(value)
	elif string.startswith("debug_div"):
		(_, value) = string.split(":", 1)
		self.web.eval('$(".debug").html("%s")' % value)

def add_open_symbol_window(editor):
	editor.symbol_window = SymbolWindow(editor, editor.parentWindow)
	return editor._addButton(":/symbol_tmp", editor.symbol_window.open, _(""), _("Insert Symbol"))

# Open SymbolWindow

def show_symbol_window():
	mw.ins_sym_window.open()

open_action = aqt.qt.QAction("Insert Symbol Options...", mw, triggered=show_symbol_window)
mw.form.menuTools.addAction(open_action)

# Editor hooks

addHook("profileLoaded", on_profile_loaded)

editor.Editor.setNote = wrap(editor.Editor.setNote, on_editor_setup, 'after')
editor.Editor.bridge = wrap(editor.Editor.bridge, on_editor_bridge, 'before')

#addHook("setupEditorButtons", add_open_symbol_window)
