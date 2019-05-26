"""
Acts as the central manager for symbol list. Interfaces with the SQLite database to store changes to 
the symbol list.

TODO: Resolve DB name conflicts if possible.
"""

import aqt
import aqt.utils

from default_symbols import DEFAULT_MATCHES

class SymbolManager(object):
    """ 
    SymbolManager keeps track of the current symbol list and interfaces with the SQLite database. 

    Symbol lists are stored per-profile.
    """

    TBL_NAME = 'ins_symbols'

    SUCCESS = 0
    ERR_NO_DATABASE = -1
    ERR_INVALID_FORMAT = -2
    ERR_KEY_CONFLICT = -3

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
        is_load_successful = self._check_db_exists()

        if not is_load_successful:
            # aqt.utils.showInfo("Table does not exist. Creating new table.")
            self._create_db()
        else:
            code = self._load_from_db()
            is_load_successful = (code == self.SUCCESS)

        # At this point, the database should have been created already. If load wasn't successful for
        # whatever reason, use the default list and save it to the database.
        if not is_load_successful:
            self._symbols = self.get_default_list()
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
        """ Returns a copy of the default symbol list. """
        return sorted(DEFAULT_MATCHES, key=lambda x: x[0])


    """ Setters """

    def _set_symbol_list(self, new_list):
        """ 
        Performs error-checking, then updates self._symbols. Returns None if there are no errors, or
        otherwise returns a tuple of the format (ERROR_CODE, ERRORS) as detailed below:

         Error Code:         Content of ERRORS:
        -------------       ----------------------
        ERR_INVALID_FORMAT  List of indices where format of new_list is incorrect.
        ERR_KEY_CONFLICT    List of key conflicts in new_list.
        """
        errors = SymbolManager.check_format(new_list)
        if errors:
            return (self.ERR_INVALID_FORMAT, errors)

        errors = SymbolManager.check_for_conflicts(new_list)
        if errors:
            return (self.ERR_KEY_CONFLICT, errors)

        self._symbols = new_list
        self._symbols.sort(key=lambda x: x[0])
        return None

    def update_and_save_symbol_list(self, new_list):
        """ 
        Attempts to update the symbol list, and if successful saves the symbol list to database
        and calls the callback function. Returns the same output as _set_symbol_list().

        """
        errors = self._set_symbol_list(new_list)
        if not errors:
            self._save_to_db()
            self._update_callback()
        return errors


    """ Validation Static Functions """

    @staticmethod
    def check_format(kv_list, ignore_empty=False):
        """ 
        Checks that the key-value list is in the correct format. Each entry must be a list/tuple of the format
        (key, value), and the key must not be None or the empty string. This function can be set to ignore 
        emtpy lines.

        @param kv_list: A list.
        @param ignore_empty: Whether to skip empty lines (represented as an empty list)
        @return: Returns a list of (index, line_contents), or None if no invalid lines.
        """
        has_error = False
        errors = []
        for i in range(len(kv_list)):
            item = kv_list[i]
            if ignore_empty and len(item) == 0:
                continue

            if len(item) != 2 or not item[0]:
                has_error = True
                err_str = ' '.join(map(str, item))
                errors.append(tuple((i, err_str)))
        return errors if has_error else None

    @staticmethod
    def check_for_conflicts(kv_list):
        """
        Checks that there are no key conflicts within the key-value list. This function accepts empty lines.

        @param kv_list: A list of key-value pairs, with each entry either being a list/tuple of format
          (key, value) or an empty list.
        @return: Returns a list of (index, conflicting_key_A, conflicting_key_B), or None if no conflicts.
        """
        has_conflict = False
        conflicts = []

        for i in range(len(kv_list)):
            if len(kv_list[i]) == 0:
                continue

            for j in range(i):
                if len(kv_list[j]) == 0:
                    continue
                k1 = kv_list[i][0]
                k2 = kv_list[j][0]

                if k1 in k2 or k2 in k1:
                    has_conflict = True
                    conflicts.append(tuple((i, k1, k2)))

        return conflicts if has_conflict else None

    @staticmethod
    def check_key_for_conflict(new_key, kv_list):
        """ 
        Checks to see if the new key would conflict with any existing key-value pairs during runtime. No keys should
        be substrings of each other. For example, a key of 'AAA' would prevent '/AAABC' from ever being used.

        @param kv_list: A list of key-value pairs in the format (key, value). 
        @return: Returns the first conflicting key, or None if no conflicts.
        """
        for k, v in kv_list:
            if k in new_key or new_key in k:
                return k
        return None


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
        """ Attempts to load the symbol list from the database, and returns a code indicating the result. """
        symbols_from_db = self._db.all("SELECT * FROM %s" % self.TBL_NAME)

        if not symbols_from_db:
            return self.ERR_NO_DATABASE
        errors = self._set_symbol_list(symbols_from_db)

        return errors[0] if errors else self.SUCCESS

    def _save_to_db(self):
        """ Overwrites the symbol list. Currently deletes all values, then writes everything to database. """
        self._db.execute("delete from %s" % self.TBL_NAME)
        for (k, v) in self._symbols:
            self._db.execute("INSERT INTO %s VALUES (?, ?)" % self.TBL_NAME, k, v)
        self._db.commit()

