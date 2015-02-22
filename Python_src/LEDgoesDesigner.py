'''
Welcome to the LEDgoes PC Tools!  This file features inialization of the font & custom layout designer.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesDesignerForm.py "C:\Users\Stephen\Documents\LEDgoes Designer.ui"

Requires pywin32 - http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/


Any assistance to make this code more "Pythonic" will be greatly welcome.
'''
# import things for this window
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebKitWidgets import QWebPage
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
# Why the hell do I need Network sockets, SSL, and printer support just to view a local HTML file?!
from PyQt5 import QtNetwork, QtWebKit, QtPrintSupport
import LEDgoesGlobals as globals
# import the LEDgoes-specific GUI framework details
import LEDgoesDesignerForm
from LEDgoesDesignerForm import Ui_DesignerWindow
# import deque so we can make globals.boards correctly
from collections import deque


################################################################################
# Class definition for the QMainWindow object
################################################################################    
    
# This class represents our Designer window, and runs functions to initialize it
class DesignerWindow(QMainWindow):

    def __init__(self):
        super(DesignerWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_DesignerWindow()
        self.ui.setupUi(self)
        # Load the content from the file -- relative paths don't seem to work in Qt
        f = open('LEDgoesDrawingTool.html', 'r')
        html = f.read()
        self.ui.webView.setHtml(html)
        #self.setWindowIcon(QIcon('LEDgoes-Icon.ico'))

        # Set listeners
        self.ui.actionAbout_LEDgoes_PC_Interface.toggled.connect(self.showAbout)
        
        # Set up a monitor so things running in other threads can write to the Designer too
        self.ui.webView.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.ui.webView.linkClicked.connect(self.reactToLinkClicked)
        
    def reactToLinkClicked(self, link):
        print "Link clicked: ", link
        # Get rid of the extra class identifier stuff that __str__() puts on
        link = link.__str__()[20:-2]
        if not "action://done_creating_layout/" in link:
            console.cwrite("Invalid link returned from the Designer.")
            return
        # Get rid of the main part of the URI
        link = link[30:]
        # Convert the returned data into a deque of tuples
        globals.boards = deque([tuple([int(s) for s in x.split(",")]) for x in link.split(";")])

    def showAbout(self, event):
        print "LEDgoes Designer v1.0\nCopyleft 2013-14 OpenBrite, LLC\n\nSee our GitHub repository at https://github.com/ledgoes/"


################################################################################
# Function definitions for this module
################################################################################    

def openDesigner():
    globals.dw = DesignerWindow()
    globals.dw.show()
