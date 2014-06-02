'''
Welcome to the LEDgoes PC Tools!  This file features inialization of the fonts and UI.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesForm.py "C:\Users\Stephen\Documents\LEDgoes PC Interface.ui"

Requires pywin32 - http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/
Requires pil
Twitter dependencies:  (pip install python-twitter)
    Requires Python-Twitter - http://code.google.com/p/python-twitter/
        Python-Twitter requires http://cheeseshop.python.org/pypi/simplejson
        Python-Twitter requires http://code.google.com/p/httplib2/
        Python-Twitter requires http://github.com/simplegeo/python-oauth2


Any assistance to make this code more "Pythonic" will be greatly welcome.
'''
# import things for the application & the GUI framework
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import LEDgoesGlobals as globals
import json
# import the LEDgoes-specific GUI framework details
import LEDgoesForm
from LEDgoesForm import Ui_MainWindow
# import things important for serial connections
import os
import serial
# find ports among the different operating systems
from serial.tools import list_ports     # Linux
import win32file                        # Windows
import re                               # In Windows, we need to search for "COM\d", thus we need regex support
# import this to help find fonts
import glob
# Import the signal module so we can listen for when the user hits Ctrl+C
import signal
# Import the window used for helping debug the marquee & the software
import LEDgoesConsole as console
# Import default text tools
import LEDgoesScrollingText as scroll
# Import image tools, including external & internal libraries
from PIL import Image
import LEDgoesImageRoutines as ImRts
# Import Twitter tools, including external & internal libraries
import twitter
import LEDgoesTwitter
# Import the derived class for raw text list items
from LEDgoesRawTextItem import RawTextItem

################################################################################
# Step 1. Define the QApplication so we can start building GUI widgets
################################################################################

app = QApplication(sys.argv)	    
app.setWindowIcon(QIcon('LEDgoes-Icon.ico'))

################################################################################
# Step 2. Define the signal handler "KeyboardInterrupt" so the user can exit the app with Ctrl+C
################################################################################

# TODO: Not working. Fix.
def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

################################################################################
# Step 3. Define the serial thread routine, since evidently I can't put this in a separate file w/o circular dependencies
################################################################################
# import deque from collections since it should be faster than using a standard list
from collections import deque
# import the capability to pause the thread so we don't go off the rails scrolling as fast as possible
from time import sleep
# import threading so our I/O isn't on the UI thread
import threading

                    
################################################################################
# Step 3. Define important variables & functions & import user-defined modules
################################################################################

globals.evt.set()         # Standard Python events allow threads to continue running if event flag is set
activeConns = 0           # How many active serial connections are going on
outputThread = None       # Reference to thread running the serial IO code for scrolling text
animationThread = None    # Reference to thread running the serial IO code for animations
baudRates = ["9600", "14400", "19200", "28800", "38400", "57600", "76800", "115200",
"200000", "250000", "500000", "1000000"]
baudRateIdx = 0           # Index of the baud rate we're running at (w.r.t. baudRates)
prevBaudRate = "9600"     # If the user resets the baud rate, store it here in case they change it again

# Import other modules & methods

