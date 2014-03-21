'''
Welcome to the LEDgoes PC Tools!  This file features inialization of the fonts and UI.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesForm.py "C:\Users\Stephen\Documents\LEDgoes PC Interface.ui"

Requires pywin32 - http://sourceforge.net/projects/pywin32/files/pywin32/Build%20218/

Any assistance to make this code more "Pythonic" will be greatly welcome.
'''
# import things for the application & the GUI framework
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
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

################################################################################
# Step 0. Define the signal handler "KeyboardInterrupt" so the user can exit the app with Ctrl+C
################################################################################

# TODO: Not working. Fix.
def signal_handler(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

################################################################################
# Step 1. Define the serial thread routine, since evidently I can't put this in a separate file w/o circular dependencies
################################################################################
# import deque from collections since it should be faster than using a standard list
from collections import deque
# import the capability to pause the thread so we don't go off the rails scrolling as fast as possible
from time import sleep
# import threading so our I/O isn't on the UI thread
import threading
# import things from our main UI script
# import richMsgs, rows, font, boards, cxn1, cxn2

exitFlag = 0              # Will be raised when the thread should exit

counter = 0               # How far the scrolling message has advanced
maxCounter = 0            # How far the scrolling message can advance without hitting errors
serialMsgRed = deque()    # Red-only data translated into serial format for direct output
serialMsgGreen = deque()  # Green-only data translated into serial format for direct output
evt = threading.Event()   # Thread will check if the event has gone to False, and then wait
evt.set()                 # Standard Python events allow threads to ocontinue running if event flag is set
evtDefinition = {}        # If the thread is running & the user wants to send a FW control signal, the thread will execute this string

def writeString(boardsIdx):
    # Import global variables
    global serialMsgRed, serialMsgGreen, cxn1, cxn2, boards
    # Figure out what serial port to use
    rows = 1
    #if rows == 2 and not multiplexed:   # With 2 rows in use & no demultiplexer, pick between the 2 active serial conns
    #    cxnRef = (offset % 0x02 == 0) ? cxn1 : cxn2;    # even chips are the top row, odd chips are the bottom row
    #else:             # With only 1 row, or 3+ rows, use just one serial conn (3+ requires the demuxer)
    cxnRef = cxn1
    # Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
    adjustment = (boardsIdx / rows) * 5;
    # Grab the 5 columns, shift if necessary, and save it into an actual byte array
    #shift = (offset % rows) * 7
    shift = 0
    rPart = chr(boards[boardsIdx] | 0x80)
    gPart = chr(boards[boardsIdx] | 0xC0)
    for i in range(5):
        index = counter + adjustment + i
        # How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
        try:
            rPart += chr((ord(serialMsgRed[index]) >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            print "writeString: Index error at index " + str(index)
        #if (index > 0x10) { rPart[i] = (byte) (rPart[i] & 0x1F); }
        try:
            gPart += chr((ord(serialMsgGreen[index]) >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            print "writeString: Index error at index " + str(index)
    #if (index > 0x10) { gPart[i] = (byte) (gPart[i] & 0xFC); }
    # Write red portion
    cxn1.write(rPart)
    # Write green portion
    cxn1.write(gPart)

def makeRMessageString(message):
    'Construct & return the message to appear in Red'
    return makeMessageString(message, "red")

def makeGMessageString(message):
    'Construct & return the message to appear in Green'
    return makeMessageString(message, "green")

# Returns public int[]
def makeMessageString(message, color):
    # The default subMessage will be a blank string the length of the "message" text
    # This is so all our deques will end up the same length
    subMessage = " " * (message.__len__())
    serialMsg = deque()
    # Find out which color we need to make the message in
    if (color == "green"):
        # Generate a sub-message containing only the parts to light up in green or yellow.
        subMessage = message
    elif (color == "red"):
        # Generate a sub-message containing only the parts to light up in red or yellow.
        subMessage = message
    else:
        # TODO: Throw exception
        print "Unknown color encountered."
        subMessage = message
    # Make the message string from the letters
    if (rows == 1):
        # Each character takes up 5 columns plus 1 spacer; each board is 5 columns wide
        serialMsg.extend(["\x00", "\x00", "\x00", "\x00", "\x00"])    # add padding to the left of the message
        for character in subMessage:
            # Map the current letter to something that appears in the font
            try:
			    # Add the prescribed character
                serialMsg.extend( font['LEDgoes Default Font']['size']['1']['weight']['4'][character] )
            except KeyError:
                serialMsg.extend(["\x00", "\x00", "\x00", "\x00", "\x00"])
                print "Character " + character + " unknown; substituting with whitespace"
            # Insert spacing between characters
            try:
				# Add the prescribed spacing between characters for this font
                serialMsg.extend(['\x00'] * font['LEDgoes Default Font']['size']['1']['weight']['4']['spacing'])
            except:
                # Add one space
                print "Character spacing is unknown for this font; assuming 0"
    return serialMsg
    
class serialThread (threading.Thread):
    def __init__(self):
        super(serialThread, self).__init__()
        print "IO Thread is now running; when it stops may not necessarily be advertised..."
    
    def run(self):
        global counter, exitFlag, serialMsgRed, serialMsgGreen, maxCounter, delay, evt, evtDefinition, cxn1
        while not exitFlag:  # mind you, this is the implementation coming straight from the firmware ;)
            # CHECKING FOR CONTROL MESSAGES
            if not evt.is_set():
                cxn1.write(evtDefinition['message'])
                try:      # if a delay has been set, sleep for that length of time
                    sleep(evtDefinition['delay'])
                    evt.set()
                except:   # otherwise, do not resume until an external event happens which resets the event flag
                    evt.wait()
            # WRITING THE MESSAGE ON THE BOARD
            for i in range(len(boards)):      # iterate through the amount of characters we have on the board
                procId = i                    # Each processor looks for its own special "code"
                writeString(procId)           # Write the portion of the string pertaining to the active processor
            counter += 1                      # Now go on to show the next character column
            # MESSAGE EXPIRATION
            if counter > maxCounter:          # If we've reached the end of the message,
                print "Updating messages...\n"
                counter = 0                   # reset the column counter to 0
                serialMsgRed.clear()          # reset the red string to empty
                serialMsgGreen.clear()        # reset the green string to empty
                for msg in richMsgs:
                    #emptyString = new String(' ', messages[i].Length);  // Make an empty string equal in length to the current message
                    #redString += ((i % 2 == 0) ? messages[i] : emptyString) + "  ";     // set the red string
                    #greenString += ((i % 2 != 0) ? messages[i] : emptyString) + "  ";   // set the green string
                    #greenString += messages[i] + "  ";     // set the red string
                    #redString += messages[i] + "  ";   // set the green string
                    serialMsgRed.extend(makeRMessageString(msg))
                    serialMsgGreen.extend(makeGMessageString(msg))
                    maxCounter = len(serialMsgRed) - (len(boards) * 5)
            # Now just sleep for a wee bit before we go to the next character column
            sleep(delay)

                    
################################################################################
# Step 2. Define important variables & functions & import user-defined modules
################################################################################

richMsgs = []             # Human-readable messages with formatting markers included
introMsg = " :: AWAITING MESSAGES "
richMsgs.append(introMsg) # The first message you should see when you connect to the board
counter = 0               # Stores how far into the message the board's first LED column needs to display
cxn1 = serial.Serial()    # Connection for row 1
cxn2 = serial.Serial()    # Connection for row 2
activeConns = 0           # How many active serial connections are going on
outputThread = None       # Reference to thread running the serial IO code
rows = 1                  # Number of rows of panels in the display
font = {}                 # Master dictionary of all font information
boards = deque()          # Number of boards being used in the matrix
delay = 0                 # Amount of time to wait until updating the board with another round of serial data
baudRates = ["9600", "14400", "19200", "28800", "38400", "57600", "76800", "115200",
"200000", "250000", "500000", "1000000"]
baudRateIdx = 0           # Index of the baud rate we're running at (w.r.t. baudRates)
prevBaudRate = "9600"     # If the user resets the baud rate, store it here in case they change it again

# Import other modules & methods

def serialWelcome():
    global cxn1, serialMsgRed, serialMsgGreen, outputThread, prevBaudRate, boards
    if not boards:       # if boards is empty,
        _updateBoards(2) # populate it
    delay = mw.ui.spinPanelsPerRow.value() * 0.001
    # At 9600 baud, adjust the boards' baud rate to conform to the user's wishes (just in case some were reset)
    if baudRateIdx != 0:
        serialMsg = "\xFF%s" % chr(0x90 + baudRateIdx)
        serialSendEx("Sending %s at 9600 baud to change baud rate" % serialMsg, serialMsg, 1)
        sleep(1.2)
    cxn1.close()
    if baudRates[baudRateIdx] != prevBaudRate and prevBaudRate != "9600":
        # the user adjusted the serial rate before, so talk to the boards at their current rate
        cxn1.baudrate = int(prevBaudRate)
        cxn1.open()
        serialMsg = "\xFF%s" % chr(0x90 + baudRateIdx)
        debugMsg = "\nSending %s at %s baud to change baud rate" % (serialMsg, baudRates[baudRateIdx])
        serialSendEx(debugMsg, serialMsg, 1)
        prevBaudRate = baudRates[baudRateIdx]
        sleep(1.2)
        cxn1.close()
    
    # Now actually re-open this program's serial connection in the user's desired speed
    cxn1.baudrate = int(baudRates[baudRateIdx])
    print cxn1.baudrate
    cxn1.open()
    # Send the serial commands to adjust any board IDs that might be one too low
    tmp = list(boards)
    increments = [x - 1 for x in tmp[1:]]
    for boardID in increments:
        serialSendEx("", "\xFF\x82" + chr(boardID + 128), 0.001)
        serialSendEx("", "\xFF\x82" + chr(boardID + 192), 0.001)
    # Construct the message strings and find their length
    serialMsgRed.extend(makeRMessageString(richMsgs[0]))
    serialMsgGreen.extend(makeGMessageString(richMsgs[0]))
    maxCounter = len(serialMsgRed) - (len(boards) * 5)
    # Start a thread
    outputThread = serialThread()
    outputThread.start()


################################################################################
# Step 2. Load all user-defined fonts
################################################################################

# Look for all .ledfont files in the current working directory
print "\nLoading fonts..."
for filename in glob.glob("*.ledfont"):
    # Debug: Print the filename
    print filename
    # Load the font into memory
    fontfile = open(filename, 'r')
    fontname = fontfile.readline().strip()      # Read font name
    fontsupport = fontfile.readline().strip()   # Read the charset this font can support (ASCII or Unicode)
    font[fontname] = {'support': fontsupport, 'size': {}}
    # Read the charset & split it into groups by font size
    charsBySizes = fontfile.read().split(chr(29))   # ASCII 29 splits fonts of different siaes
    for sizeSet in charsBySizes:
        charDefs = sizeSet.split(chr(10))
        # The first entry designates the font size & font weight
        fontProperties = charDefs.pop(0).split(',')
        fontSize = fontProperties[0][5:]
        fontWeight = fontProperties[1][8:-1]
        font[fontname]['size'][fontSize] = {}
        font[fontname]['size'][fontSize]['weight'] = {}
        font[fontname]['size'][fontSize]['weight'][fontWeight] = {}
        # The second entry designates the spacing that should occur between characters
        spacing = charDefs.pop(0).split(": ")[1]
        # The subsequent entries designate characters
        for charDef in charDefs:
            char = charDef.split(':')
            font[fontname]['size'][fontSize]['weight'][fontWeight][char[0]] = char[1]
        # Now record the desired spacing value
        font[fontname]['size'][fontSize]['weight'][fontWeight]['spacing'] = int(spacing)
    
print "\nFont set:"
print font

# This function finds the name of all serial ports and adds them to our lists
def serial_ports(mainWindow):
    print "\nScanning for serial ports..."
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
	    print "TODO: Add this to the list:", port[0]
    
def serialSendEx(debugMsg, serialMsg, delay):
    global outputThread, evt, evtDefinition
    print debugMsg
    try:
        if outputThread.isAlive():
            # If the output thread is alive, let that thread handle the IO
            # define the message: control mode flag FF, instruction 80, chip ID 80 (chip ID doesn't matter in this case)
            evtDefinition = {'message': serialMsg, 'delay': delay}
            evt.clear()      # clear the event flag to indicate it should branch before further updates
        else:
            # Raise an exception so we send the commands over serial anyway
            raise
    except:
        global cxn1
        print "Output thread is dead.  Will now open serial port manually."
        try:
            cxn1.write(serialMsg)
        except Exception as ex:
            #print "Error writing to the selected port; perhaps it is closed.  Will try opening it.  Details:", ex
            # TODO FIXME: Port name should be determined from an array of rowNum -> COM port
            try:
                cxn = serial.Serial(mw.ui.selRow1COM.currentText())
                cxn.write(serialMsg)
            except Exception as ex:
                print "There was a problem opening the selected port (%s) and writing the desired message.  Please make sure you have a working COM port selected.\n" % mw.ui.selRow1COM.currentText()
                print "Details:", ex
                cxn.close()
                return
            print "Finished writing the desired message.\n"
            cxn.close()
        
def _updateBoards(numBoards):
    global boards
    boards.clear()              # empty the list of board indexes
    delta = 1024 / numBoards    # the auto-address line on each board should be equal to (1024 / # boards) * i
    for i in range(0, numBoards):
        boards.extend([int( delta * i / 16 )])

def isValidBoardAddress(inputContainer, lowBound=128):
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
            print "Error: Chip address \"%s\" is not valid.  The address must be a number between %d and 255 inclusive.\n" % (inputContainer.toPlainText(), lowBound)
            return None
    except Exception as ex:  # something else besides a ValueError happened, so likely the input is garbage
        print "There was a general error while making sure the chip address is numeric.  Details:", ex
        return None
    if number >= lowBound and number < 256:
        return number        # the board ID is valid (0x80 - 0xFF)
    # If we're here, the chip ID is invalid
    print "Error: Chip address \"%d\" is not valid.  The address must be between %d and 255 inclusive.\n" % (number, lowBound)
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
        
        # Set up the delay variable with the value from the UI, in case anyone changes the spin box's default value
        delay = self.ui.spinUpdateDelay.value() * 0.001

        # Connect up the UI elements to event listeners.
        # Main panels on top
        self.ui.selSpeed.activated.connect(self.updateSpeed)
        self.ui.btnConnectRow1.clicked[()].connect(lambda row=1: self.toggleRow(row))
        self.ui.btnConnectRow2.clicked[()].connect(lambda row=2: self.toggleRow(row))
        self.ui.spinUpdateDelay.valueChanged.connect(self.updateDelay)
        self.ui.spinPanelsPerRow.valueChanged.connect(self.updateBoards)
        # Raw Text panel
        self.ui.btnPush.clicked.connect(self.pushMessage)
        # Twitter Feed panel
        # Animation panel
        # Firmware panel
        self.ui.btnResetChipIDs.clicked.connect(self.resetChipIDs)
        self.ui.btnIncrementChipID.clicked[()].connect(lambda idContainer=self.ui.txtChipIDIncr: self.excrementChipID(idContainer, 1))
        self.ui.btnDecrementChipID.clicked[()].connect(lambda idContainer=self.ui.txtChipIDDecr: self.excrementChipID(idContainer, -1))
        self.ui.btnSetChipID.clicked[()].connect(lambda oldIdContainer=self.ui.txtChipIDCurrent, newIdContainer=self.ui.txtChipIDDesired: self.setChipID(oldIdContainer, newIdContainer))
        self.ui.btnShowTestPattern.clicked[()].connect(lambda idContainer=self.ui.txtTestOn: self.showTestPatternOn(idContainer))
        self.ui.btnStopGuessing.clicked.connect(lambda id=64: self.showTestPatternOn(id))
        # Simulator panel
        # Baud Rate panel
        
    def updateSpeed(self, speed):
        global baudRateIdx
        baudRateIdx = speed
        
    def toggleRow(self, rowNum):
        'When either of the connect/disconnect buttons are clicked, this method toggles the appropriate serial state'
        global cxn1, cxn2, activeConns, outputThread, exitFlag
        portName = str(self.ui.selRow1COM.currentText()) if (rowNum == 1) else str(self.ui.selRow2COM.currentText())
        
        # First, toggle the connection states
        if rowNum == 1:
            if cxn1.isOpen():
                # Close an active connection
                cxn1.close()
                activeConns -= 1
                self.ui.btnConnectRow1.setText("Connect")
            else:
                # Open a new connection at 9600 baud; we'll account for the user-defined baud rate in serialWelcome()
                cxn1 = serial.Serial(portName, 9600)
                activeConns += 1
                self.ui.btnConnectRow1.setText("Disconnect")
        elif rowNum == 2:
            if cxn2.isOpen():
                cxn2.close()
                activeConns -= 1
                self.ui.btnConnectRow2.setText("Connect")
            else:
                cxn1 = serial.Serial(portName)
                activeConns += 1
                self.ui.btnConnectRow2.setText("Disconnect")
                
        # Now, look to see if we have the required connections in place to start the matrix
        # Otherwise, stop the matrix
        
        # TODO: Don't assume we're using just one row
        if activeConns == 1:
            serialWelcome()
        elif activeConns == 0:
            exitFlag = 1;
            try:
                print "Stopping IO thread..."
                outputThread.join();
                exitFlag = 0;
                outputThread = None;
                print "IO thread stopped!"
            except AttributeError:
                print "Thread was probably already stopped"
                
    def updateDelay(self, event):
        global delay
        delay = event * 0.001
        
    def updateBoards(self, event):
        # event contains the number of boards the user says is in the matrix
        _updateBoards(event)
        
    def pushMessage(self, event):
        print event
        # TODO: Show the new message on our UI
        # Put the message on our message stack
        print "Attempting to add message:", self.ui.txtMessage.toPlainText()
        if richMsgs[0] != introMsg:
            richMsgs.append(self.ui.txtMessage.toPlainText())
        else:
            richMsgs[0] = self.ui.txtMessage.toPlainText()
        print richMsgs
        
    def resetChipIDs(self, event):
        serialSendEx("Resetting chip IDs...", "\xFF\x81\x00", 2)

    def excrementChipID(self, chipIdContainer, direction):
        # Validate the input
        chipAddr = isValidBoardAddress(chipIdContainer)
        if chipAddr is None: return
        if direction == 1:
            debugMsg = "Incrementing chip address %d..." % chipAddr
            serialSendEx(debugMsg, "\xFF\x82" + chr(int(chipAddr)), 2)
        elif direction == -1:
            debugMsg = "Decrementing chip address %d..." % chipAddr
            serialSendEx(debugMsg, "\xFF\x82" + chr(int(chipAddr)), 2)
        
    def setChipID(self, oldBoardIdContainer, newBoardIdContainer):
        # Validate the input
        oldBoardAddr = isValidBoardAddress(oldBoardIdContainer)
        newBoardAddr = isValidBoardAddress(newBoardIdContainer)
        if (oldBoardAddr is None) or (newBoardAddr is None): return
        debugMsg = "Setting board address %d to be %d..." % (oldBoardAddr, newBoardAddr)
        serialSendEx(debugMsg, "\xFF\x84" + chr(int(oldBoardAddr)) + chr(int(newBoardAddr)), 2)
        
    def showTestPatternOn(self, boardIdContainer):
        # Validate the input
        boardAddr = isValidBoardAddress(boardIdContainer)
        if boardAddr is None: return
        if (boardAddr < 64):
            debugMsg = "Showing test pattern on board ID %s (chip addresses %d and %d..." % (boardAddr, boardAddr + 128, boardAddr + 192)
            serialSendEx(debugMsg, "\xFF\x80" + chr(int(boardAddr)), 5)
        elif (boardAddr < 128):
            serialSendEx("Showing test pattern on all boards...", "\xFF\x80" + chr(int(boardAddr)), 5)
        elif (boardAddr < 256):
            debugMsg = "Showing test pattern on chip ID %s..." % boardAddr
            serialSendEx(debugMsg, "\xFF\x80" + chr(int(boardAddr)), 5)
    

################################################################################
# Step 3. Launch the app
################################################################################    

app = QApplication(sys.argv)	    
mw = MainWindow()
# Add our serial ports.
serial_ports(mw)
mw.show()
print "\nApplication is loaded."
sys.exit(app.exec_())
