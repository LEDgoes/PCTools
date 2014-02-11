'''
Welcome to the LEDgoes PC Tools!  This file features inialization of the fonts and UI.

To recompile any changes to the UI, run at the command prompt:
pyuic5 -o LEDgoesForm.py "C:\Users\Stephen\Documents\LEDgoes PC Interface.ui"
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
from serial.tools import list_ports
# import this to help find fonts
import glob

################################################################################
# Step 0. Define the serial thread routine, since evidently I can't put this in a separate file w/o circular dependencies
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
serialMsgRed = deque()    # Red-only data translated into serial format for direct output
serialMsgGreen = deque()  # Green-only data translated into serial format for direct output

def writeString(procId):
    # Import global variables
    global serialMsgRed, serialMsgGreen, cxn1, cxn2
    # Figure out what serial port to use
    rows = 1
    #if rows == 2 and not multiplexed:   # With 2 rows in use & no demultiplexer, pick between the 2 active serial conns
    #    cxnRef = (offset % 0x02 == 0) ? cxn1 : cxn2;    # even chips are the top row, odd chips are the bottom row
    #else:             # With only 1 row, or 3+ rows, use just one serial conn (3+ requires the demuxer)
    cxnRef = cxn1
    # Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
    adjustment = (procId / rows) * 5;
    # Grab the 5 columns, shift if necessary, and save it into an actual byte array
    #shift = (offset % rows) * 7
    shift = 0
    rPart = chr(procId | 0x80)
    gPart = chr(procId | 0xC0)
    for i in range(5):
        index = counter + adjustment + i
        # How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
        try:
            rPart += chr((serialMsgRed[index] >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            print "writeString: Index error at index " + str(index)
        #if (index > 0x10) { rPart[i] = (byte) (rPart[i] & 0x1F); }
        try:
            gPart += chr((serialMsgGreen[index] >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            print "writeString: Index error at index " + str(index)
    #if (index > 0x10) { gPart[i] = (byte) (gPart[i] & 0xFC); }
    # Write red portion
    print "Connection is open? "
    cxn1.write(rPart)
    # Write green portion
    cxn1.write(gPart)
    # Now just sleep for a wee bit before we go to the next character column
    sleep(0.004)

def makeRMessageString(message):
    global serialMsgRed
    'Make the message to appear in Red'
    ### BIG TODO: This needs to APPEND to the deque, NOT overwrite it!!!
    serialMsgRed = makeMessageString(message, "red")

def makeGMessageString(message):
    global serialMsgGreen
    'Make the message to appear in Green'
    ### BIG TODO: This needs to APPEND to the deque, NOT overwrite it!!!
    serialMsgGreen = makeMessageString(message, "green")

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
        serialMsg.extend([0, 0, 0, 0, 0])    # add padding to the left of the message
        for character in subMessage:
            # Map the current letter to something that appears in the font
            try:
                serialMsg.extend( font['LEDgoes Default Font']['size']['1']['weight']['4'][character] )
            except KeyError:
                serialMsg.extend([0, 0, 0, 0, 0])
                print "Character " + character + " unknown; substituting with whitespace"
    return serialMsg
    
class serialThread (threading.Thread):
    def __init__(self):
        super(serialThread, self).__init__()
        print "IO Thread is now running; when it stops may not necessarily be advertised..."
    
    def run(self):
        global counter, exitFlag
        while not exitFlag:  # mind you, this is the implementation coming straight from the firmware ;)
            # WRITING THE MESSAGE ON THE BOARD
            for i in range(boards):           # iterate through the amount of characters we have on the board
                procId = i                    # Each processor looks for its own special "code"
                writeString(procId)           # Write the portion of the string pertaining to the active processor
            counter += 1                      # Now go on to show the next character column
            # MESSAGE EXPIRATION
            if counter >= len(serialMsgRed):  # If we've reached the end of the message,
                counter = 0                   # reset the column counter to 0
                serialMsgRed.clear()          # reset the red string to empty
                serialMsgGreen.clear()        # reset the green string to empty
                for msg in richMsgs:
                    #emptyString = new String(' ', messages[i].Length);  // Make an empty string equal in length to the current message
                    #redString += ((i % 2 == 0) ? messages[i] : emptyString) + "  ";     // set the red string
                    #greenString += ((i % 2 != 0) ? messages[i] : emptyString) + "  ";   // set the green string
                    #greenString += messages[i] + "  ";     // set the red string
                    #redString += messages[i] + "  ";   // set the green string
                    serialMsgRed += makeRMessageString(msg)
                    serialMsgGreen += makeGMessageString(msg)

                    
################################################################################
# Step 1. Define important variables & functions & import user-defined modules
################################################################################

richMsgs = []             # Human-readable messages with formatting markers included
richMsgs.append(" :: AWAITING MESSAGES ")
counter = 0               # Stores how far into the message the board's first LED column needs to display
cxn1 = serial.Serial()    # Connection for row 1
cxn2 = serial.Serial()    # Connection for row 2
activeConns = 0           # How many active serial connections are going on
outputThread = None       # Reference to thread running the serial IO code
rows = 1                  # Number of rows of panels in the display
font = {}                 # Master dictionary of all font information
boards = 8                # Number of boards being used in the matrix

# Import other modules & methods

def serialWelcome():
    global cxn1
    serialMsgRed = makeRMessageString(richMsgs[0])
    serialMsgGreen = makeGMessageString(richMsgs[0])
    print "Serial port is open?"
    print cxn1.isOpen()
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
        spacing = charDefs.pop(0)[9:0]
        # The subsequent entries designate characters
        for charDef in charDefs:
            char = charDef.split(':')
            font[fontname]['size'][fontSize]['weight'][fontWeight][char[0]] = char[1]
        # Now record the desired spacing value
        font[fontname]['size'][fontSize]['weight'][fontWeight]['spacing'] = spacing
    
print "\nFont set:"
print font

# This function finds the name of all serial ports and adds them to our lists
def serial_ports(mainWindow):
    print "\nScanning for serial ports..."
    if os.name == 'nt':
        # windows
        for i in range(256):
            try:
                s = serial.Serial(i)
                mainWindow.ui.selRow1COM.addItem("COM" + str(i + 1))
                mainWindow.ui.selRow2COM.addItem("COM" + str(i + 1))
                s.close()
            except serial.SerialException as ex:
                pass
    else:
        # unix
        for port in list_ports.comports():
	    print "TODO: Add this to the list:", port[0]


# This class represents our main window, and runs functions to initialize it
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from Designer.
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Make some local modifications.
        self.ui.selSpeed.addItem("9600")
        self.ui.selSpeed.addItem("19200")
        self.ui.selSpeed.addItem("38400")
        self.ui.selSpeed.addItem("57600")
        self.ui.selSpeed.addItem("115200")
        self.ui.selSpeed.addItem("230400")

        # Connect up the buttons.
        self.ui.btnConnectRow1.clicked[()].connect(lambda row=1: self.toggleRow(row)) 
        self.ui.btnConnectRow2.clicked[()].connect(lambda row=2: self.toggleRow(row)) 
        
    def toggleRow(self, rowNum):
        'When either of the connect/disconnect buttons are clicked, this method toggles the appropriate serial state'
        global cxn1, cxn2, activeConns, outputThread, exitFlag
        portName = str(self.ui.selRow1COM.currentText()) if (rowNum == 1) else str(self.ui.selRow2COM.currentText())
        
        # First, toggle the connection states
        if rowNum == 1:
            if cxn1.isOpen():
                cxn1.close()
                activeConns -= 1
                self.ui.btnConnectRow1.setText("Connect")
            else:
                cxn1 = serial.Serial(portName)
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