def serialWelcome(welcomeType):
    global outputThread, animationThread, prevBaudRate
    if not globals.boards:       # if globals.boards is empty,
        _updateBoards(2)         # populate it
    globals.delay = mw.ui.spinUpdateDelay.value() * 0.001
    # At 9600 baud, adjust each board's baud rate to conform to the user's wishes (just in case some were reset)
    if baudRateIdx != 0:
        serialMsg = "\xFF%s" % chr(0x90 + baudRateIdx)
        serialSendEx("Sending %s at 9600 baud to change baud rate" % serialMsg, serialMsg, 1)
        sleep(1.2)
    globals.cxn1.close()
    if baudRates[baudRateIdx] != prevBaudRate and prevBaudRate != "9600":
        # the user adjusted the serial rate before, so talk to the boards at their current rate
        globals.cxn1.baudrate = int(prevBaudRate)
        globals.cxn1.open()
        serialMsg = "\xFF%s" % chr(0x90 + baudRateIdx)
        debugMsg = "\nSending %s at %s baud to change baud rate" % (serialMsg, baudRates[baudRateIdx])
        serialSendEx(debugMsg, serialMsg, 1)
        prevBaudRate = baudRates[baudRateIdx]
        sleep(1.2)
        globals.cxn1.close()
    
    # Now actually re-open this program's serial connection in the user's desired speed
    globals.cxn1.baudrate = int(baudRates[baudRateIdx])
    console.cwrite(globals.cxn1.baudrate)
    globals.cxn1.open()
    # Send the serial commands to adjust any board IDs that might be one too low
    if len(globals.boards) < 33:    # Only do this when 32 boards or less are in use
        tmp = list(globals.boards)
        increments = [x - 1 for x in tmp[1:]]
        for boardID in increments:
            serialSendEx("", "\xFF\x82" + chr(boardID + 128), 0.001)
            serialSendEx("", "\xFF\x82" + chr(boardID + 192), 0.001)
    # Start a thread
    if welcomeType == "scroll":
        outputThread = scroll.serialThread()
        outputThread.start()
    elif welcomeType == "animation":
        animationThread = ImRts.animationThread()
        animationThread.start()

################################################################################
# Step 4. Load all user-defined fonts
################################################################################

# Look for all .ledfont files in the current working directory
console.cwrite("\nLoading fonts...")
fontWarningsEnabled = True
for filename in glob.glob("*.ledfont"):
    try:
        # Debug: Print the filename
        console.cwrite(filename)
        # Load the font into memory
        fontfile = open(filename, 'r')
        font = fontfile.read()
        fontfile.close()
        fontjson = json.loads(font)
        globals.font[fontjson['name']] = fontjson
    except Exception as e:
        console.cwrite("Error loading font %s" % filename)
        if fontWarningsEnabled:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("LEDgoes PC Interface")
            msgBox.setText("Error parsing font")
            msgBox.setInformativeText("There appears to be a syntax error in font file %s, and it has not been loaded.  Press OK to continue, or Ignore to continue and suppress future messages of this type." % filename)
            msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Ignore)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.setIcon(QMessageBox.Warning)
            ret = msgBox.exec_()
            if ret == QMessageBox.Ignore:
                fontWarningsEnabled = False
    
#print "\nFont set:"
#print globals.font

# Die if there are no fonts
if len(globals.font) == 0:
    msgBox = QMessageBox()
    msgBox.setWindowTitle("LEDgoes PC Interface")
    msgBox.setText("Fatal error; cannot start")
    msgBox.setInformativeText("No fonts were successfully loaded from the working directory of LEDgoes PC Interface.  Font files (*.ledfont) can be downloaded from http://www.ledgoes.com.")
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setDefaultButton(QMessageBox.Ok)
    msgBox.setIcon(QMessageBox.Critical)
    ret = msgBox.exec_()
    sys.exit(0)

# This function finds the name of all serial ports and adds them to our lists
def serial_ports(mainWindow):
    console.cwrite("\nScanning for serial ports...")
    if os.name == 'nt':
        # windows
        #for i in range(256):
        #    try:
        #        s = serial.Serial(i)
        #        mainWindow.ui.selRow1COM.addItem("COM" + str(i + 1))
        #        mainWindow.ui.selRow2COM.addItem("COM" + str(i + 1))
        #        s.close()
        #    except serial.SerialException as ex:
        #        pass
		comPorts = [device for device in win32file.QueryDosDevice(None).split("\x00") if re.search("^COM\d+$", device)]
		comPorts.sort()
		[mainWindow.ui.selRow1COM.addItem(comPort) for comPort in comPorts]
		[mainWindow.ui.selRow2COM.addItem(comPort) for comPort in comPorts]
    else:
        # unix
        for port in list_ports.comports():
	    console.cwrite("TODO: Add this to the list: " + port[0])
    
