'''
Welcome to the BriteBlox PC Tools!  This file features inialization of the fonts and UI.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesForm.py "C:\Python27\LEDgoes PC Interface.ui"

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
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import LEDgoesGlobals as globals
import json
# import the LEDgoes-specific GUI framework details
import LEDgoesForm
from LEDgoesForm import Ui_MainWindow
# Import other windows used in our GUI
import LEDgoesConsole as console    # Used to debug the marquee & the software
import LEDgoesDesigner as designer  # Used to design fonts & board layouts
# import things important for serial connections
import os
import serial
# find ports among the different operating systems
from serial.tools import list_ports     # All OSes have this but it can be really slow in Windows
# NOTE: There are a couple more Windows-specific imports if the alternate port enumeration method is selected
# import this to help find fonts
import glob
# Import the signal module so we can listen for when the user hits Ctrl+C
import signal
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
# Allow user to save & import configurations
import ConfigParser

################################################################################
# Step 1. Define the QApplication so we can start building GUI widgets
################################################################################

app = QApplication(sys.argv)
if sys.platform != "darwin":
    app.setWindowIcon(QIcon('LEDgoes-Icon.ico'))
else:
    app.setWindowIcon(QIcon('LEDgoes-Icon.icns'))

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
        serialMsg = "%s%s" % (globals.cmdPassword, chr(0x90 + baudRateIdx))
        serialSendEx("Sending %s at 9600 baud to change baud rate" % serialMsg, serialMsg, 1)
        sleep(1.2)
    globals.cxn1.close()
    if baudRates[baudRateIdx] != prevBaudRate and prevBaudRate != "9600":
        # the user adjusted the serial rate before, so talk to the boards at their current rate
        globals.cxn1.baudrate = int(prevBaudRate)
        globals.cxn1.open()
        serialMsg = "%s%s" % (globals.cmdPassword, chr(0x90 + baudRateIdx))
        debugMsg = "\nSending %s at %s baud to change baud rate" % (serialMsg, baudRates[baudRateIdx])
        serialSendEx(debugMsg, serialMsg, 1)
        prevBaudRate = baudRates[baudRateIdx]
        sleep(1.2)
        globals.cxn1.close()
    
    # Now actually re-open this program's serial connection in the user's desired speed
    sleep(1)
    globals.cxn1.baudrate = int(baudRates[baudRateIdx])
    #console.cwrite(globals.cxn1.baudrate)
    globals.cxn1.open()
    # Send the serial commands to adjust any board IDs that might be one too low
    if len(globals.boards) < 33:    # Only do this when 32 boards or less are in use
        tmp = list(globals.boards)
        increments = [int(x[2]) - 1 for x in tmp]
        for boardID in increments:
            if boardID == 0:
                continue
            serialSendEx("", globals.cmdPassword + "\x82" + chr(boardID + 128), 0.001)
            serialSendEx("", globals.cmdPassword + "\x82" + chr(boardID + 192), 0.001)
    # Start a thread
    if welcomeType == "scroll":
        outputThread = scroll.serialThread()
        outputThread.start()
    elif welcomeType == "animation":
        animationThread = ImRts.animationThread()
        animationThread.start()

################################################################################
# Step 4. Load all user-defined fonts & configurations
################################################################################

# Make sure we are looking for fonts in the right place
if getattr(sys, 'frozen', False):
    globals.application_path = "%s/" % os.path.dirname(sys.executable)
elif __file__:
    globals.application_path = os.path.dirname(__file__)

# Look for all .ledfont files in the current working directory
console.cwrite("\nLoading fonts...")
fontWarningsEnabled = True
for filename in glob.glob("%s*.ledfont" % globals.application_path):
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
        print e
        console.cwrite("Error loading font %s" % filename)
        if fontWarningsEnabled:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("BriteBlox PC Interface")
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
    msgBox.setWindowTitle("BriteBlox PC Interface")
    msgBox.setText("Fatal error; cannot start")
    msgBox.setInformativeText("No fonts were successfully loaded from the working directory of LEDgoes PC Interface.  Font files (*.ledfont) can be downloaded from http://www.ledgoes.com.\n\nTried path: %s*.ledfont" % globals.application_path)
    msgBox.setStandardButtons(QMessageBox.Ok)
    msgBox.setDefaultButton(QMessageBox.Ok)
    msgBox.setIcon(QMessageBox.Critical)
    ret = msgBox.exec_()
    sys.exit(0)

# Read the configuration file
OpenBriteUSBDevicesOnly = False
config = ConfigParser.ConfigParser()
if config.read('briteblox.ini') != []:
    # Set the third, optional argument of get to 1 if you wish to use raw mode.
    OpenBriteUSBDevicesOnly = config.getboolean('Communication', 'OpenBriteUSBDevicesOnly')

# This function finds the name of all serial ports and adds them to our lists
def serial_ports(mainWindow):
    console.cwrite("\nScanning for serial ports...")
    mainWindow.ui.selRow1COM.clear()
    mainWindow.ui.selRow2COM.clear()
    if os.name == 'nt' and False:
        # Windows (alternate option)
        import win32file
        import re           # So we can search for "COM\d"
        comPorts = [device for device in win32file.QueryDosDevice(None).split("\x00") if re.search("^COM\d+$", device)]
        comPorts.sort()
        [mainWindow.ui.selRow1COM.addItem(comPort) for comPort in comPorts]
        [mainWindow.ui.selRow2COM.addItem(comPort) for comPort in comPorts]
    else:
        vidpid = "USB VID:PID=403:7AD0" if sys.platform == "darwin" else "VID_0403+PID_7AD0"
        # Everyone else
        for comPort in list_ports.comports():
            # If the user only wants to see connections for compatible OpenBrite devices, use this filter
            if (not OpenBriteUSBDevicesOnly) or (vidpid in comPort[2].upper()):
                mainWindow.ui.selRow1COM.addItem(comPort[0])
                mainWindow.ui.selRow2COM.addItem(comPort[0])
    
def serialSendEx(debugMsg, serialMsg, delay, keepCxn=False):
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
        cxn = globals.cxn1
        try:
            cxn.write(serialMsg)
        except Exception as ex:
            console.cwrite("Error writing to the selected port; perhaps it is closed.  Will try opening it.  Details: %s" % ex)
            # TODO FIXME: Port name should be determined from an array of rowNum -> COM port
            cxn = None
            try:
                cxn = serial.Serial(mw.ui.selRow1COM.currentText(), baudRates[baudRateIdx], timeout=2)
                cxn.write(serialMsg)
            except Exception as ex:
                console.cwrite("There was a problem opening the selected port (%s) and writing the desired message.  Please make sure you have a working COM port selected.\n" % mw.ui.selRow1COM.currentText())
                console.cwrite("Details: %s" % ex)
                return False
            console.cwrite("Finished writing the desired message.\n")
            if keepCxn:
                globals.cxn1 = cxn
            else:
                globals.cxn1.close()
    return True

def serialReadEx(msgLen, msgWrapper, delay, keepCxn=False):
    global outputThread
    try:
        if outputThread.isAlive():
            # If the output thread is alive, let that thread handle the IO
            # Define the message: control mode flag FF, instruction 80, chip ID 80 (chip ID doesn't matter in this case)
            # Add a flag to read the serial output
            globals.evtDefinition = {'message': serialMsg, 'delay': delay, 'read': True}
            globals.evt.clear()      # clear the event flag to indicate it should branch before further updates
        else:
            # Raise an exception so we send the commands over serial anyway
            raise
    except:
        try:
            message = globals.cxn1.read(msgLen)
            console.cwrite(msgWrapper % message)
        except Exception as ex:
            console.cwrite("There was a problem opening the selected port (%s) and reading the desired message.  Please make sure you have a working COM port selected.\n" % mw.ui.selRow1COM.currentText())
            console.cwrite("Details: %s" % ex)
            globals.cxn1.close()
            return False
        if message == "":
            console.cwrite("The device on %s did not respond to the query.  Please make sure you have a working COM port selected.\n" % mw.ui.selRow1COM.currentText())
            return False
        else:
            console.cwrite([ord(m) for m in message])		
        if not keepCxn:
            globals.cxn1.close()
    return True
            
def _updateBoards(numBoards):
    rows = mw.ui.spinRows.value()
    globals.boards.clear()              # empty the list of board indexes
    delta = 1024 / (numBoards * rows)      # the auto-address line on each board should be equal to (1024 / # boards) * i
    if rows == 1:
        # Standard arrangement -- one row worth of numBoards panels
        for i in range(0, numBoards):
            globals.boards.extend([(i, 0, int( delta * i / 16 ))])
    else:
        if True:    # TODO: this should be based on if Multiplexed is set or not
            # Multi-row arrangement -- 0 on top left, 63 on bottom right, no snake; each row has numBoards worth of panels
            for r in range(0, rows):
                for i in range(0, numBoards):
                    boardIdx = (r * numBoards) + i
                    globals.boards.extend([(i, rows - r - 1, int( delta * boardIdx / 16 ))])
        else:
            # Multi-row arrangement -- multiplexed so that 0 is on top row, 1 is on 2nd row, ...
            counter = 0
            for r in range(0, rows):
                for i in range(0, numBoards):
                    globals.boards.extend([(i, r, counter)])
                    counter += 1
    print globals.boards

def isValidBoardAddress(address):
    number = 0
    # if the number is False, return 0
    if address is False:
        return 0
    try:                     # first, try the number in Base 10
        number = int(address)
    except ValueError:       # now try it in hex (Base 16)
        try:
            number = int(address, 16)
        except:              # number is not valid in decimal or hex
            console.cwrite("Error: Address \"%s\" is not valid.  A board address is an integer ranging from 0 through 63; chip addresses exist from 128 through 255.\n" % inputContainer.text())
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

################################################################################
# Firmware Operations
################################################################################

def showTestPatternOn(boardId):
    # Validate the input
    boardAddr = isValidBoardAddress(boardId) if (boardId != 64) else 64
    if boardAddr is None: return
    if (boardAddr < 64):
        debugMsg = "Showing test pattern on board ID %s (chip addresses %d and %d)..." % (boardAddr, boardAddr + 128, boardAddr + 192)
        serialSendEx(debugMsg, globals.cmdPassword + "\x80" + chr(int(boardAddr)), 5)
    elif (boardAddr < 128):
        serialSendEx("Showing test pattern on all boards...", globals.cmdPassword + "\x80" + chr(int(boardAddr)), 5)
    elif (boardAddr < 256):
        debugMsg = "Showing test pattern on chip ID %s..." % boardAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x80" + chr(int(boardAddr)), 5)

def resetChipIDs():
    serialSendEx("Resetting chip IDs...", globals.cmdPassword + "\x81\x00", 2)

def excrementChipID(chipId, direction):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId)
    if chipAddr is None: return
    if chipAddr < 64:
        if direction == 1:
            debugMsg = "Incrementing chips on board %d..." % chipAddr
            serialSendEx(debugMsg, globals.cmdPassword + "\x82" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x82" + chr(int(chipAddr + 192)), 2)
        elif direction == -1:
            debugMsg = "Decrementing chips on board %d..." % chipAddr
            serialSendEx(debugMsg, globals.cmdPassword + "\x83" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x83" + chr(int(chipAddr + 192)), 2)
    elif chipAddr > 127:
        if direction == 1:
            debugMsg = "Incrementing chip address %d..." % chipAddr
            serialSendEx(debugMsg, globals.cmdPassword + "\x82" + chr(int(chipAddr)), 2)
        elif direction == -1:
            debugMsg = "Decrementing chip address %d..." % chipAddr
            serialSendEx(debugMsg, globals.cmdPassword + "\x83" + chr(int(chipAddr)), 2)

def setChipID(oldBoardId, newBoardId):
    # Validate the input
    oldBoardAddr = isValidBoardAddress(oldBoardId)
    newBoardAddr = isValidBoardAddress(newBoardId)
    if (oldBoardAddr is None) or (newBoardAddr is None): return
    # Do some additional validation
    if (oldBoardAddr < 64 and newBoardAddr >= 64) or (oldBoardAddr >= 64 and newBoardAddr < 64):
        console.cwrite("When changing IDs for a board, the current value and desired value must be each less than 64.")
        return
    if (oldBoardAddr < 64):
        debugMsg = "Setting board address %d to be %d..." % (oldBoardAddr, newBoardAddr)
        serialSendEx(debugMsg,
                     globals.cmdPassword + "\x84" + chr(int(oldBoardAddr) + 128) + chr(int(newBoardAddr) + 128) + 
                     globals.cmdPassword + "\x84" + chr(int(oldBoardAddr) + 192) + chr(int(newBoardAddr) + 192),
                     2)
    elif (oldBoardAddr > 127):
        debugMsg = "Setting chip address %d to be %d..." % (oldBoardAddr, newBoardAddr)
        serialSendEx(debugMsg, globals.cmdPassword + "\x84" + chr(int(oldBoardAddr)) + chr(int(newBoardAddr)), 2)

def saveChipID(chipId):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId) if (chipId != 64) else 64
    if chipAddr is None: return
    if chipAddr < 64:
        debugMsg = "Saving chip addresses on board %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x85" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x85" + chr(int(chipAddr + 192)), 2)
    elif chipAddr > 127:
        debugMsg = "Saving chip address %d to the chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x85" + chr(int(chipAddr)), 2)
    elif chipAddr == 64:
        # Save All IDs
        tempMsg = ""
        for i in range(128, 256):
            tempMsg += globals.cmdPassword + "\x85" + chr(i)
        if serialSendEx("Saving all chip IDs to all chips...", tempMsg, 0.5):
            console.cwrite("Done saving all chip IDs.")
        else:
            console.cwrite("Failed to save all chip IDs.")

def eraseChipID(chipId):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId) if (chipId != 64) else 64
    if chipAddr is None: return
    if chipAddr < 64:
        debugMsg = "Erasing chip addresses on board %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x86" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x86" + chr(int(chipAddr + 192)), 2)
    elif chipAddr > 127:
        debugMsg = "Erasing chip address %d to the chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x86" + chr(int(chipAddr)), 2)
    elif chipAddr == 64:
        # Erase All IDs
        for i in range(128, 256):
            if not serialSendEx("Erasing chip ID " + i.__str__() + " from the chip...", globals.cmdPassword + "\x86" + chr(i), 0.002):
                break
        console.cwrite("Done erasing all chip IDs.  Sorry for all the messages; we'll reduce the extraneous output later.")

def saveBaudRate(chipId):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId)
    if chipAddr is None: return
    if chipAddr < 64:
        debugMsg = "Saving baud rate to board %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x9E" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x9E" + chr(int(chipAddr + 192)), 2)
    elif chipAddr > 127:
        debugMsg = "Saving baud rate to chip %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x9E" + chr(int(chipAddr)), 2)

def eraseBaudRate(chipId):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId)
    if chipAddr is None: return
    if chipAddr < 64:
        debugMsg = "Erasing baud rate on board %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x9F" + chr(int(chipAddr + 128)) + globals.cmdPassword + "\x9F" + chr(int(chipAddr + 192)), 2)
    elif chipAddr > 127:
        debugMsg = "Erasing baud rate from chip %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\x9F" + chr(int(chipAddr)), 2)

def eraseMemoryOnAll():
    serialSendEx("Erasing the EEPROM settings (Chip ID & baud rate) on all boards...", globals.cmdPassword + "\x8F\x00", 2)

def viewFirmwareVersion(chipId):
    # Validate the input
    chipAddr = isValidBoardAddress(chipId) if (chipId != 64) else 64
    if chipAddr is None: return
    if chipAddr < 64:
        debugMsg = "Polling for firmware version on board %d red chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 128)), 0.35, True)
        serialReadEx(3, "Red chip firmware version: %s", 0.35, True)
        sleep(1)
        debugMsg = "Polling for firmware version on board %d green chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 192)), 0.35, True)
        serialReadEx(3, "Green chip firmware version: %s", 0.35, False)
    elif chipAddr == 64:
        boardCount = len(globals.boards)
        for i in range(1, boardCount):
            serMsg = ""
            chipAddr = globals.boards[i - 1][2]
            debugMsg = "Polling for firmware version on board %d red chip..." % chipAddr
            if not serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 128)), 0.35, True):
                break
            if not serialReadEx(3, "Red chip firmware version: %s", 0.35, False):
                break
            sleep(1)
            debugMsg = "Polling for firmware version on board %d green chip..." % chipAddr
            if not serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 192)), 0.35, True):
                break
            if not serialReadEx(3, "Green chip firmware version: %s", 0.35, False):
                break
            sleep(1)
        chipAddr = globals.boards[boardCount - 1][2]
        debugMsg = "Polling for firmware version on board %d red chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 128)), 0.35, True)
        serialReadEx(3, "Red chip firmware version: %s", 0.35, False)
        sleep(1)
        debugMsg = "Polling for firmware version on board %d green chip..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr + 192)), 0.35, True)
        serialReadEx(3, "Green chip firmware version: %s", 0.35, False)
    elif chipAddr > 127:
        debugMsg = "Polling for firmware version on chip %d..." % chipAddr
        serialSendEx(debugMsg, globals.cmdPassword + "\xA0" + chr(int(chipAddr)), 2, True)
        serialReadEx(3, "Chip " + chipAddr.__str__() + " firmware version: %s", 0.35, False)

def compressChipIDs(startsWith, perceivedGap):
    ''' Takes a marquee whose boards have at least somewhat evenly dispersed 
        IDs and condenses those IDs into an incrementally ascending order.
        For instance, with 4 boards {0, 16, 32, 48} offset = 0, and gap = 1, 
        the new board address layout will be {0, 1, 2, 3).  Offset adjusts the 
        starting number; gap adjusts the difference in assigned ID between 
        boards (minimum gap is 1).

		The for loop iterates backward through the boards in order to 
		assign the highest desired ID first to the highest-addressed board so 
		conflicts do not arise.  This loop sets the user's desired sequence 
		after the first loop has changed the boards' addresses to predictable 
		values.
    '''
    boardCount = len(globals.boards)
    # Validate startsWith
    startsWith = isValidBoardAddress(startsWith)
    if startsWith is None: return
    if startsWith > 63:
        console.cwrite("You must specify a board address between 0 and 63 for the startsWith offset.")
        return
    # Validate the gap
    try:
        gap = int(perceivedGap)
        if gap < 1 or gap > 32:
            raise ValueError
    except ValueError:
        console.cwrite("Error: Gap \"%s\" is not valid.  The gap must be an integer ranging from 1 through 32.\n" % perceivedGap)
        return None
    serMsg = ""
    balanceChipIDs(boardCount)
    for i in range(boardCount - 1, -1, -1):
        serMsg += globals.cmdPassword + "\x84" + chr(i + 0x80) + chr(startsWith + (gap * i) + 0x80)
        serMsg += globals.cmdPassword + "\x84" + chr(i + 0xC0) + chr(startsWith + (gap * i) + 0xC0)
    serialSendEx("Resetting chip IDs...", serMsg, 2)

def balanceChipIDs(boardCount):
    ''' This for loop spreads the IDs out evenly among the entire marquee,
        correcting any "sag" where any board might have an address slightly 
        lower than expected.  For each correct (expected) board ID from the 
        marquee's end to start, take all chip IDs from (expected ID for the 
        previous board) all the way up to (currect expected board - 1) and send
        a command to reassign those boards with the address of the current 
        expected board.
    '''
    for i in range(1, boardCount):
        serMsg = ""
        for j in range(globals.boards[i - 1][2] + 1, globals.boards[i][2] + 1):
            serMsg += globals.cmdPassword + "\x84" + chr(j + 0x80) + chr(i + 0x80)
            serMsg += globals.cmdPassword + "\x84" + chr(j + 0xC0) + chr(i + 0xC0)
        if not serialSendEx("Compressing chip IDs...", serMsg, 2):
            break
        #sleep(0.5)


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
        # Menu
        self.ui.actionUSB_Device_Selection.toggled.connect(self.toggleUSBFlavors)
        self.ui.actionDumb_Enumeration.toggled.connect(self.toggleDumbEnumeration)
        self.ui.actionRefresh_COM_Ports.triggered.connect(lambda: serial_ports(mw))
        self.ui.actionAbout_LEDgoes_PC_Interface.triggered.connect(self.showAbout)
        # Main panels on top
        self.ui.spinUpdateDelay.valueChanged.connect(self.updateDelay)
        self.ui.spinRows.valueChanged.connect(self.updateBoards)
        self.ui.spinPanelsPerRow.valueChanged.connect(self.updateBoards)
        self.ui.btnCustomLayout.clicked.connect(self.openDesigner)
        self.ui.selSpeed.activated.connect(self.updateSpeed)
        self.ui.btnConnectRow1.clicked.connect(lambda: self.toggleRow(1))
        self.ui.btnConnectRow2.clicked.connect(lambda: self.toggleRow(2))
        self.ui.btnOpenConsole.clicked.connect(self.openConsole)
        # Raw Text panel
        self.ui.btnDeleteRawText.clicked.connect(self.deleteMessage)
        self.ui.btnInsertRawTextBefore.clicked.connect(lambda: self.insertMessage(0))
        self.ui.btnInsertRawTextAfter.clicked.connect(lambda: self.insertMessage(1))
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
        #self.ui.btnShowTestPattern.clicked.connect(lambda: self.showTestPatternOn(self.ui.txtTestOn))
        #self.ui.btnShowAllTestPatterns.clicked.connect(lambda: self.showTestPatternOn(64))
               # This changes the chip ID from Target to Desired
        #self.ui.btnSetChipID.clicked.connect(lambda: self.setChipID(self.ui.txtChipIDTarget, self.ui.txtChipIDDesired))
        #self.ui.btnEraseMemoryOnAll.clicked.connect(self.eraseMemoryOnAll)
        self.ui.fwOpsList.itemSelectionChanged.connect(self.setupFwOpPanel)
        self.ui.btnAllBoards.clicked.connect(self.selectAllBoards)
        self.ui.btnExecFwOp.clicked.connect(self.executeFwOp)
        self.ui.btnEraseSettings.clicked.connect(self.eraseSomething)
        # Simulator panel
        # Baud Rate panel
        self.ui.spinBaudRatePanels.valueChanged.connect(self.updateTargetBaudRate)
        self.ui.spinBaudRateScrollRate.valueChanged.connect(self.updateTargetBaudRate)
        
        # Populate the list in the Firmware tab
        # 1 = command is from firmware, 128-255 = 0x80-0xFF = actual firmware opcode
        # 2 = command is implemented in software & runs multiple firmware ops, 000-999 = index
        QListWidgetItem("Show Test Pattern", self.ui.fwOpsList, 1128)
        QListWidgetItem("Increment Chip ID", self.ui.fwOpsList, 1130)
        QListWidgetItem("Decrement Chip ID", self.ui.fwOpsList, 1131)
        QListWidgetItem("Change Chip ID", self.ui.fwOpsList, 1132)
        QListWidgetItem("Reset All Chip IDs", self.ui.fwOpsList, 1129)
        QListWidgetItem("Save/Erase Chip ID(s)", self.ui.fwOpsList, 1133)
        QListWidgetItem("Save/Erase Baud Rate(s)", self.ui.fwOpsList, 1158)
        QListWidgetItem("Erase All Settings", self.ui.fwOpsList, 1143)
        QListWidgetItem("View Firmware Version", self.ui.fwOpsList, 1160)
        QListWidgetItem("Compress Chip IDs", self.ui.fwOpsList, 2000)
    
    def toggleUSBFlavors(self, event):
        global OpenBriteUSBDevicesOnly
        # Set the "OpenBriteUSBDevicesOnly" boolean value to "event" -- true or false depending on if the checkmark is toggled
        OpenBriteUSBDevicesOnly = event
        # Refresh the available serial ports right away
        serial_ports(mw)

    def toggleDumbEnumeration(self, event):
        print event

    def showAbout(self, event):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("About")
        msgBox.setText("BriteBlox PC Interface, Version 1.2.1a - 7/7/2015")
        msgBox.setInformativeText("Copyleft 2013-15 OpenBrite, LLC\n\nSee our GitHub repository at https://github.com/ledgoes/")
        msgBox.setStandardButtons(QMessageBox.Ok)
        msgBox.setDefaultButton(QMessageBox.Ok)
        msgBox.setIcon(QMessageBox.Warning)
        ret = msgBox.exec_()

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
        # baudRateIdx is the old baud rate the boards were running at; speed is the desired baud rate
        serialMsg = "%s%s" % (globals.cmdPassword, chr(0x90 + speed))
        # Send a message to the panels to run at the desired rate
        serialSendEx("Changing baud rate from %s to %s..." % (baudRates[baudRateIdx], baudRates[speed]), serialMsg, 1)
		# Now set the "old baud rate index" to the present index, since we're done talking at the old baud rate
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
                globals.cxn1 = serial.Serial(portName, 9600, timeout=2)
                activeConns += 1
                self.ui.btnConnectRow1.setText("Disconnect")
        elif rowNum == 2:
            if globals.cxn2.isOpen():
                globals.cxn2.close()
                activeConns -= 1
                self.ui.btnConnectRow2.setText("Connect")
            else:
                globals.cxn1 = serial.Serial(portName, timeout=2)
                activeConns += 1
                self.ui.btnConnectRow2.setText("Disconnect")
                
        # Now, look to see if we have the required connections in place to start the matrix
        # Otherwise, stop the matrix
        
        # TODO: Don't assume we're using just one row
        if activeConns == 1:
            serialWelcome("scroll")
        elif activeConns == 0:
            globals.exitFlag = 1
            try:
                console.cwrite("Stopping IO thread...")
                outputThread.join()
                globals.exitFlag = 0
                outputThread = None
                console.cwrite("IO thread stopped!")
            except AttributeError:
                console.cwrite("Thread was probably already stopped")

    def openConsole(self, event):
        console.openConsole()

    def openDesigner(self, event):
        designer.openDesigner()

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
            msgBox.setWindowTitle("BriteBlox PC Interface")
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
            self.ui.txtTwitterConsumerKey.text(),
            self.ui.txtTwitterConsumerSecret.text(),
            self.ui.txtTwitterTokenKey.text(),
            self.ui.txtTwitterTokenSecret.text()
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
        globals.cxn1 = serial.Serial(portName, 9600, timeout=2)
        serialWelcome("animation")

    def selectAllBoards(self, event):
        # Just make the box say "All" - the program will pick up on that keyword
        self.ui.txtSrcBoard.setPlainText("All")

    def setupFwOpPanel(self):
        # Find out what item (firmware operation) is selected, then do it
        fwOp = 0
        try:
            fwOp = self.ui.fwOpsList.selectedItems()[0].type()
        except:
            return
        if fwOp == 1128:
            # show test pattern
            self.ui.lblFwOpHelp.setText("Shows the test pattern on the specified board(s), normally consisting of the board ID.")
            self.ui.lblSrcBoard.setText("On:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.show()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1130:
            # increment chip ID
            self.ui.lblFwOpHelp.setText("Adds 1 to the specified board or chip ID.  Make sure no other device has the resulting ID.")
            self.ui.lblSrcBoard.setText("Current ID:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1131:
            # decrement chip ID
            self.ui.lblFwOpHelp.setText("Subtracts 1 from the specified board or chip ID.  Make sure no other device has the resulting ID.")
            self.ui.lblSrcBoard.setText("Current ID:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1132:
            # change chip ID
            self.ui.lblFwOpHelp.setText("Changes the current board or chip ID to the desired value.  Make sure no other device has the desired ID.")
            self.ui.lblSrcBoard.setText("Current ID:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.setText("Desired ID:")
            self.ui.lblTargetBoard.show()
            self.ui.txtTargetBoard.show()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1129:
            # reset all chip IDs
            self.ui.lblFwOpHelp.setText("Resets all chip IDs to the stored value, or the value determined by auto-addressing.")
            self.ui.lblSrcBoard.hide()
            self.ui.txtSrcBoard.hide()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1133:
            # Save/Erase Chip ID
            self.ui.lblFwOpHelp.setText('Hit "Save" to commit the chip or board ID to the specified device\'s memory.  Hit "Erase" to erase it.')
            self.ui.lblSrcBoard.setText("On:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.show()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Save")
            self.ui.btnEraseSettings.show()
        elif fwOp == 1158:
            # Save/Erase Baud Rate
            self.ui.lblFwOpHelp.setText('Hit "Save" to commit each board\'s baud rate to its memory.  Hit "Erase" to erase the settings.')
            self.ui.lblSrcBoard.hide()
            self.ui.txtSrcBoard.hide()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Save")
            self.ui.btnEraseSettings.show()
        elif fwOp == 1143:
            # Erase All Settings
            self.ui.lblFwOpHelp.setText("Erase all settings (ID and baud rate) stored on all devices.")
            self.ui.lblSrcBoard.hide()
            self.ui.txtSrcBoard.hide()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 1160:
            # View Firmware Version
            self.ui.lblFwOpHelp.setText("Displays the firmware version installed on the specified board(s) on the console.")
            self.ui.lblSrcBoard.setText("On:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.show()
            self.ui.lblTargetBoard.hide()
            self.ui.txtTargetBoard.hide()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()
        elif fwOp == 2000:
            # Compress Chip IDs
            self.ui.lblFwOpHelp.setText('Changes sequence of IDs: e.g. 0, 16, 32, 48 can become 0, 1, 2, 3. "Start with" adds initial offset. "Gap" specifies common difference.')
            self.ui.lblSrcBoard.setText("Start with:")
            self.ui.lblSrcBoard.show()
            self.ui.txtSrcBoard.show()
            self.ui.btnAllBoards.hide()
            self.ui.lblTargetBoard.setText("Gap:")
            self.ui.lblTargetBoard.show()
            self.ui.txtTargetBoard.show()
            self.ui.btnExecFwOp.setText("Go!")
            self.ui.btnEraseSettings.hide()

    def executeFwOp(self, event):
        # Find out what item (firmware operation) is selected, then do it
        fwOp = 0
        id = 0
        id2 = 0
        try:
            fwOp = self.ui.fwOpsList.selectedItems()[0].type()
            id = self.ui.txtSrcBoard.toPlainText() if self.ui.txtSrcBoard.toPlainText() != "All" else 64
            if fwOp == 1132 or fwOp == 2000:
                id2 = self.ui.txtTargetBoard.toPlainText()
        except IndexError:
            console.cwrite("You must first select a firmware operation from the list at left.")
        except Exception as ex:
            print ex
            return
        if fwOp == 1128:
            # show test pattern
            showTestPatternOn(id)
        elif fwOp == 1130:
            # increment chip ID
            excrementChipID(id, 1)
        elif fwOp == 1131:
            # decrement chip ID
            excrementChipID(id, -1)
        elif fwOp == 1132:
            # change chip ID
            setChipID(id, id2)
        elif fwOp == 1129:
            # reset all chip IDs
            resetChipIDs()
        elif fwOp == 1133:
            # Save/Erase Chip ID
            saveChipID(id)
        elif fwOp == 1158:
            # Save/Erase Baud Rate
            saveBaudRate(id)
        elif fwOp == 1143:
            # Erase All Settings
            eraseMemoryOnAll()
        elif fwOp == 1160:
            # View Firmware Version
            viewFirmwareVersion(id)
        elif fwOp == 2000:
            # Compress Chip IDs
            compressChipIDs(id, id2)

    def eraseSomething(self, event):
        # Find out what item (firmware operation) is selected, then do it
        fwOp = 0
        id = 0
        try:
            fwOp = self.ui.fwOpsList.selectedItems()[0].type()
            id = self.ui.txtSrcBoard.toPlainText() if self.ui.txtSrcBoard.toPlainText() != "All" else 64
        except Exception as ex:
            print ex
            return
        if fwOp == 1133:
            # Save/Erase Chip ID
            eraseChipID(id)
        elif fwOp == 1158:
            # Save/Erase Baud Rate
            eraseBaudRate(id)

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
