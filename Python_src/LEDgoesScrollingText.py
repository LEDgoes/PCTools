# import deque from collections since it should be faster than using a standard list
from collections import deque
# import the capability to pause the thread so we don't go off the rails scrolling as fast as possible
from time import sleep
# import threading so our I/O isn't on the UI thread
import threading
# import regular expressions so we can pull out the color from our rich text input
import re
# import XML so we can parse the element tree for each rich text we send to the matrix
import xml.etree.ElementTree as ET
# now import our own libraries
import LEDgoesGlobals as globals
# Import the window used for helping debug the marquee & the software
import LEDgoesConsole as console

counter = 0               # Stores how far into the message the board's first LED column needs to display
maxCounter = 0            # How far the scrolling message can advance without hitting errors
errFlag = False           # If we've seen COM port errors, toggle this
serialMsgRed = deque()    # Red-only data translated into serial format for direct output
serialMsgGreen = deque()  # Green-only data translated into serial format for direct output

def writeString(boardsIdx):
    # Import global variables
    global errFlag, serialMsgRed, serialMsgGreen
    # Figure out what serial port to use
    rows = 1
    #if rows == 2 and not multiplexed:   # With 2 rows in use & no demultiplexer, pick between the 2 active serial conns
    #    cxnRef = (offset % 0x02 == 0) ? globals.cxn1 : globals.cxn2;    # even chips are the top row, odd chips are the bottom row
    #else:             # With only 1 row, or 3+ rows, use just one serial conn (3+ requires the demuxer)
    cxnRef = globals.cxn1
    # Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
    adjustment = (boardsIdx / rows) * 5;
    # Grab the 5 columns, shift if necessary, and save it into an actual byte array
    #shift = (offset % rows) * 7
    shift = 0
    rPart = chr(globals.boards[boardsIdx] | 0x80)
    gPart = chr(globals.boards[boardsIdx] | 0xC0)
    for i in range(5):
        index = counter + adjustment + i
        # How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
        try:
            rPart += chr((ord(serialMsgRed[index]) >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            console.cwrite("writeString: Index error at index " + str(index))
        #if (index > 0x10) { rPart[i] = (byte) (rPart[i] & 0x1F); }
        try:
            gPart += chr((ord(serialMsgGreen[index]) >> shift) & 0x7F)
        except IndexError:
            rPart += chr(0)
            console.cwrite("writeString: Index error at index " + str(index))
    #if (index > 0x10) { gPart[i] = (byte) (gPart[i] & 0xFC); }

    try:
        # Write red portion
        globals.cxn1.write(rPart)
        # Write green portion
        globals.cxn1.write(gPart)
    except:
        console.cwrite("Serial communication disconnected")
        errFlag = True

def makeRMessageString(message):
    'Construct & return the message to appear in Red'
    return makeMessageString(message, 0x800000)   # hex value for dark red

def makeGMessageString(message):
    'Construct & return the message to appear in Green'
    return makeMessageString(message, 0x008000)   # hex value for dark green

def makeMessageString(message, panelColor):
    # TODO FIXME: Rows needs to be dynamic based on number of open COMs
    rows = 1
    # Initialize subMessage as empty
    subMessage = ""
    serialMsg = deque()
    # Find out which color we need to make the message in
    tree = ET.ElementTree(ET.fromstring(message))
    body = tree.find("body")
    # Iterate through each element in the html <body> tag
    for element in body.iter():
        # Parse out the <span style=' color=#{this is what we want};'>
        segmentColor = re.search(r'color\:\#([0-9a-fA-F]{6})', element.attrib['style'], flags=re.S)
        if segmentColor is None:
            continue    # the element was the <body> tag itself
        segmentColor = int(segmentColor.group(1), 16)
        # find out if the font color in the rich text box matches the deque whose color we're making now
        # Default red is 0xFF0000, default yellow is 0x808000, and default green is 0x008000.  Default blue would probably be 0x0000FF.
        # The point is the high bit is always set when the text is a default color.
        # The lower bits are only set if a special arrangement is desired -- e.g. 0x1F7C00 would be bottom 2 rows red, top 2 rows green, and middle rows yellow
        if (panelColor & segmentColor == panelColor):
            # "rich text" color is set to contain this panel's color completely (i.e. no special pattern)
            subMessage += element.text
        else:  #if (panelColor & segmentColor == 0):
            # "rich text" color is not set to contain this panel's color at all
            subMessage += " " * (element.text.__len__())
        #else:
            # this color is set for specific rows, not the whole matrix
        #    pass

    # Make the message string from the letters
    if (rows == 1):
        # Each character takes up 5 columns plus 1 spacer; each board is 5 columns wide
        serialMsg.extend(["\x00", "\x00", "\x00", "\x00", "\x00"])    # add padding to the left of the message
        for character in subMessage:
            # Map the current letter to something that appears in the font
            try:
			    # Add the prescribed character
                serialMsg.extend( globals.font['LEDgoes Default Font']['size'][7]['weight'][4][character] )
            except KeyError:
                serialMsg.extend(["\x00", "\x00", "\x00", "\x00", "\x00"])
                console.cwrite("Character " + character + " unknown; substituting with whitespace")
            # Insert spacing between characters
            try:
				# Add the prescribed spacing between characters for this font
                serialMsg.extend(['\x00'] * globals.font['LEDgoes Default Font']['size'][7]['weight'][4]['spacing'])
            except:
                # Add one space
                console.cwrite("Character spacing is unknown for this font; assuming 0")
    return serialMsg

def makeMessageStringFromFont(message, color):
    pass
    
class serialThread (threading.Thread):
    def __init__(self):
        # Carry out the rest of the "serial welcome" here by indicating "Awaiting Messages"
        serialMsgRed.extend(makeRMessageString(globals.richMsgs[0]))
        serialMsgGreen.extend(makeGMessageString(globals.richMsgs[0]))
        maxCounter = len(serialMsgRed) - (len(globals.boards) * 5)
        # Start the thread
        super(serialThread, self).__init__()
        console.cwrite("IO Thread is now running; when it stops may not necessarily be advertised...")
    
    def run(self):
        global errFlag, counter, serialMsgRed, serialMsgGreen, maxCounter
        errFlag = False
        while not globals.exitFlag:  # mind you, this is the implementation coming straight from the firmware ;)
            # CHECKING FOR CONTROL MESSAGES
            if not globals.evt.is_set():
                globals.cxn1.write(globals.evtDefinition['message'])
                try:      # if a delay has been set, sleep for that length of time
                    sleep(globals.evtDefinition['delay'])
                    globals.evt.set()
                except:   # otherwise, do not resume until an external event happens which resets the event flag
                    globals.evt.wait()
            # STOP RUNNING SERIAL COMMANDS ON AN ERROR (TODO: make this more elegant)
            if errFlag:
                continue
            # WRITING THE MESSAGE ON THE BOARD
            for i in range(len(globals.boards)):      # iterate through the amount of characters we have on the board
                procId = i                    # Each processor looks for its own special "code"
                writeString(procId)           # Write the portion of the string pertaining to the active processor
            counter += 1                      # Now go on to show the next character column
            # MESSAGE EXPIRATION
            if counter > maxCounter:          # If we've reached the end of the message,
                console.cwrite("Updating messages...\n")
                # NOTE: This is where we used to pring out the messages... If we want to do this again, put it here
                counter = 0                   # reset the column counter to 0
                serialMsgRed.clear()          # reset the red string to empty
                serialMsgGreen.clear()        # reset the green string to empty
                for msg in globals.richMsgs:
                    serialMsgRed.extend(makeRMessageString(msg))
                    serialMsgGreen.extend(makeGMessageString(msg))
                    maxCounter = len(serialMsgRed) - (len(globals.boards) * 5)
            # Now just sleep for a wee bit before we go to the next character column
            sleep(globals.delay)