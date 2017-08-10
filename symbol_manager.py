# TODO imports

TBL_NAME = 'ins_symbols'

class SymbolManager(object):

	def __init__(self, main_window):
		self.mw = main_window
		self.symbols = None

	# Turns symbols into a JSON string
	def get_JSON(self):
		if not self.symbols:
			return '[]'
		output = '['
		for key, val in self.symbols:
			output += '{"key":"' + key + '","val":"' + val + '"},'
		return output[:-1] + ']'

	# Initializes values from DB
	def load_from_db(self):
		#exists = self.mw.col.db.execute("SELECT * FROM sqlite_master WHERE name='%s'" % tbl_name).fetchone()
		#if exists:
		#	entries = self.mw.col.db.execute("SELECT * FROM %s" % tbl_name).fetchall()
			# load entries into file
		self.symbols = DEFAULT_MATCHES
		return 

	# Writes changes to DB
	def save_to_db(self):
		#exists = self.mw.col.db.execute("SELECT * FROM sqlite_master WHERE name='%s'" % tbl_name).fetchone()
		#if not exists:
		#	self.mw.col.db.execute("CREATE TABLE %s (Key varchar(255), Value varchar(255))" % tbl_name)
		return

	# Called when symbol list has been updated from the SymbolWindow
	def on_update(self):
		return

	# Called when symbol list has been reset from the SymbolWindow
	def on_reset(self):
		return

# Strings to replace.
DEFAULT_MATCHES = [
	# Arrows
	('->', 			'\u2192'),
	(':N:', 		'\u2191'),
	(':S:', 		'\u2193'),
	(':E:', 		'\u2192'),
	(':W:', 		'\u2190'),

	# Math symbols
	(':geq:', 		'\u2265'),
	(':leq:', 		'\u2264'),
	('>>', 			'\u226B'),
	('<<',			'\u226A'),
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

