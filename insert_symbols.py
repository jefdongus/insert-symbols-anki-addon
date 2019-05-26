"""
Performs setup when the profile, main window, and editor window is loaded.
"""

import sys
import os

from anki import version
from anki.hooks import addHook, wrap
from aqt import editor, utils, mw

from .symbol_manager import *
from .symbol_window import SymbolWindow

ANKI_VER_21 = version.startswith("2.1.")
SYS_ENCODING = sys.getfilesystemencoding()

if ANKI_VER_21:
    ADDON_PATH = os.path.dirname(__file__)
else:
    ADDON_PATH = os.path.dirname(__file__).decode(SYS_ENCODING)

""" 
Profile Loading Actions 

These actions occur when a new profile is opened.
"""

def on_profile_loaded():
    """ Perform setup when a new profile is loaded. """
    mw.ins_sym_manager = SymbolManager(mw, update_symbols)
    mw.ins_sym_window = SymbolWindow(mw, mw.ins_sym_manager)
    mw.ins_sym_manager.on_profile_loaded()

addHook("profileLoaded", on_profile_loaded)

# Add menu button
open_action = aqt.qt.QAction("Insert Symbol Options...", mw, triggered=lambda: mw.ins_sym_window.open())
mw.form.menuTools.addAction(open_action)


""" 
Editor Actions 

These actions occur when an instance of the card editor defined in Anki's aqt/editor.py (ie. Add Card window 
or Card Browser) is opened.
"""

open_editors = []

def on_editor_set_note(self, note, hide=True, focus=False):
    """
    Anki calls Editor.setNote() when an instance of the editor should be updated. This occurs when either
    the Add Card window or Card Browser either should show a note or is closed. NOTE will either contain the 
    note to show or None if the editor should be closed. 

    We implement this wrapper to keep track of all the editors that are currently open so that any changes
    to the symbol list will be pushed to all editors immediately. Since this is a wrapper to Editor.setNote(), 
    SELF refers to the editor in aqt/editor.py.
    
    FYI: In Anki 2.1, focus=False becomes focusTo=None.
    """
    if note:
        if self not in open_editors:
            open_editors.append(self)
            #sys.stderr.write("Open Editors: " + str(len(open_editors)))
    else:
        if self in open_editors:
            open_editors.remove(self)
            #sys.stderr.write("Open Editors: " + str(len(open_editors)))

def on_editor_load_note(self, focusTo=None):
    """ 
    Anki calls Editor.loadNote() to refresh the editor's WebView with the fields of the note. This occurs
    after Editor.setNote() is called, when the "Edit HTML" command is used (through Editor.onHtmlEdit()), and
    when Editor.bridge() / Editor.onBridgeCmd() is called.

    We implement this wrapper to add the Javascript code that performs symbol replacement into the WebView.
    The code gets cleared after every call to Editor.loadNote(), so it's not enough to add the Javascript
    during on_editor_set_note() only. Since this is a wrapper to Editor.setNote(), SELF refers to the editor 
    in aqt/editor.py.

    FYI: In Anki 2.1, 1) the focusTo=None argument is new and 2) there is now a hook for loadNote().
    """
    js_path = os.path.join(ADDON_PATH, "replacer.js")
    with open(js_path, 'r') as js_file:
        js = js_file.read()
        self.web.eval(js % mw.ins_sym_manager.get_JSON())

def update_symbols():
    """
    This function is called by SymbolManager whenever the symbol list is updated. It updates the
    symbolList for every editor that is open.
    """
    for editor in open_editors:
        editor.web.eval("insert_symbols.setMatchList(\'%s\')" % mw.ins_sym_manager.get_JSON())

# Add wrappers:
editor.Editor.setNote = wrap(editor.Editor.setNote, on_editor_set_note, 'after')
editor.Editor.loadNote = wrap(editor.Editor.loadNote, on_editor_load_note, 'after')


""" 
Debugging Functions 

Note: In Anki 2.1, the bridge() function in editor is renamed to onBridgeCmd().
"""

def on_editor_bridge(self, string, _old=None):
	# Note: this doesn't quite work in Anki 2.1 yet
    if string.startswith("debug_err"):
        (_, value) = string.split(":", 1)
        sys.stderr.write(value)
    elif string.startswith("debug_div"):
        (_, value) = string.split(":", 1)
        self.web.eval('$(".debug").html("%s")' % value)

if ANKI_VER_21:
    editor.Editor.bridge = wrap(editor.Editor.onBridgeCmd, on_editor_bridge, 'before')
else:
    editor.Editor.bridge = wrap(editor.Editor.bridge, on_editor_bridge, 'before')