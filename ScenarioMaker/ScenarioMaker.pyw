"""
Tool for authoring HOBL test cases.
"""


# Imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PyQt6 import QtWidgets, QtGui, QtCore
import pywinstyles
import main_window as mainwin
import remote as remote
from settings import SettingsData

def main():
    os.environ['QT_QPA_PLATFORM'] = "windows:darkmode=1"
    # Load settings
    settings_data = SettingsData()
    # data_directory = settings["data_directory"]
    config_file = settings_data.get("config_file")

    app = QtWidgets.QApplication(sys.argv)
    app.setStyle('Fusion')

    main_window = mainwin.MainWindow(app, settings_data) 
    # main_window = mainwin.MainWindow(app) 

    pywinstyles.apply_style(main_window, "normal")
    # pywinstyles.change_header_color(main_window, color="#303030")
    main_window.setWindowIcon(QtGui.QIcon('images/logo.png'))

    main_window.show()
    main_window.raise_()

    # remote_thread = remote.RemoteThread(main_window)
    # remote_thread.start()

    app.exec()

    # remote_thread.stop()
    # remote_thread.join()

    print("Application Closed \n")


if __name__ == "__main__":
    main()
