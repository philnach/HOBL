"""
Creates the Settings dialog.
"""


from PyQt6 import QtWidgets, uic
from PyQt6.QtCore import QSettings

settings_form, settings_base = uic.loadUiType("settings.ui")

class SettingsData():
    registry_path = "HKEY_CURRENT_USER\\Software\\Microsoft\\HOBLCreate"

    def __init__(self):
        return

    @classmethod
    def get(self, parameter, default_val=""):
        qsettings = QSettings(self.registry_path, QSettings.Format.NativeFormat)
        qsettings.setFallbacksEnabled(False)
        return qsettings.value(parameter, default_val)

    @classmethod
    def set(self, parameter, value):
        qsettings = QSettings(self.registry_path, QSettings.Format.NativeFormat)
        qsettings.setFallbacksEnabled(False)
        qsettings.setValue(parameter, value)


class SettingsWindow(QtWidgets.QDialog, settings_form):
    def __init__(self, app, settings_data, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent=parent)
        self.ui = settings_form()
        self.ui.setupUi(self)
        self.settings = settings_data

        self.ui.dutIpLineEdit.setText(self.settings.get("dut_ip"))
        self.ui.defaultDelaySpinBox.setValue(int(self.settings.get("default_delay", 2)))
        self.ui.captureDelaySpinBox.setValue(float(self.settings.get("capture_delay", 0.5)))
        self.ui.authorLineEdit.setText(self.settings.get("author"))
        self.ui.deviceLineEdit.setText(self.settings.get("device"))

    def accept(self):
        self.settings.set('dut_ip', self.ui.dutIpLineEdit.text())
        self.settings.set('default_delay', self.ui.defaultDelaySpinBox.value())
        self.settings.set('capture_delay', self.ui.captureDelaySpinBox.value())
        self.settings.set('author', self.ui.authorLineEdit.text())
        self.settings.set('device', self.ui.deviceLineEdit.text())
        super().accept()

    def reject(self):
        super().reject()
           