def serialSendEx(debugMsg, serialMsg, delay):
    global outputThread
    #console.cwrite(debugMsg + " " + serialMsg)
    console.cwrite(debugMsg)
    try:
        if outputThread.isAlive():
            # If the output thread is alive, let that thread handle the IO
            # define the message: control mode flag FF, instruction 80, chip ID 80 (chip ID doesn't matter in this case)
            globals.evtDefinition = {'message': serialMsg, 'delay': delay}
            globals.evt.clear()      # clear the event flag to indicate it should branch before further updates
        else:
            # Raise an exception so we send the commands over serial anyway
            raise
    except:
        console.cwrite("Output thread is dead.  Will now open serial port manually.")
        try:
            globals.cxn1.write(serialMsg)
        except Exception as ex:
            #print "Error writing to the selected port; perhaps it is closed.  Will try opening it.  Details:", ex
            # TODO FIXME: Port name should be determined from an array of rowNum -> COM port
            try:
                cxn = serial.Serial(mw.ui.selRow1COM.currentText())
                cxn.write(serialMsg)
            except Exception as ex:
                console.cwrite("There was a problem opening the selected port (%s) and writing the desired message.  Please make sure you have a working COM port selected.\n" % mw.ui.selRow1COM.currentText())
                console.cwrite("Details:", ex)
                cxn.close()
                return
            console.cwrite("Finished writing the desired message.\n")
            cxn.close()
        
def _updateBoards(numBoards):
    globals.boards.clear()              # empty the list of board indexes
    #globals.boards.extend(range(0, 32))
    delta = 1024 / numBoards            # the auto-address line on each board should be equal to (1024 / # boards) * i
    for i in range(0, numBoards):
        globals.boards.extend([int( delta * i / 16 )])

def isValidBoardAddress(inputContainer):
    number = 0
    # if the number is False, return 0
    if inputContainer.toPlainText() is False:
        return 0
    try:                     # first, try the number in Base 10
        number = int(inputContainer.toPlainText())
    except ValueError:       # now try it in hex (Base 16)
        try:
            number = int(inputContainer.toPlainText(), 16)
        except:              # number is not valid in decimal or hex
            console.cwrite("Error: Address \"%s\" is not valid.  A board address is an integer ranging from 0 through 63; chip addresses exist from 128 through 255.\n" % inputContainer.toPlainText())
            return None
    except Exception as ex:  # something else besides a ValueError happened, so likely the input is garbage
        console.cwrite("There was a general error while making sure the chip address is numeric.  Details:", ex)
        return None
    if number >= 0 and number < 256:
        if number < 64 or number > 127:
            return number
    # If we're here, the chip ID is invalid
    console.cwrite("Error: Address \"%d\" is not valid.  Valid board addresses range from 0 through 63; valid chip addresses are 128 through 255.\n" % number)
    return None


