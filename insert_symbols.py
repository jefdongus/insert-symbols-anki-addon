"""
Performs setup when the profile, main window, and editor window is loaded.
"""

import sys
import os

from PyQt4 import QtCore

from aqt import editor, utils, mw
from anki.hooks import addHook, wrap

from symbol_manager import *
from symbol_window import SymbolWindow

PLUGIN_NAME = 'insert_symbols'

""" Profile Loading Actions """

def on_profile_loaded():
	mw.ins_sym_manager = SymbolManager(mw, update_symbols)
	mw.ins_sym_window = SymbolWindow(mw, mw.ins_sym_manager)
	mw.ins_sym_manager.on_profile_loaded()

addHook("profileLoaded", on_profile_loaded)


""" Main Window toolbar setup """
def show_symbol_window():
	mw.ins_sym_window.open()

open_action = aqt.qt.QAction("Insert Symbol Options...", mw, triggered=show_symbol_window)
mw.form.menuTools.addAction(open_action)


""" Editor Actions (note: self refers to the calling editor in the functions below) """

open_editors = []	# List of open editors

# Loads JS into the editor's WebView.
def _add_JS_to_editor(editor):
	with open(mw.pm.addonFolder() + '/' + PLUGIN_NAME + '/init_script.js', 'r') as js_file:
		js = js_file.read()
		editor.web.eval(js % mw.ins_sym_manager.get_JSON())

# This function is called by SymbolManager whenever the symbol list is updated. It updates the
# symbolList for every editor that is open.
def update_symbols():
	for editor in open_editors:
		editor.web.eval("insert_symbols.setMatchList(\'%s\')" % mw.ins_sym_manager.get_JSON())

# There is no dedicated cleanup function in Anki 2.0, so using loading / unloading notes
# to keep track of which editors need to be updated in update_symbols().
# Note: In Anki 2.1 editor.setNote() calls editor.loadNote(), so no need to call 
# _add_JS_to_editor() here.
def on_editor_set_note(self, note, hide=True, focus=False):
	if self.note:
		if self not in open_editors:
			open_editors.append(self)
			#sys.stderr.write("Open Editors: " + str(len(open_editors)))
		_add_JS_to_editor(self)
	else:
		if self in open_editors:
			open_editors.remove(self)
			#sys.stderr.write("Open Editors: " + str(len(open_editors)))

# The loadNote wrapper is needed because the JS gets reloaded if the "Edit HTML" button is pressed, 
# so the plugin no longer works in that editor window. Thus, we have to reload it.
editor.Editor.setNote = wrap(editor.Editor.setNote, on_editor_set_note, 'after')
editor.Editor.loadNote = wrap(editor.Editor.loadNote, _add_JS_to_editor, 'after')

# Bridge function for debugging
def on_editor_bridge(self, string, _old=None):
	if string.startswith("debug_err"):
		(_, value) = string.split(":", 1)
		sys.stderr.write(value)
	elif string.startswith("debug_div"):
		(_, value) = string.split(":", 1)
		self.web.eval('$(".debug").html("%s")' % value)

editor.Editor.bridge = wrap(editor.Editor.bridge, on_editor_bridge, 'before')
