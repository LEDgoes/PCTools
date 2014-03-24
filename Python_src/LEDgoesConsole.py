'''
Welcome to the LEDgoes PC Tools!  This file features inialization of the fonts and UI.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesForm.py "C:\Users\Stephen\Documents\LEDgoes PC Interface.ui"

Requires pywin32 - http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/
Requires pil


Any assistance to make this code more "Pythonic" will be greatly welcome.
'''
# import things for this window
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import LEDgoesGlobals as globals
import json
# import the LEDgoes-specific GUI framework details
import LEDgoesConsoleForm
from LEDgoesConsoleForm import Ui_ConsoleWindow
# import things important for serial connections
import os


################################################################################
# Class definition for the QMainWindow object
################################################################################    
    
# This class represents our console window, and runs functions to initialize it
class ConsoleWindow(QMainWindow):

    updateText = pyqtSignal(str)

    def __init__(self):
        super(ConsoleWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_ConsoleWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QIcon('LEDgoes-Icon.ico'))
        
        # Set up a monitor so things running in other threads can write to the console too
        self.updateText.connect(_updateConsoleText)


################################################################################
# Function definitions for this module
################################################################################    

def openConsole():
    globals.cw = ConsoleWindow()
    globals.cw.show()

def _updateConsoleText(str):
    try:
        globals.cw.ui.txtConsole.setPlainText(globals.cw.ui.txtConsole.toPlainText() + "\n" + str.decode("latin_1"))
        globals.cw.ui.txtConsole.verticalScrollBar().setValue(globals.cw.ui.txtConsole.verticalScrollBar().maximum())
    except Exception as e:
        print e

def cwrite(str):
    print str
    try:
        globals.cw.updateText.emit(str)
    except Exception as e:
        pass