# This class represents our main window, and runs functions to initialize it
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Make some local modifications.
        [self.ui.selSpeed.addItem(rate) for rate in baudRates]
        self.ui.txtMessage.setTextColor(Qt.GlobalColor(18))
        
        # Set up particular globals variables with their values from the UI, in case anyone changes the default values
        globals.delay = self.ui.spinUpdateDelay.value() * 0.001
        globals.msgLimit = self.ui.spinMsgLimit.value()
        globals.uiMsgList = self.ui.rawTextList

        # Connect up the UI elements to event listeners.
        # Main panels on top
        self.ui.selSpeed.activated.connect(self.updateSpeed)
        self.ui.btnConnectRow1.clicked[()].connect(lambda row=1: self.toggleRow(row))
        self.ui.btnConnectRow2.clicked[()].connect(lambda row=2: self.toggleRow(row))
        self.ui.btnOpenConsole.clicked.connect(self.openConsole)
        self.ui.spinUpdateDelay.valueChanged.connect(self.updateDelay)
        self.ui.spinPanelsPerRow.valueChanged.connect(self.updateBoards)
        # Raw Text panel
        self.ui.btnDeleteRawText.clicked.connect(self.deleteMessage)
        self.ui.btnInsertRawTextBefore.clicked[()].connect(lambda direction=0: self.insertMessage(direction))
        self.ui.btnInsertRawTextAfter.clicked[()].connect(lambda direction=1: self.insertMessage(direction))
        self.ui.spinMsgLimit.valueChanged.connect(self.updateMsgLimit)
        self.ui.btnGreen.clicked.connect(self.setGreen)
        self.ui.btnRed.clicked.connect(self.setRed)
        self.ui.btnYellow.clicked.connect(self.setYellow)
        self.ui.btnPush.clicked.connect(self.pushMessage)
        # Twitter Feed panel
        self.ui.btnTwitterAuth.clicked.connect(self.twitterAuth)
        self.ui.btnTwitterStream.clicked.connect(self.twitterStream)
        # Animation panel
        self.ui.btnAnim.clicked.connect(self.showAnimation)
        # Firmware panel
        self.ui.btnShowTestPattern.clicked[()].connect(lambda idContainer=self.ui.txtTestOn: self.showTestPatternOn(idContainer))
        self.ui.btnStopGuessing.clicked[()].connect(lambda id=64: self.showTestPatternOn(id))
        self.ui.btnResetChipIDs.clicked.connect(self.resetChipIDs)
        self.ui.btnIncrementChipID.clicked[()].connect(lambda idContainer=self.ui.txtChipIDIncr: self.excrementChipID(idContainer, 1))
        self.ui.btnDecrementChipID.clicked[()].connect(lambda idContainer=self.ui.txtChipIDDecr: self.excrementChipID(idContainer, -1))
        self.ui.btnSetChipID.clicked[()].connect(lambda oldIdContainer=self.ui.txtChipIDCurrent, newIdContainer=self.ui.txtChipIDDesired: self.setChipID(oldIdContainer, newIdContainer))
        self.ui.btnSaveChipID.clicked[()].connect(lambda idContainer=self.ui.txtSaveOn: self.saveChipID(idContainer))
        self.ui.btnSaveAllIDs.clicked.connect(self.saveAllIDs)
        self.ui.btnCompressChipIDs.clicked.connect(self.compressChipIDs)
        # Simulator panel
        # Baud Rate panel
        self.ui.spinBaudRatePanels.valueChanged.connect(self.updateTargetBaudRate)
        self.ui.spinBaudRateScrollRate.valueChanged.connect(self.updateTargetBaudRate)
    
    # @Override
    # Triggers when the main window is closed by the user.  Initiates graceful application shutdown.
    def closeEvent(self, event):
        global outputThread
        globals.exitFlag = True
        try:
            outputThread.join()
        except:
            pass
        globals.cxn1.close()
        globals.cxn2.close()
        sys.exit(0)
        
    def updateSpeed(self, speed):
        global baudRateIdx
        baudRateIdx = speed
        
    def toggleRow(self, rowNum):
        'When either of the connect/disconnect buttons are clicked, this method toggles the appropriate serial state'
        global activeConns, outputThread
        portName = str(self.ui.selRow1COM.currentText()) if (rowNum == 1) else str(self.ui.selRow2COM.currentText())
        
        # First, toggle the connection states
        if rowNum == 1:
            if globals.cxn1.isOpen():
                # Close an active connection
                globals.cxn1.close()
                activeConns -= 1
                self.ui.btnConnectRow1.setText("Connect")
            else:
                # Open a new connection at 9600 baud; we'll account for the user-defined baud rate in serialWelcome()
                globals.cxn1 = serial.Serial(portName, 9600)
                activeConns += 1
                self.ui.btnConnectRow1.setText("Disconnect")
        elif rowNum == 2:
            if globals.cxn2.isOpen():
                globals.cxn2.close()
                activeConns -= 1
                self.ui.btnConnectRow2.setText("Connect")
            else:
                globals.cxn1 = serial.Serial(portName)
                activeConns += 1
                self.ui.btnConnectRow2.setText("Disconnect")
                
        # Now, look to see if we have the required connections in place to start the matrix
        # Otherwise, stop the matrix
        
        # TODO: Don't assume we're using just one row
        if activeConns == 1:
            serialWelcome("scroll")
        elif activeConns == 0:
            globals.exitFlag = 1;
            try:
                console.cwrite("Stopping IO thread...")
                outputThread.join();
                globals.exitFlag = 0;
                outputThread = None;
                console.cwrite("IO thread stopped!")
            except AttributeError:
                console.cwrite("Thread was probably already stopped")

    def openConsole(self, event):
        console.openConsole()

    def updateDelay(self, event):
        globals.delay = event * 0.001

    def updateBoards(self, event):
        # event contains the number of boards the user says is in the matrix
        self.ui.spinBaudRatePanels.setValue(event)
        _updateBoards(event)

    def deleteMessage(self, event):
        # delete the message from the UI list
        for SelectedItem in self.ui.rawTextList.selectedItems():
            self.ui.rawTextList.takeItem(self.ui.rawTextList.row(SelectedItem))
        # Reconstruct the global list by pulling out "formattedText" from the UI list objects
        globals.richMsgs = [x.formattedText for x in self.ui.rawTextList.findItems('.*', Qt.MatchRegExp)]
        # If nothing's left, make sure we at least have the "Awaiting Messages" message to scroll
        if len(globals.richMsgs) == 0:
            globals.richMsgs = globals.initMsgs

    def insertMessage(self, direction):
        # Make the item
        item = RawTextItem(QIcon.fromTheme("edit-undo"), self.ui.txtMessage.toHtml(), None, 0)
        # Add it using the insertItem() function
        # TODO FIXME: If we ever support multi-select, this'll need to be examined closer
        for SelectedItem in self.ui.rawTextList.selectedItems():
            self.ui.rawTextList.insertItem(self.ui.rawTextList.row(SelectedItem) + direction, item)
        # Reconstruct the global list by pulling out "formattedText" from the UI list objects
        globals.richMsgs = [x.formattedText for x in self.ui.rawTextList.findItems('.*', Qt.MatchRegExp)]

    def updateMsgLimit(self, event):
        globals.msgLimit = event

    def setGreen(self, event):
        # Set the rich text editor to write in green and/or set selected text to green
        self.ui.txtMessage.setTextColor(Qt.GlobalColor(14))
        self.ui.txtMessage.setFocus()

    def setRed(self, event):
        # Set the rich text editor to write in red and/or set selected text to red
        self.ui.txtMessage.setTextColor(Qt.GlobalColor(7))
        self.ui.txtMessage.setFocus()

    def setYellow(self, event):
        # Set the rich text editor to write in yellow and/or set selected text to yellow
        self.ui.txtMessage.setTextColor(Qt.GlobalColor(18))
        self.ui.txtMessage.setFocus()

    def pushMessage(self, event):
        if self.ui.txtMessage.toPlainText() == "":
            msgBox = QMessageBox()
            msgBox.setWindowTitle("LEDgoes PC Interface")
            msgBox.setText("Error: No empty messages allowed")
            msgBox.setInformativeText("You cannot push an empty message onto the stack.")
            msgBox.setStandardButtons(QMessageBox.Ok)
            msgBox.setDefaultButton(QMessageBox.Ok)
            msgBox.setIcon(QMessageBox.Warning)
            ret = msgBox.exec_()
            return
        globals.pushMsg("raw-text", self.ui.txtMessage.toPlainText(), self.ui.txtMessage.toHtml(), self.ui.isSticky.isChecked())
        self.ui.txtMessage.setText("")

    def twitterAuth(self, event):
        global twitterApi
        twitterApi = LEDgoesTwitter.twitterAuth(
            self.ui.txtTwitterConsumerKey.toPlainText(),
            self.ui.txtTwitterConsumerSecret.toPlainText(),
            self.ui.txtTwitterTokenKey.toPlainText(),
            self.ui.txtTwitterTokenSecret.toPlainText()
        )
        if twitterApi is None:
            console.cwrite("Failed to store Twitter authentication credentials")
        else:
            console.cwrite("Authentication parameters stored successfully.  The credentials will be verified when you click on Start.")

    def twitterStream(self, event):
        twitterThreadIsOn = LEDgoesTwitter.twitterStream(self.ui.txtTwitterSearch.toPlainText())
        if twitterThreadIsOn:
            self.ui.btnTwitterStream.setText("Stop")
        else:
            self.ui.btnTwitterStream.setText("Start")

    def showAnimation(self, animFileContainer):
        path = self.ui.txtGIFPath.toPlainText()
        results = ImRts.analyzeImage(path)
        console.cwrite("Returned results: %s" % results)
        # FIXME: if results is messed up, don't run the next line
        # processImage returns a tuple of deques containing frames for each band
        globals.animTuple = ImRts.processImage(path, results)
        console.cwrite("Animation loaded successfully.")
        # Scrolling thread needs to be stopped if it was initialized already
        try:
            console.cwrite("Stopping IO thread...")
            outputThread.join();
            globals.exitFlag = 0;
            outputThread = None;
            console.cwrite("IO thread stopped!")
        except:
            console.cwrite("Thread was probably already stopped")
        # Now get the animation thread going
        portName = str(self.ui.selRow1COM.currentText())
        globals.cxn1 = serial.Serial(portName, 9600)
        serialWelcome("animation")

    def resetChipIDs(self, event):
        serialSendEx("Resetting chip IDs...", "\xFF\x81\x00", 2)

    def saveChipID(self, chipIdContainer):
        # Validate the input
        chipAddr = isValidBoardAddress(chipIdContainer)
        if chipAddr is None: return
        if chipAddr < 64:
            debugMsg = "Saving chip addresses on board %d..." % chipAddr
            serialSendEx(debugMsg, "\xFF\x85" + chr(int(chipAddr + 128)) + "\xFF\x85" + chr(int(chipAddr + 192)), 2)
        elif chipAddr > 127:
            debugMsg = "Saving chip address %d to the chip..." % chipAddr
            serialSendEx(debugMsg, "\xFF\x85" + chr(int(chipAddr)), 2)

    def saveAllIDs(self, event):
        for i in range(128, 256):
            serialSendEx("Saving chip ID " + i.__str__() + " to the chip...", "\xFF\x85" + chr(i), 0.002)
        console.cwrite("Done saving all chip IDs.  Sorry for all the messages; we'll reduce the extraneous output later.")

    def compressChipIDs(self, event):
        boardCount = len(globals.boards)
        for i in range(1, boardCount):
            serMsg = ""
            for j in range(globals.boards[i - 1] + 1, globals.boards[i] + 1):
                serMsg += "\xFF\x84" + chr(j + 0x80) + chr(i + 0x80)
                serMsg += "\xFF\x84" + chr(j + 0xC0) + chr(i + 0xC0)
            serialSendEx("Compressing chip IDs...", serMsg, 2)
            #sleep(0.5)
        startWith = isValidBoardAddress(self.ui.txtCompressStartFrom)
        if startWith is None:
            startWith = 0
        msgIndexes = [i % 64 for i in range(startsWith, startsWith + boardCount)]
        serMsg = ""
        for i in range(startWith + boardCount - 1, startWith - 1, -1):
            serMsg += "\xFF\x84" + chr((i - boardCount) + 0x80) + chr(i + 0x80)
            serMsg += "\xFF\x84" + chr((i - boardCount) + 0xC0) + chr(i + 0xC0)
        serialSendEx("Resetting chip IDs...", serMsg, 2)

    def excrementChipID(self, chipIdContainer, direction):
        # Validate the input
        chipAddr = isValidBoardAddress(chipIdContainer)
        if chipAddr is None: return
        if chipAddr < 64:
            if direction == 1:
                debugMsg = "Incrementing chips on board %d..." % chipAddr
                serialSendEx(debugMsg, "\xFF\x82" + chr(int(chipAddr + 128)) + "\xFF\x82" + chr(int(chipAddr + 192)), 2)
            elif direction == -1:
                debugMsg = "Decrementing chips on board %d..." % chipAddr
                serialSendEx(debugMsg, "\xFF\x83" + chr(int(chipAddr + 128)) + "\xFF\x83" + chr(int(chipAddr + 192)), 2)
        elif chipAddr > 127:
            if direction == 1:
                debugMsg = "Incrementing chip address %d..." % chipAddr
                serialSendEx(debugMsg, "\xFF\x82" + chr(int(chipAddr)), 2)
            elif direction == -1:
                debugMsg = "Decrementing chip address %d..." % chipAddr
                serialSendEx(debugMsg, "\xFF\x83" + chr(int(chipAddr)), 2)
        
    def setChipID(self, oldBoardIdContainer, newBoardIdContainer):
        # Validate the input
        oldBoardAddr = isValidBoardAddress(oldBoardIdContainer)
        newBoardAddr = isValidBoardAddress(newBoardIdContainer)
        if (oldBoardAddr is None) or (newBoardAddr is None): return
        # Do some additional validation
        if (oldBoardAddr < 64 and newBoardAddr >= 64) or (oldBoardAddr >= 64 and newBoardAddr < 64):
            console.cwrite("When changing IDs for a board, the current value and desired value must be each less than 64.")
            return
        if (oldBoardAddr < 64):
            debugMsg = "Setting board address %d to be %d..." % (oldBoardAddr, newBoardAddr)
            serialSendEx(debugMsg,
                         "\xFF\x84" + chr(int(oldBoardAddr) + 128) + chr(int(newBoardAddr) + 128) + 
                         "\xFF\x84" + chr(int(oldBoardAddr) + 192) + chr(int(newBoardAddr) + 192),
                         2)
        elif (oldBoardAddr > 127):
            debugMsg = "Setting chip address %d to be %d..." % (oldBoardAddr, newBoardAddr)
            serialSendEx(debugMsg, "\xFF\x84" + chr(int(oldBoardAddr)) + chr(int(newBoardAddr)), 2)
        
    def showTestPatternOn(self, boardIdContainer):
        # Validate the input
        boardAddr = isValidBoardAddress(boardIdContainer) if (boardIdContainer != 64) else 64
        if boardAddr is None: return
        if (boardAddr < 64):
            debugMsg = "Showing test pattern on board ID %s (chip addresses %d and %d)..." % (boardAddr, boardAddr + 128, boardAddr + 192)
            serialSendEx(debugMsg, "\xFF\x80" + chr(int(boardAddr)), 5)
        elif (boardAddr < 128):
            serialSendEx("Showing test pattern on all boards...", "\xFF\x80" + chr(int(boardAddr)), 5)
        elif (boardAddr < 256):
            debugMsg = "Showing test pattern on chip ID %s..." % boardAddr
            serialSendEx(debugMsg, "\xFF\x80" + chr(int(boardAddr)), 5)
            
    def updateTargetBaudRate(self, event):
        numPanels = self.ui.spinBaudRatePanels.value()
        maxRefresh = self.ui.spinBaudRateScrollRate.value()
        for baud in baudRates:
            if (int(baud) / (numPanels * 96) > maxRefresh):
                self.ui.lblTargetBaudRate.setText(baud)
                break
            else:
                self.ui.lblTargetBaudRate.setText("Unsupported")
    

################################################################################
# Step 3. Launch the app
################################################################################    

mw = MainWindow()
# Add our serial ports.
serial_ports(mw)
mw.show()
console.cwrite("\nApplication is loaded.")
globals.pushMessage = mw.pushMessage
sys.exit(app.exec_())
