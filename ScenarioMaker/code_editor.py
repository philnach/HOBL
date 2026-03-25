"""
Opens Python code editor widget.
"""

from qtpy.QtWidgets import QApplication
from pyqcodeeditor.QCodeEditor import QCodeEditor
from pyqcodeeditor.highlighters import QPythonHighlighter
from pyqcodeeditor.completers import QPythonCompleter
import os

class CodeEditorWindow(QCodeEditor):
    def __init__(self, app, file_path, parent=None):
        super().__init__()
        self.file_path = file_path
        self.setCompleter(QPythonCompleter())
        self.setHighlighter(QPythonHighlighter())
        self.resize(800, 600)
        if os.path.exists(file_path):
            # Open existing file
            print(f"Opening code block from: {file_path}")
            with open(file_path) as file:
                content = file.read()
                self.setPlainText(content)
        else:
            # Create new file
            file_name = os.path.basename(file_path)
            self.setPlainText(f"import logging\n\ndef run(scenario):\n    logging.debug('Executing code block: {file_name}')")


    def closeEvent(self, event):
        # self.settings.set('size', self.size())
        # self.settings.set('pos', self.pos())
        with open(self.file_path, 'w') as file:
            file.write(self.toPlainText())
        print(f"Saving code block to: {self.file_path}")
        event.accept()
