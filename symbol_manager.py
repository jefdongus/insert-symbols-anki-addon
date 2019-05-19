"""
Acts as the central manager for symbol list. Interfaces with the SQLite database to store changes to 
the symbol list.

TODO: 
1. Load from default_list.txt.
2. Perform more rigorous error checking when loading from DB.
3. Resolve DB name conflicts if possible.
4. Documentation
"""

import aqt
import aqt.utils

class SymbolManager(object):
	""" 
	SymbolManager keeps track of the current symbol list and interfaces with the SQLite database. 

	Symbol lists are stored per-profile. Loading priority:
	1. Symbol list in database
	2. Default symbol list in default_list.txt file
	3. Hard-coded default symbol list.

	"""

	TBL_NAME = 'ins_symbols'
	DEFAULT_FNAME = 'default_list.txt'

	def __init__(self, main_window, update_callback):
		self._db = main_window.col.db
		self._symbols = None
		self._defaults = None
		self._update_callback = update_callback

	def on_profile_loaded(self):
		""" 
		Called when a new profile is loaded. First tries to load the symbol list from the database. If
		that is not successful, loads the default symbol list instead, then saves it to the database.
		"""
		exists = self._check_db_exists()

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


	""" Getters """

	def get_JSON(self):
		""" Converts the symbol list into a JSON string. """
		if not self._symbols:
			return '[]'
		output = '['
		for key, val in self._symbols:
			output += '{"key":"%s","val":"%s"},' % (key, val)
		return output[:-1] + ']'

	def get_copy(self):
		""" Returns a copy of the current symbol list. """
		return list(self._symbols)

	def get_default_list(self):
		""" Returns a copy of the default symbol list. TODO: load from default_list.txt """
		if not self._defaults:
			self._defaults = sorted(DEFAULT_MATCHES, key=lambda x: x[0])

		return list(self._defaults)


	""" Setters """

	def _set_symbol_list(self, new_list):
		""" Setter for self._symbol_list. Assumes that there are no conflicts. """
		self._symbols = new_list
		self._symbols.sort(key=lambda x: x[0])

	def update_symbol_list(self, new_list):
		""" 
		Updates the symbol list to new_list if there are no errors.

		@return List of conflicts, or None if there were no conflicts.
		"""
		conflicts = self.validate_list(new_list)
		if conflicts:
			return conflicts
		else:
			self._set_symbol_list(new_list)
			self._save_to_db()
			self._update_callback()
			return None


	""" Validation """

	def validate_list(self, kv_list):
		"""
		Checks to see if there are any key conflicts within kv_list. 

		@return: Returns a list of conflicting keys, or None if no conflicts.
		"""
		has_conflict = False
		conflicts = []

		for i in range(len(kv_list)):
			for j in range(i):
				k1 = kv_list[i][0]
				k2 = kv_list[j][0]
				if k1 in k2 or k2 in k1:
					has_conflict = True
					conflicts.append(tuple(k1, k2))
		return conflicts if has_conflict else None


	""" 
	Database Access Functions

	List all tables: mw.col.db.all("select name from sqlite_master where type = 'table'")
	Check if table exists: mw.col.db.first("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='NAME'")
	Create table: mw.col.db.execute("create table if not exists NAME (key varchar(255), kalue varchar(255))")
	Insert: mw.col.db.execute("insert into NAME values (?, ?)", *, *)
	Read all: mw.col.db.all("select * from NAME")

	mw.pm.db = profiles database -- maybe better to store things in Collections still? 

	"""

	def _check_db_exists(self):
		""" Returns whether the symbol database exists. """
		return self._db.first("SELECT * FROM sqlite_master WHERE type='table' AND name='%s'" % self.TBL_NAME)

	def _create_db(self):
		""" Creates a new table for the symbol list. """
		self._db.execute("CREATE TABLE %s (key varchar(255), value varchar(255))" % self.TBL_NAME)

	def _load_from_db(self):
		""" 
		Attempts to load the symbol list from the database. TODO: perform more rigorous error checking.

		@return True if symbols were successfully loaded and set, or False if not.
		"""
		symbols_from_db = self._db.all("SELECT * FROM %s" % self.TBL_NAME)

		if not symbols_from_db:
			#aqt.utils.showInfo("Error: problem in _load_from_db()!")
			return False

		# TODO: validate database entries
		conflicts = self.validate_list(symbols_from_db)
		if conflicts:
			return False

		self._set_symbol_list(symbols_from_db)
		return True

	def _save_to_db(self):
		""" Overwrites the symbol list. Currently deletes all values, then writes everything to database. """
		self._db.execute("delete from %s" % self.TBL_NAME)
		for (k, v) in self._symbols:
			self._db.execute("INSERT INTO %s VALUES (?, ?)" % self.TBL_NAME, k, v)
		self._db.commit()


