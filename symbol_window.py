# Controller for Ui_SymbolWindow. GUI that lets users to edit the symbol list.

# TODO:
# - documentation
# - symbol display bug
# - issues with scrolling

import aqt

from PyQt4 import QtGui
from PyQt4.QtGui import QTableWidgetItem, QMessageBox, QAbstractItemView, QFileDialog

from symbol_manager import SymbolManager
from Ui_SymbolWindow import Ui_SymbolWindow

class SymbolWindow(QtGui.QDialog):

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
		self.ui.resetButton.clicked.connect(self.on_reset_clicked)

		self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
		self.ui.deleteButton.clicked.connect(self.delete_pair_from_list)

		self.ui.keyLineEdit.textEdited.connect(self.on_key_text_changed)
		self.ui.keyLineEdit.returnPressed.connect(self.on_kv_return_pressed)

		self.ui.valueLineEdit.textEdited.connect(self.on_value_text_changed)
		self.ui.valueLineEdit.returnPressed.connect(self.on_kv_return_pressed)

		self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)

	def _reload_view(self):
		self.ui.tableWidget.clear()

		count = 0
		for k, v in self._working_list:
			self.ui.tableWidget.insertRow(count)
			self.ui.tableWidget.setItem(count, 0, QTableWidgetItem(k))
			self.ui.tableWidget.setItem(count, 1, QTableWidgetItem(v))
			count += 1
		self.ui.tableWidget.setRowCount(count)

		self.set_key_line_text("")
		self.set_val_line_text("")

		self._unselect_row()
		self.ui.addReplaceButton.setEnabled(False)
		self._check_integrity()

	def set_key_line_text(self, text):
		self._is_key_valid = bool(text)
		self.ui.keyLineEdit.setText(text)

	def set_val_line_text(self, text):
		self._is_val_valid = bool(text)
		self.ui.valueLineEdit.setText(text)

	# Opens window and sets up table
	def open(self):
		super(SymbolWindow, self).open()
		self._working_list = self._sym_manager.get_copy()
		self._reload_view()

	# Saves changes, then closes window
	def accept(self):
		self._sym_manager.update_symbol_list(self._working_list)
		super(SymbolWindow, self).accept()

	# Closes window without saving
	def reject(self):
		old_list = self._sym_manager.get_copy()

		if old_list != self._working_list:
			confirm_msg = "Close without saving?"
			reply = QMessageBox.question(self, 'Message', confirm_msg, QMessageBox.Yes, QMessageBox.No)
			if reply == QMessageBox.Yes:
				super(SymbolWindow, self).reject()
		else:
			super(SymbolWindow, self).reject()

	# Returns the index in which key would be inserted
	def _find_prospective_index(self, key):
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
		if self._selected_row != -1:
			aqt.utils.showInfo("Error: Adding when valid row is selected")
			return

		new_key = self.ui.keyLineEdit.text()
		new_val = self.ui.valueLineEdit.text()

		(_, idx) = self._find_prospective_index(new_key)
		if _:
			aqt.utils.showInfo("Error: Adding when existing key is found")
			return
		self._working_list.insert(idx, (new_key, new_val))

		self.ui.tableWidget.insertRow(idx)
		self.ui.tableWidget.setItem(idx, 0, QTableWidgetItem(new_key))
		self.ui.tableWidget.setItem(idx, 1, QTableWidgetItem(new_val))
		
		self.set_key_line_text("")
		self.set_val_line_text("")
		self._unselect_row()
		self.ui.addReplaceButton.setEnabled(False)
		self._check_integrity()

	def replace_pair_in_list(self):
		if self._selected_row < 0:
			aqt.utils.showInfo("Error: Replacing when no valid row selected")
			return

		new_val = self.ui.valueLineEdit.text()
		old_pair = self._working_list[self._selected_row]
		self._working_list[self._selected_row] = (old_pair[0], new_val)

		widget_item = self.ui.tableWidget.item(self._selected_row, 1)
		widget_item.setText(new_val)

		self.set_key_line_text("")
		self.set_val_line_text("")
		self._unselect_row()
		self.ui.addReplaceButton.setEnabled(False)
		self._check_integrity()

	def delete_pair_from_list(self):
		if self._selected_row < 0:
			aqt.utils.showInfo("Error: Deleting when no valid row selected")
			return

		del self._working_list[self._selected_row]
		self.ui.tableWidget.removeRow(self._selected_row)

		self.set_key_line_text("")
		self.set_val_line_text("")
		self._unselect_row()
		self.ui.addReplaceButton.setEnabled(False)
		self._check_integrity()

	def on_reset_clicked(self):
		confirm_msg = "Reset to defaults?"
		reply = QMessageBox.question(self, 'Message', confirm_msg, QMessageBox.Yes, QMessageBox.No)
		if reply == QMessageBox.Yes:
			self._working_list = self._sym_manager.get_default_list()
			self._reload_view()

	def on_import_clicked(self):
		fname = QFileDialog.getOpenFileName(self, 'Open file', '', "Text (*.txt)")

		new_list = []

		if fname != "":
			with open(fname, 'r') as file:
				i = 1
				for line in file:
					words = line.split()
					if not self._validate_key(new_list, words):
						return
					new_list.append(tuple(words))
					i += 1

		self._working_list = new_list
		self._reload_view()

	def _validate_key(self, kv_list, words):
		if len(words) != 2:
			aqt.utils.showInfo("Error in line %d: incorrect format. Expecting '<key> <value>'." % i)
			return False

		if self._key_already_exists(kv_list, words[0]):
			aqt.utils.showInfo("Error in line %d: key '%s' already exists." % (i, words[0]))
			return False
		return True

	def _key_already_exists(self, items, key):
		for k, v in items:
			if k == key:
				return True
		return False

	def on_export_clicked(self):
		old_list = self._sym_manager.get_copy()

		if old_list != self._working_list:
			aqt.utils.showInfo("Please save changes first before exporting list.")
			return

		fname = QFileDialog.getSaveFileName(self, 'Save file', '', "Text (*.txt)")
		if fname != "":
			with open(fname, 'w') as file:
				for k, v in self._working_list:
					file.write("%s\t%s\n" % (k, v))
				aqt.utils.showInfo("Symbol list written to:" + fname)
		
	def on_key_text_changed(self, current_text):
		self._is_key_valid = bool(current_text)

		(found, idx) = self._find_prospective_index(current_text)
		if len(self._working_list) > 0:
			item = self.ui.tableWidget.item(idx, 0)
			self.ui.tableWidget.scrollToItem(item, QAbstractItemView.PositionAtTop)

		if not self._is_key_valid:
			self._unselect_row()
			self.ui.addReplaceButton.setEnabled(False)
		else:
			if found:
				self._select_row(idx)
			else:
				self._unselect_row()

			cur_val = self._working_list[self._selected_row][1]
			new_val = self.ui.valueLineEdit.text()
			self.ui.addReplaceButton.setEnabled(self._is_val_valid and (new_val != cur_val))

	def on_value_text_changed(self, current_text):
		self._is_val_valid = bool(current_text)

		cur_val = self._working_list[self._selected_row][1]
		btn_enabled = self._is_val_valid and self._is_key_valid and (current_text != cur_val)
		self.ui.addReplaceButton.setEnabled(btn_enabled)

	def on_kv_return_pressed(self):
		if self._is_key_valid and self._is_val_valid:
			if self._selected_row == -1:
				self.add_pair_to_list()
			else:
				self.replace_pair_in_list()

	def on_cell_clicked(self, row, col):
		self.ui.keyLineEdit.setText(self.ui.tableWidget.item(row, 0).text())
		self.ui.valueLineEdit.setText(self.ui.tableWidget.item(row, 1).text())
		self._is_key_valid = True
		self._is_val_valid = True

		self._select_row(row)
		self.ui.addReplaceButton.setEnabled(False)

	def _select_row(self, row):
		if self._selected_row == -1:
			self.ui.addReplaceButton.clicked.disconnect(self.add_pair_to_list)
			self.ui.addReplaceButton.setText("Replace")
			self.ui.addReplaceButton.clicked.connect(self.replace_pair_in_list)
			self.ui.deleteButton.setEnabled(True)

		self._selected_row = row

	def _unselect_row(self):
		if self._selected_row != -1:
			self.ui.addReplaceButton.clicked.disconnect(self.replace_pair_in_list)
			self.ui.addReplaceButton.setText("Add")
			self.ui.addReplaceButton.clicked.connect(self.add_pair_to_list)
			self.ui.deleteButton.setEnabled(False)

		self._selected_row = -1

	def _check_integrity(self):
		list_len = len(self._working_list)
		tw_len = self.ui.tableWidget.rowCount()

		if list_len != tw_len:
			aqt.utils.showInfo("Error: working list length %d does not match tableWidget length %d" % (list_len, tw_len))
			return

		for i in range(list_len):
			tw_k = self.ui.tableWidget.item(i, 0).text()
			tw_v = self.ui.tableWidget.item(i, 1).text()

			l_k = self._working_list[i][0]
			l_v = self._working_list[i][1]

			k_match = (tw_k == l_k)
			v_match = (tw_v == l_v)

			if not k_match or not v_match:
				aqt.utils.showInfo("Error: kv pair at row %d does not match.\nList: %s, %s\nWidget: %s, %s" % (i, l_k, l_v, tw_k, tw_v))
				return

		sorted_list = sorted(self._working_list, key=lambda x: x[0])
		has_error = False
		err_str = ""

		for i in range(list_len):
			l_k = self._working_list[i][0]
			s_k = sorted_list[i][0]

			if l_k != s_k:
				has_error = True
				err_str += "at row %d key is %s, but should be %s\n" % (i, l_k, s_k)

		if has_error:
			aqt.utils.showInfo("Error: list not alphabetical:" + err_str)

