from collections import deque
from PyQt5.QtCore import Qt, pyqtSignal
from LEDgoesRawTextItem import RawTextItem
import serial
import threading
# Import other windows used in our GUI
import LEDgoesConsole as console

html = u'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.0//EN" "http://www.w3.org/TR/REC-html40/strict.dtd">\n<html><head><meta name="qrichtext" content="1" /><style type="text/css">\np, li { white-space: pre-wrap; }\n</style></head><body style=" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;">\n<p style=" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;">%s</p></body></html>'
initMsgs = [html % '<span style=" color:#808000;"> :: AWAITING MESSAGES  </span>']

animTuple = None          # Tuple containing deques of each band (RGB), themselves containing a matrix of each frame
boards = deque()          # Number of boards being used in the matrix
cxn1 = serial.Serial()    # Connection for row 1
cxn2 = serial.Serial()    # Connection for row 2
cw = None                 # Console window
dw = None                 # Designer window
delay = 0                 # Amount of time to wait until updating the board with another round of serial data
evt = threading.Event()   # Thread will check if the event has gone to False, and then wait
evtDefinition = {}        # If the thread is running & the user wants to send a FW control signal, the thread will execute this string
exitFlag = 0              # Will be raised when the thread should exit
font = {}                 # Master dictionary of all font information
richMsgs = initMsgs       # Human-readable messages with formatting markers included
msgLimit = 0              # How many messages can appear on the board before they start getting kicked off
msgToOverwrite = 0        # message to attempt to overwrite if we exceed the msgLimit (will skip to the next one if sticky)
uiMsgList = 0             # reference to the message list on the UI of "Raw Text"
rowPixels = 7             # how many pixels exist in each row of a 5x7 matrix (hint: 7)

# This is the new "password" to get into Command Mode
# It consists of the ASCII for "PassWord" + 0x80 on each letter, plus 0xFF at the end
# for backward-compatibility with FW version 3.2
cmdPassword = "\xD0\xE1\xF3\xF3\xD7\xEF\xF2\xE4\xFF"


def msgIndexToOverwrite():
    global msgToOverwrite
    return msgToOverwrite

def pushMsg(source, rawMessage, richMessage, isSticky):
    global richMsgs, msgLimit, msgToOverwrite, uiMsgList
    console.cwrite("Attempting to add message: " + rawMessage)
    console.cwrite(richMessage)
    # Count how many items exist in the list now
    msgList = uiMsgList.findItems('.*', Qt.MatchRegExp)
    if len(msgList) >= msgLimit:
        # We are at or above our message limit; find one to overwrite
        written = False    # Keep track of if we've successfully overwritten a message
        # Start with the message at index "msgToOverwrite", go to the end of the list, then restart at the beginning
        msgIndexes = range(msgToOverwrite, msgLimit) + range(0, msgToOverwrite)
        for index in msgIndexes:
            if not msgList[index].sticky:    # Do not overwrite sticky messages
                formattedSource = "[%s]" % source
                formattedSource = formattedSource + " sticky" if isSticky else formattedSource
                msgList[index].setText("%s %s" % (formattedSource, rawMessage))
                msgList[index].formattedText = richMessage
                msgList[index].sticky = isSticky
                msgToOverwrite = index + 1
                written = True
                break
        if not written:
            raise Exception("Could not overwrite any messages; they are all sticky")
    else:
        # We have not exceeded the maximum message count; add the message to the UI list
        RawTextItem(richMessage, source, isSticky, uiMsgList)
    # Reconstruct the global list by pulling out "formattedText" from the UI list objects
    richMsgs = [x.formattedText for x in uiMsgList.findItems('.*', Qt.MatchRegExp)]
