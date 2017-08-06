""" 
Current Status: Does not work if dropdown menu is clicked.
""" 

from aqt import editor
from aqt import utils

from anki.hooks import wrap
from PyQt4 import QtGui, QtCore

import sys
import os

# Creates a match string
def load_match_string(self, match_list):
	output = '['
	for key, val in match_list:
		output += '{"key":"' + key + '","val":"' + val + '"},'
	return output[:-1] + ']'

# Setup function
def my_setup(self, note, hide=True, focus=False):
	if self.note:
		# Load list of matches
		match_str = load_match_string(self, DEFAULT_MATCHES)

		# Load JS file
		js_file = QtCore.QFile(":/init_script")
		if js_file.open(QtCore.QIODevice.ReadOnly | QtCore.QFile.Text):
			js = QtCore.QTextStream(js_file).readAll()
			js_file.close()
			self.web.eval(js % match_str)

# Bridging function
def my_bridge(self, str, _old=None):
	if str.startswith("debug_err"):
		(_, value) = str.split(":", 1)
		sys.stderr.write(value)
	if str.startswith("debug_div"):
		(_, value) = str.split(":", 1)
		self.web.eval('$(".debug").html("%s")' % value)

editor.Editor.setNote = wrap(editor.Editor.setNote, my_setup, 'after')
editor.Editor.bridge = wrap(editor.Editor.bridge, my_bridge, 'before')


# Strings to replace.
DEFAULT_MATCHES = [
	# Arrows
	('-&gt;', 		'\u2192'),
	(':N:', 		'\u2191'),
	(':S:', 		'\u2193'),
	(':E:', 		'\u2192'),
	(':W:', 		'\u2190'),

	# Math symbols
	(':geq:', 		'\u2265'),
	(':leq:', 		'\u2264'),
	('&gt;&gt;', 	'\u226B'),
	('&lt;&lt;',	'\u2264'),
	(':pm:', 		'\u00B1'),
	(':infty:', 	'\u221E'),
	(':approx:',	'\u2248'),
	(':neq:', 		'\u2260'),

	# Fractions
	(':1/2:', 		'\u00BD'),
	(':1/3:',		'\u2153'),
	(':2/3:', 		'\u2154'),
	(':1/4:',		'\u00BC'),
	(':3/4:', 		'\u00BE'),

	# Greek letters (lowercase)
	(':alpha:', 	'\u03B1'),
	(':beta:', 		'\u03B2'),
	(':gamma:', 	'\u03B3'),
	(':delta:', 	'\u03B4'),
	(':episilon:', 	'\u03B5'),
	(':zeta:', 		'\u03B6'),
	(':eta:', 		'\u03B7'),
	(':theta:', 	'\u03B8'),
	(':iota:', 		'\u03B9'),
	(':kappa:', 	'\u03BA'),
	(':lambda:', 	'\u03BB'),
	(':mu:', 		'\u03BC'),
	(':nu:', 		'\u03BD'),
	(':xi:', 		'\u03BE'),
	(':omicron:', 	'\u03BF'),
	(':pi:', 		'\u03C0'),
	(':rho:', 		'\u03C1'),
	(':sigma:', 	'\u03C3'),
	(':tau:', 		'\u03C4'),
	(':upsilon:', 	'\u03C5'),
	(':phi:', 		'\u03C6'),
	(':chi:', 		'\u03C7'),
	(':psi:', 		'\u03C8'),
	(':omega:', 	'\u03C9'),

	# Greek letters (uppercase)
	(':Alpha:', 	'\u0391'),
	(':Beta:', 		'\u0392'),
	(':Gamma:', 	'\u0393'),
	(':Delta:', 	'\u0394'),
	(':Episilon:', 	'\u0395'),
	(':Zeta:', 		'\u0396'),
	(':Eta:', 		'\u0397'),
	(':Theta:', 	'\u0398'),
	(':Iota:', 		'\u0399'),
	(':Kappa:', 	'\u039A'),
	(':Lambda:', 	'\u039B'),
	(':Mu:', 		'\u039C'),
	(':Nu:', 		'\u039D'),
	(':Xi:', 		'\u039E'),
	(':Omicron:', 	'\u039F'),
	(':Pi:', 		'\u03A0'),
	(':Rho:', 		'\u03A1'),
	(':Sigma:', 	'\u03A3'),
	(':Tau:', 		'\u03A4'),
	(':Upsilon:', 	'\u03A5'),
	(':Phi:', 		'\u03A6'),
	(':Chi:', 		'\u03A7'),
	(':Psi:', 		'\u03A8'),
	(':Omega:', 	'\u03A9')
]
