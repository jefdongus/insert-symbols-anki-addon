# Acts as the central manager for symbol list. Interfaces with the SQLite database to store
# changes to the symbol list.

# TODO: Documentation

import aqt
import aqt.utils

TBL_NAME = 'ins_symbols'

# SQLite commands
#
# List all tables: mw.col.db.all("select name from sqlite_master where type = 'table'")
# Check if table exists: mw.col.db.first("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='NAME'")
# Create table: mw.col.db.execute("create table if not exists NAME (key varchar(255), kalue varchar(255))")
# Insert: mw.col.db.execute("insert into NAME values (?, ?)", *, *)
# Read all: mw.col.db.all("select * from NAME")
#
# mw.pm.db = profiles database -- maybe better to store things in Collections still?

class SymbolManager(object):

	def __init__(self, main_window, update_callback):
		self._db = main_window.col.db
		self._symbols = None
		self._update_callback = update_callback

	# Turns symbols into a JSON string
	def get_JSON(self):
		if not self._symbols:
			return '[]'
		output = '['
		for key, val in self._symbols:
			output += '{"key":"%s","val":"%s"},' % (key, val)
		return output[:-1] + ']'

	def get_copy(self):
		return list(self._symbols)

	def get_default_list(self):
		return sorted(list(DEFAULT_MATCHES), key=lambda x: x[0])

	# This should only be called by a function that performs database operations
	def _set_symbol_list(self, new_list):
		self._symbols = new_list
		self._symbols.sort(key=lambda x: x[0])

	def _create_db(self):
		self._db.execute("CREATE TABLE %s (key varchar(255), value varchar(255))" % TBL_NAME)

	def _load_from_db(self):
		symbols_from_db = self._db.all("SELECT * FROM %s" % TBL_NAME)

		if not symbols_from_db:
			#aqt.utils.showInfo("Error: problem in _load_from_db()!")
			return False
		self._set_symbol_list(symbols_from_db)
		return True

	def _save_to_db(self):
		self._db.execute("delete from %s" % TBL_NAME)
		for (k, v) in self._symbols:
			self._db.execute("INSERT INTO %s VALUES (?, ?)" % TBL_NAME, k, v)
		self._db.commit()

	# Initializes values from DB
	def on_profile_loaded(self):
		exists = self._db.first("SELECT * FROM sqlite_master WHERE type='table' AND name='%s'" % TBL_NAME)

		if not exists:
			# aqt.utils.showInfo("Creating new table")
			self._create_db()
		else:
			# aqt.utils.showInfo("Table already exists")
			exists = self._load_from_db()

		# If database does not exist or cannot be loaded, fallback to loading default list
		if not exists:
			self._set_symbol_list(self.get_default_list())
			self._save_to_db()

	# Called when symbol list has been updated from the SymbolWindow
	def update_symbol_list(self, new_list):
		# TODO validation here
		self._set_symbol_list(new_list)
		self._save_to_db()
		self._update_callback()

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
	(':deg:', 		'\u00B0'),

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

