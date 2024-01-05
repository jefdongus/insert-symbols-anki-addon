"""
This file is run when the plugin is first loaded. It contains functions to set 
up the plugin, open the symbol list editor, and broadcast symbol list updates
to editor windows that are open. 
"""

import os
import sys

import aqt
from anki.hooks import addHook, wrap
from aqt.editor import Editor, EditorWebView
from aqt.reviewer import Reviewer
from aqt.browser import Browser

from .browser_replacer import BrowserReplacer
from .get_version import *
from .symbol_manager import SymbolManager
from .symbol_window import SymbolWindow

""" 
Anki Version-specific Code 
"""

ANKI_VER = get_anki_version()

# Add-on path changed between Anki 2.0 and Anki 2.1
if ANKI_VER == ANKI_VER_PRE_2_1_0:
    sys_encoding = sys.getfilesystemencoding()
    ADDON_PATH = os.path.dirname(__file__).decode(sys_encoding)
else:
    ADDON_PATH = os.path.dirname(__file__)

# Load new hooks if supported
if ANKI_VER > ANKI_VER_PRE_23_10:
    from aqt import gui_hooks

# Webview requires different JS between Anki 2.1.40 and Anki 2.1.41
if ANKI_VER <= ANKI_VER_PRE_2_1_41:
    JS_FILE = "replacer_pre-2.1.41.js"
else:
    JS_FILE = "replacer.js"


""" 
Variable declarations
"""

ins_sym_manager = None
ins_sym_window = None
ins_sym_replacer = None

ins_sym_webview_owners = {
    'editors': [],
    'reviewer': None
}


"""
Javascript Loading & Updating
"""

def _update_JS(webview: EditorWebView):
    """ Updates the symbol list in the Javascript file. """
    json = ins_sym_manager.get_JSON()
    webview.eval("insert_symbols.setMatchList(%s)" % json)

def _load_JS(webview: EditorWebView):
    """ 
    Loads replacer.js, the Javascript file which performs symbol replacement, 
    into the given WebView.
    """
    js_path = os.path.join(ADDON_PATH, JS_FILE)
    with open(js_path, 'r') as js_file:
        js = js_file.read()
        webview.eval(js)
        _update_JS(webview)

def update_symbols():
    """
    This function is called by SymbolManager whenever the symbol list is 
    updated. It updates the symbolList for every editor that is open.
    """

    for editor in ins_sym_webview_owners['editors']:
        _update_JS(editor.web)

    if ins_sym_webview_owners['reviewer']:
        _update_JS(ins_sym_webview_owners['reviewer'].web)

    ins_sym_replacer.update_list(ins_sym_manager.get_match_list())

    # aqt.utils.showInfo("Number of editors: %d" % len(ins_sym_webview_owners['editors']))

""" 
Editor Actions 

These actions occur when an instance of the card editor defined in Anki's 
aqt/editor.py (ie. Add Card window, Card Browser, or Reviewer) is opened.
"""

def on_editor_load_note(editor: Editor, focusTo=None):
    """ 
    Anki calls Editor.loadNote() to refresh the editor's WebView, which occurs 
    after setNote(), onHtmlEdit(), and bridge() / onBridgeCmd() in Editor is 
    called. Editor.loadNote() resets Javascript code, so we must re-add our JS
    after every loadNote(). 

    FYI: In Anki 2.1, the focusTo=None argument is new.
    """
    if editor not in ins_sym_webview_owners['editors']:
        ins_sym_webview_owners['editors'].append(editor)

    _load_JS(editor.web)

def on_editor_cleanup(editor: Editor):
    ins_sym_webview_owners['editors'].remove(editor)

def on_browser_init(browser: Browser, main_window = None, card = None, 
    search = None):
    ins_sym_replacer.on_browser_init(browser)

def on_reviewer_initweb(reviewer: Reviewer):
    """
    Anki calls Reviewer._initWeb() to update the WebView, which occurs when the
    reviewer is first opened or after every 100 cards have been reviewed. 
    """
    ins_sym_webview_owners['reviewer'] = reviewer
    _load_JS(reviewer.web)
    # aqt.utils.showInfo("on_reviewer_start() called")

def on_reviewer_show_qa(card=None):
    """ 
    This event is triggered when the Reviewer shows either a question or an
    answer. Since the Editable Fields plugin makes the fields editable when 
    each card is created, key listeners need to be set up after each time.
    """
    webview = ins_sym_webview_owners['reviewer'].web
    if webview:
        webview.eval("insert_symbols.setupReviewerKeyEvents()")
    # aqt.utils.showInfo("on_show_qa() called")

def on_reviewer_cleanup():
    """ This event is triggered when the Reviewer is about to be closed. """
    ins_sym_webview_owners['reviewer'] = None
    # aqt.utils.showInfo("on_reviewer_end() called")


""" 
Add-on Initialization

These actions occur when a new profile is opened since each profile can have
its own symbol list.
"""

def _setup_modules():
    global ins_sym_manager, ins_sym_window, ins_sym_replacer

    ins_sym_manager = SymbolManager(aqt.mw, update_symbols)
    ins_sym_manager.on_profile_loaded()

    ins_sym_window = SymbolWindow(aqt.mw, ins_sym_manager)
    ins_sym_replacer = BrowserReplacer(ins_sym_manager.get_match_list()) 

def _setup_hooks():
    """
    Migrate to new hooks when possible though currently no suitable hooks for 
    editor cleanup, browser init (gui_hooks.browser_will_show runs before search
    bar is set up), or reviewer webview initiation (gui_hooks.reviewer_did_init
    doesn't work).
    """

    gui_hooks.editor_did_load_note.append(on_editor_load_note)
    Editor.cleanup = wrap(Editor.cleanup, on_editor_cleanup, 'before')

    Browser.__init__ = wrap(Browser.__init__, on_browser_init, 'after')

    Reviewer._initWeb = wrap(Reviewer._initWeb, on_reviewer_initweb, 'after')
    gui_hooks.reviewer_did_show_question.append(on_reviewer_show_qa)
    gui_hooks.reviewer_did_show_answer.append(on_reviewer_show_qa)
    gui_hooks.reviewer_will_end.append(on_reviewer_cleanup)

def _setup_hooks_legacy():
    Editor.loadNote = wrap(Editor.loadNote, on_editor_load_note, 'after')
    Editor.cleanup = wrap(Editor.cleanup, on_editor_cleanup, 'before')

    Browser.__init__ = wrap(Browser.__init__, on_browser_init, 'after')

    Reviewer._initWeb = wrap(Reviewer._initWeb, on_reviewer_initweb, 'after')
    addHook("showQuestion", on_reviewer_show_qa)
    addHook("showAnswer", on_reviewer_show_qa)
    addHook("reviewCleanup", on_reviewer_cleanup)

# Perform setup when a new profile is loaded

def on_profile_loaded():
    _setup_modules()
    _setup_hooks()

def on_profile_loaded_legacy():
    _setup_modules()
    _setup_hooks_legacy()

if ANKI_VER <= ANKI_VER_PRE_23_10:
    addHook("profileLoaded", on_profile_loaded_legacy)
else:
    gui_hooks.profile_did_open.append(on_profile_loaded)

# Add menu button
open_action = aqt.qt.QAction("Insert Symbol Options...", aqt.mw, 
    triggered=lambda: ins_sym_window.open())
aqt.mw.form.menuTools.addAction(open_action)
