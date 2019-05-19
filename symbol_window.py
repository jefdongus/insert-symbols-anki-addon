""" 
Controller for Ui_SymbolWindow. GUI that lets users to edit the symbol list.

"""

import aqt
import io

from PyQt4 import QtGui
from PyQt4.QtGui import QTableWidgetItem, QMessageBox, QAbstractItemView, QFileDialog

from symbol_manager import SymbolManager
from Ui_SymbolWindow import Ui_SymbolWindow

class SymbolWindow(QtGui.QDialog):
	"""
	SymbolWindow is a controller for the symbol list editor. All edits are performed on a copy of the current
	symbol list known as the working list. The symbol list itself is owned by the SymbolManager class, and changes
	are written from the working list to the symbol list only when 'OK' is clicked.

	The working list must obey the following rules at all times:
	1. It must be sorted in alphabetical order by key
	2. There must be no duplicate or conflicting keys (ie. keys that are substrings of one another).
	"""

	def __init__(self, parent_widget, symbol_manager):
		super(SymbolWindow, self).__init__(parent_widget)
		self._sym_manager = symbol_manager
		self._working_list = None
		self._selected_row = -1

		self.ui = Ui_SymbolWindow()
		self.ui.setupUi(self)
		
		self.ui.importButton.clicked.connect(self.on_import_clicked)
		self.ui.exportButton.clicked.connect(self.on_export_clicked)
		self.ui.okButton.clicked.connect(self.accept)
		self.ui.cancelButton.clicked.connect(self.reject)
		self.ui.resetButton.clicked.connect(self.reset_working_list)

		self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
		self.ui.deleteButton.clicked.connect(self.delete_pair_from_list)

		self.ui.keyLineEdit.textEdited.connect(self.on_key_text_changed)
		self.ui.keyLineEdit.returnPressed.connect(self.on_kv_return_pressed)

		self.ui.valueLineEdit.textEdited.connect(self.on_value_text_changed)
		self.ui.valueLineEdit.returnPressed.connect(self.on_kv_return_pressed)

		self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)


	""" Editor State Getters """

	def is_row_selected(self):
		return self._selected_row > 0

	def is_key_valid(self):
		return bool(self.ui.keyLineEdit.text())

	def is_val_valid(self):
		return bool(self.ui.valueLineEdit.text())

	def can_val_be_added(self):
		""" 
		Checks if the current text in valueLineEdit can be added to the working list. Returns True if that text
		is different than the value of the currently selected key-value pair or if no key-value pair is selected.
		"""
		if not self.is_row_selected(): 
			return True
		old = self._working_list[self._selected_row][1]
		new = self.ui.valueLineEdit.text()
		return old != new


	""" UI Update Utility Functions """

	def _on_row_selected(self, row, enable_add_replace):
		""" 
		Called when a row in the tableView is selected, which occurs either A) when the user types a string
		into keyLineEdit that matches an existing key or B) when the user clicks on a cell in the tableView. 

		Changes addReplaceButton to replace mode and enables the delete command. In scenario A addReplaceButton
		may be enabled if the text in valueLineEdit is different (so that users may replace the existing entry),
		but in scenario B addReplaceButton should NOT be enabled since both keyLineEdit and valueLineEdit are
		updated to cell contents.
		"""
		if self._selected_row == -1:
			self.ui.addReplaceButton.setText("Replace")
			self.ui.addReplaceButton.clicked.disconnect(self.add_pair_to_list)
			self.ui.addReplaceButton.clicked.connect(self.replace_pair_in_list)

		self.ui.addReplaceButton.setEnabled(enable_add_replace)
		self.ui.deleteButton.setEnabled(True)
		self._selected_row = row

	def _on_row_deselected(self, enable_add_replace):
		""" 
		Called when a row in the tableView is deselected, which occurs either A) when the user types a string
		into keyLineEdit that doesn't match any existing keys or B) when the working list is somehow otherwise
		updated. 

		Changes addReplaceButton to add mode and disables the delete command. In scenario A addReplaceButton
		may be enabled if the text in valueLineEdit is different (so that users may add a new entry), but in
		scenario B addReplaceButton should NOT be enabled since both keyLineEdit and valueLineEdit will be reset.
		"""
		if self._selected_row != -1:
			self.ui.addReplaceButton.setText("Add")
			self.ui.addReplaceButton.clicked.disconnect(self.replace_pair_in_list)
			self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
			
		self.ui.addReplaceButton.setEnabled(enable_add_replace)
		self.ui.deleteButton.setEnabled(False)
		self._selected_row = -1

	def _on_working_list_updated(self):
		""" 
		Called when the working list is updated. Clears keyLineEdit, valueLineEdit, and deselects any selected 
		rows in the tableView. 
		"""
		self.ui.keyLineEdit.setText("")
		self.ui.valueLineEdit.setText("")

		self._on_row_deselected(False)
		self._check_table_widget_integrity()

	def _reload_view(self):
		""" Reloads the entire editor and populates it with the working list. """
		self.ui.tableWidget.clear()

		count = 0
		for k, v in self._working_list:
			self.ui.tableWidget.insertRow(count)
			self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(k))
			self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(v))
			count += 1

		self.ui.tableWidget.setRowCount(count)	
		self._on_working_list_updated()
	

	""" UI Listeners """

	def on_key_text_changed(self, current_text):
		""" 
		Called when the text in keyLineEdit is changed. First scrolls the tableWidget to the closest
		row as CURRENT_TEXT, then updates the tableWidget selection, addReplaceButton, and deleteButton
		depending on the values in keyLineEdit and valueLineEdit.
		"""
		found, idx = self._find_prospective_index(current_text)
		if len(self._working_list) > 0:
			# scroll to last row if current_text would be placed after the last row of tableView
			idx = min(idx, self.ui.tableWidget.rowCount() - 1)

			item = self.ui.tableWidget.item(idx, 0)
			self.ui.tableWidget.scrollToItem(item, QAbstractItemView.PositionAtTop)

		if not self.is_key_valid():
			self._on_row_deselected(False)
		else:
			enable_add_replace = self.is_val_valid() and self.can_val_be_added()
			if found:
				self._on_row_selected(idx, enable_add_replace)
			else:
				self._on_row_deselected(enable_add_replace)

	def on_value_text_changed(self, current_text):
		""" 
		Called when the text in valueLineEdit is changed. Enables or disables addReplaceButton depending
		on the values in keyLineEdit and valueLineEdit. 
		"""
		enable_btn = self.is_val_valid() and self.is_key_valid() and self.can_val_be_added()
		self.ui.addReplaceButton.setEnabled(enable_btn)

	def on_kv_return_pressed(self):
		""" 
		Called when the Enter key is pressed while either keyLineEdit or valueLineEdit has focus, and behaves as if 
		addReplaceButton was clicked. If addReplaceButton cannot be clicked, do nothing.
		"""
		if self.is_key_valid() and self.is_val_valid() and self.can_val_be_added():
			if self.is_row_selected():
				self.replace_pair_in_list()
			else:
				self.add_pair_to_list()

	def on_cell_clicked(self, row, col):
		""" 
		When a cell in the tableWidget is clicked, update keyLineEdit, valueLineEdit, and tableWidget to 
		select that key-value pair. 
		"""
		self.ui.keyLineEdit.setText(self.ui.tableWidget.item(row, 0).text())
		self.ui.valueLineEdit.setText(self.ui.tableWidget.item(row, 1).text())
		self._on_row_selected(row, False)


	""" 
	Opening / Closing Editor 

	The SymbolManager's symbol list is updated ONLY during this time if accept() is called.
	"""

	def open(self):
		""" Opens the editor and sets up the UI. """
		super(SymbolWindow, self).open()
		self._working_list = self._sym_manager.get_copy()
		self._reload_view()

	def accept(self):
		""" Saves changes if possible, then closes the editor. """
		conflicts = self._sym_manager.update_symbol_list(self._working_list)
		if conflicts:
			err_str = "Error: The following key conflicts were detected. Changes will not be saved.\n\n"
			for k1, k2 in conflicts:
				err_str += "'%s' and '%s'\n" % (k1, k2)
			aqt.utils.showInfo(err_str)
		super(SymbolWindow, self).accept()

	def reject(self):
		""" Closes the editor without saving. """
		old_list = self._sym_manager.get_copy()

		if old_list != self._working_list:
			confirm_msg = "Close without saving?"
			reply = QMessageBox.question(self, 'Message', confirm_msg, QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.Yes:
				super(SymbolWindow, self).reject()
		else:
			super(SymbolWindow, self).reject()


	""" 
	Working List Update Functions. 

	These functions update the editor's working list, but do NOT modify the Symbol Manager's symbol list. 
	Will also update the UI.
	"""

	def _find_prospective_index(self, key):
		""" 
		Checks if the given key exists in the working list. If it does, returns the index where the key 
		can be found. If it does not, returns the index where the key would be inserted.

		@return: (key_exists, index)
		"""
		low, high = 0, len(self._working_list) - 1
		mid = 0

		while low <= high:
			mid = (low + high) / 2
			k = self._working_list[mid][0]

			if key == k:
				return (True, mid)
			elif k < key:
				low = mid + 1
				mid += 1
			else:
				high = mid - 1
		return (False, mid)

	def add_pair_to_list(self):
		""" Adds an entry to the working list, performs validation, and updates the UI. """
		if self.is_row_selected():
			aqt.utils.showInfo("Error: Cannot add entry when a row is already selected.")
			return

		new_key = self.ui.keyLineEdit.text()
		new_val = self.ui.valueLineEdit.text()

		conflict_key = self._check_key_for_conflict(new_key, self._working_list)
		if conflict_key:
			aqt.utils.showInfo("Error: Cannot add '%s' as it conflicts with existing key '%s'. Please try a different name." 
				% (new_key, conflict_key))
			return

		(_, idx) = self._find_prospective_index(new_key)
		self._working_list.insert(idx, (new_key, new_val))

		self.ui.tableWidget.insertRow(idx)
		self.ui.tableWidget.setItem(idx, 0, QTableWidgetItem(new_key))
		self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem(new_val))
		self._on_working_list_updated()

	def replace_pair_in_list(self):
		""" Replaces an existing key-value pair from the working list. """
		if not self.is_row_selected():
			aqt.utils.showInfo("Error: Cannot replace when no valid row selected.")
			return

		new_val = self.ui.valueLineEdit.text()
		old_pair = self._working_list[self._selected_row]

		self._working_list[self._selected_row] = (old_pair[0], new_val)

		widget_item = self.ui.tableWidget.item(self._selected_row, 1)
		widget_item.setText(new_val)
		self._on_working_list_updated()

	def delete_pair_from_list(self):
		""" Deletes an existing key-value pair from the working list. """
		if not self.is_row_selected():
			aqt.utils.showInfo("Error: Cannot delete when no valid row selected.")
			return

		del self._working_list[self._selected_row]

		self.ui.tableWidget.removeRow(self._selected_row)
		self._on_working_list_updated()

	def reset_working_list(self):
		""" Resets the working list to the default symbol list. """
		confirm_msg = "Load default symbols? This will delete any unsaved changes!"
		reply = QMessageBox.question(self, 'Message', confirm_msg, QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self._working_list = self._sym_manager.get_default_list()
			self._reload_view()


	""" Import / Export Functions """

	def on_import_clicked(self):
		""" 
		Imports key-value pairs from a .txt file into the editor. The import procedure is successful only if 
		each and every entry in the .txt file is valid; otherwise, an error will be displayed and the operation
		will abort.
		"""
		fname = QFileDialog.getOpenFileName(self, 'Open file', '', "Text (*.txt)")
		if fname != "":
			with io.open(fname, 'r', encoding='utf8') as file:
				new_list = []
				i = 1
				for line in file:
					words = line.split()
					if not self._validate_imported_line(i, new_list, words):
						return
					new_list.append(tuple(words))
					i += 1

				new_list = sorted(new_list, key=lambda x: x[0])
				self._working_list = new_list
				self._reload_view()

	def _validate_imported_line(self, line_num, kv_list, words):
		""" 
		Checks that a line in the imported symbol .txt file is in the correct format, and that there are 
		no conflicts between keys. 
		"""
		if len(words) != 2:
			aqt.utils.showInfo("Error in line %d: incorrect format. Expecting '<key> <value>'." % line_num)
			return False

		conflict_key = self._check_key_for_conflict(words[0], kv_list)
		if conflict_key:
			aqt.utils.showInfo("Error in line %d: '%s' conflicts with existing key '%s'. The list will not be imported." 
				% (line_num, words[0], conflict_key))
			return False
		return True

	def on_export_clicked(self):
		""" 
		Exports the current symbol list into a .txt file. Before exporting, the list displayed in the 
		editor must match the symbol list stored in the system. 
		"""
		old_list = self._sym_manager.get_copy()

		if old_list != self._working_list:
			aqt.utils.showInfo("Please save changes first before exporting list.")
			return

		fname = QFileDialog.getSaveFileName(self, 'Save file', '', "Text (*.txt)")
		if fname != "":
			with io.open(fname, 'w', encoding='utf-8') as file:
				for k, v in self._working_list:
					file.write("%s\t%s\n" % (k, v))
				aqt.utils.showInfo("Symbol list written to: " + fname)


	""" Validation Functions """

	def _check_key_for_conflict(self, new_key, kv_list):
		""" 
		Checks to see if the new key would conflict with any existing key-value pairs during runtime. No keys should
		be substrings of each other. For example, a key of 'AAA' would prevent '/AAABC' from ever being used.

		@param kv_list: A list of key, value pairs.
		@return: Returns the first conflicting key, or None if no conflicts.
		"""
		for k, v in kv_list:
			if k in new_key or new_key in k:
				return k
		return None

	def _check_table_widget_integrity(self):
		""" Checks that the tableWidget displays the same items in the same order as the working list. """
		wl_len = len(self._working_list)
		tw_len = self.ui.tableWidget.rowCount()

		# Checks that the tableWidget has the same # of entries as the working list:
		if wl_len != tw_len:
			aqt.utils.showInfo("Error: working list length %d does not match tableWidget length %d." % (wl_len, tw_len))
			return

		# Checks that each entry in the tableWidget matches each entry of the working list:
		for i in range(wl_len):
			tw_k = self.ui.tableWidget.item(i, 0).text()
			tw_v = self.ui.tableWidget.item(i, 1).text()

			l_k = self._working_list[i][0]
			l_v = self._working_list[i][1]

			k_match = (tw_k == l_k)
			v_match = (tw_v == l_v)

			if not k_match or not v_match:
				err_str = "Error: kv pair at row %d does not match.\nList: %s, %s\nWidget: %s, %s" % (i, l_k, l_v, tw_k, tw_v)
				aqt.utils.showInfo(err_str)
				return

		# Checks that the tableWidget is displaying entries in alphabetical order by key:
		sorted_list = sorted(self._working_list, key=lambda x: x[0])
		has_error = False
		err_str = ""

		for i in range(wl_len):
			l_k = self._working_list[i][0]
			s_k = sorted_list[i][0]

			if l_k != s_k:
				has_error = True
				err_str += "at row %d key is %s, but should be %s\n" % (i, l_k, s_k)

		if has_error:
			aqt.utils.showInfo("Error: list not alphabetical:" + err_str)
