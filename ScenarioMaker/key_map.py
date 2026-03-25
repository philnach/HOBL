"""
Maps keys from Qt to Appium.
"""

from PyQt6.QtCore import Qt
import re

class KeyMap:
    map = {
        Qt.Key.Key_Backspace : ['\ue003', '<BACKSPACE>'],
        Qt.Key.Key_Tab : ['\ue004', '<TAB>'],
        Qt.Key.Key_Return : ['\ue007', '<ENTER>'],
        Qt.Key.Key_Shift : ['\ue008', '<SHIFT>'],
        Qt.Key.Key_Control : ['\ue009', '<CONTROL>'],
        Qt.Key.Key_Alt : ['\ue00a', '<ALT>'],
        Qt.Key.Key_Escape : ['\ue00c', '<ESC>'],
        Qt.Key.Key_Space : ['\ue00d', ' '],
        Qt.Key.Key_PageUp : ['\ue00e', '<PGUP>'],
        Qt.Key.Key_PageDown : ['\ue00f', '<PGDN>'],
        Qt.Key.Key_End : ['\ue010', '<END>'],
        Qt.Key.Key_Home : ['\ue011', '<HOME>'],
        Qt.Key.Key_Left : ['\ue012', '<LEFT>'],
        Qt.Key.Key_Up : ['\ue013', '<UP>'],
        Qt.Key.Key_Right : ['\ue014', '<RIGHT>'],
        Qt.Key.Key_Down : ['\ue015', '<DOWN>'],
        Qt.Key.Key_Delete : ['\ue017', '<DELETE>'],
        Qt.Key.Key_F1 : ['\ue031', '<F1>'],
        Qt.Key.Key_F2 : ['\ue032', '<F2>'],
        Qt.Key.Key_F3 : ['\ue033', '<F3>'],
        Qt.Key.Key_F4 : ['\ue034', '<F4>'],
        Qt.Key.Key_F5 : ['\ue035', '<F5>'],
        Qt.Key.Key_F6 : ['\ue036', '<F6>'],
        Qt.Key.Key_F7 : ['\ue037', '<F7>'],
        Qt.Key.Key_F8 : ['\ue038', '<F8>'],
        Qt.Key.Key_F9 : ['\ue039', '<F9>'],
        Qt.Key.Key_F10 : ['\ue03a', '<F10>'],
        Qt.Key.Key_Meta : ['\ue03d', '<WIN>'],
        Qt.Key.Key_F32 : ['\ue03e', '<FN>'] # Mac key
    }

    @staticmethod
    def QtToWDKey(qt_key):
        # Convert key code from PyQT to WebDriver (used by Input Inject)
        return KeyMap.map[qt_key][0]

    @staticmethod
    def WDToDisplayKey(wd_key):
        # Convert key code from WebDriver to human readable (for displaying in Edit dialog)
        for k in KeyMap.map:
            if KeyMap.map[k][0] == wd_key:
                return KeyMap.map[k][1]
        return wd_key

    @staticmethod
    def DisplayToWDKey(display_key):
        # Convert key code from WebDriver to human readable (for displaying in Edit dialog)
        for k in KeyMap.map:
            if KeyMap.map[k][1] == display_key:
                return KeyMap.map[k][0]
        return display_key 

    @staticmethod
    def WDToDisplayString(s):
        # Convert string from WebDriver to human readable (for displaying in Edit dialog)
        display_string = ""
        for c in s:
            display_string += KeyMap.WDToDisplayKey(c)
        return display_string

    @staticmethod
    def DisplayToWDString(original):
        # Convert string from WebDriver to human readable (for displaying in Edit dialog)
        if original == None:
            return None
        # Replace special characters in square brackets
        search_results = re.findall(r'\<\w+\>', original)
        for match in search_results:
            val = KeyMap.DisplayToWDKey(match)
            original = original.replace(match, val)
        # Replace spaces
        original = original.replace(' ', '\ue00d')
        return original


    @staticmethod
    def QtToDisplayKey(qt_key):
        # Convert key code from PyQT to WebDriver (used by Input Inject)
        return KeyMap.map[qt_key][1]

    @staticmethod
    def ContainsQtKey(qt_key):
        if qt_key in KeyMap.map:
            return True
        else:    
            return False
    