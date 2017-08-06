
from PyQt4 import QtGui

class SymbolWindow(object):

	def __init__(self, editor, parent_window):
		self.editor = editor
		self.parent_window = parent_window

	def open(self):
		dialog = QtGui.QDialog(self.parent_window)
		form = QtGui.QFormLayout()

		dialog.setLayout(form)
		dialog.exec_()