""" Default symbol list. Used as a backup if default_list.txt does not exist. """
DEFAULT_MATCHES = [
	# Arrows
	('->', 			u'\u2192'),
	(':N:', 		u'\u2191'),
	(':S:', 		u'\u2193'),
	(':E:', 		u'\u2192'),
	(':W:', 		u'\u2190'),

	# Math symbols
	(':geq:', 		u'\u2265'),
	(':leq:', 		u'\u2264'),
	('>>', 			u'\u226B'),
	('<<',			u'\u226A'),
	(':pm:', 		u'\u00B1'),
	(':infty:', 	u'\u221E'),
	(':approx:',	u'\u2248'),
	(':neq:', 		u'\u2260'),
	(':deg:', 		u'\u00B0'),

	# Fractions
	(':1/2:', 		u'\u00BD'),
	(':1/3:',		u'\u2153'),
	(':2/3:', 		u'\u2154'),
	(':1/4:',		u'\u00BC'),
	(':3/4:', 		u'\u00BE'),

	# Greek letters (lowercase)
	(':alpha:', 	u'\u03B1'),
	(':beta:', 		u'\u03B2'),
	(':gamma:', 	u'\u03B3'),
	(':delta:', 	u'\u03B4'),
	(':episilon:', 	u'\u03B5'),
	(':zeta:', 		u'\u03B6'),
	(':eta:', 		u'\u03B7'),
	(':theta:', 	u'\u03B8'),
	(':iota:', 		u'\u03B9'),
	(':kappa:', 	u'\u03BA'),
	(':lambda:', 	u'\u03BB'),
	(':mu:', 		u'\u03BC'),
	(':nu:', 		u'\u03BD'),
	(':xi:', 		u'\u03BE'),
	(':omicron:', 	u'\u03BF'),
	(':pi:', 		u'\u03C0'),
	(':rho:', 		u'\u03C1'),
	(':sigma:', 	u'\u03C3'),
	(':tau:', 		u'\u03C4'),
	(':upsilon:', 	u'\u03C5'),
	(':phi:', 		u'\u03C6'),
	(':chi:', 		u'\u03C7'),
	(':psi:', 		u'\u03C8'),
	(':omega:', 	u'\u03C9'),

	# Greek letters (uppercase)
	(':Alpha:', 	u'\u0391'),
	(':Beta:', 		u'\u0392'),
	(':Gamma:', 	u'\u0393'),
	(':Delta:', 	u'\u0394'),
	(':Episilon:', 	u'\u0395'),
	(':Zeta:', 		u'\u0396'),
	(':Eta:', 		u'\u0397'),
	(':Theta:', 	u'\u0398'),
	(':Iota:', 		u'\u0399'),
	(':Kappa:', 	u'\u039A'),
	(':Lambda:', 	u'\u039B'),
	(':Mu:', 		u'\u039C'),
	(':Nu:', 		u'\u039D'),
	(':Xi:', 		u'\u039E'),
	(':Omicron:', 	u'\u039F'),
	(':Pi:', 		u'\u03A0'),
	(':Rho:', 		u'\u03A1'),
	(':Sigma:', 	u'\u03A3'),
	(':Tau:', 		u'\u03A4'),
	(':Upsilon:', 	u'\u03A5'),
	(':Phi:', 		u'\u03A6'),
	(':Chi:', 		u'\u03A7'),
	(':Psi:', 		u'\u03A8'),
	(':Omega:', 	u'\u03A9')
]

