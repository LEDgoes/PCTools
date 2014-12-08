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
# so we can sort globals.boards in our desired manner:
from operator import itemgetter
# now import our own libraries
import LEDgoesGlobals as globals
# Import the window used for helping debug the marquee & the software
import LEDgoesConsole as console

errFlag = False           # If we've seen COM port errors, toggle this
frames = deque()          # we update the marquee with "frames" after the update delay timer ticks

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

    # Find out how many rows exist in the selected font & size
    rows = globals.font['LEDgoes Default Font']['size'][7]['weight'][4]['spacing']
    # Make that many rows of serialMsg
    serialMsg = [deque() for i in range(0, rows)]
    # Make the message string from the letters
    # TODO: Allow an optional amount of padding before the message is shown
    for d in serialMsg:
        d.extend(["\x00", "\x00", "\x00", "\x00", "\x00"])    # add padding to the left of the message
    for character in subMessage:
        # Map the current letter to something that appears in the font
        for r in range(0, rows):
            try:
                # Add the prescribed row of the prescribed character
                serialMsg[r].extend( globals.font['LEDgoes Default Font']['size'][7]['weight'][4][character][r] )
            except KeyError:
                serialMsg[r].extend(["\x00", "\x00", "\x00", "\x00", "\x00"])
                console.cwrite("Character " + character + " unknown; substituting with whitespace")
        # Insert spacing between characters
        for r in range(0, rows):
            try:
                # Add the prescribed spacing between characters for this font
                serialMsg[r].extend(['\x00'] * globals.font['LEDgoes Default Font']['size'][7]['weight'][4]['spacing'])
            except:
                # Tell the user there was a problem
                console.cwrite("Character spacing is unknown for this font; assuming 0")
    return serialMsg

def makeMessageStringFromFont(message, color):
    # Make the string in the prescribed font
    from PIL import Image, ImageDraw, ImageFont
    import LEDgoesImageRoutines
    textImage = Image.new("RGB", (50, 25), (0,0,0))
    textCanvas = ImageDraw.Draw(textImage)
    textCanvas.fontmode = "1"     # this turns off anti-aliasing
    font = ImageFont.truetype("C:\\Windows\\Fonts\\arialbd.ttf", 18)
    txt = " FIVE "
    textCanvas.text((0, 0), txt, (255,255,0), font=font)
    # Do thresholding on the image so only pixels bright enough will show the desired color
    bands = Image.eval(textImage, LEDgoesImageRoutines.doThreshold)
    # find the bounding box (smallest rectangle) around the text that was drawn
    bbox = bands.getbbox()
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    pd = list(bands.crop(bbox).getdata())
    # break pixelData down into rows
    pixelData = [pd[x:x + width] for x in xrange(0, len(pd), width)]
    # FIXME: This only gets the first channel (Red) from pixelData
    pixelData = [[d[0] for d in r] for r in pixelData]
    # Reverse the pixelData list so the bottom row comes first; top row comes last; and we can append spacing if needed
    pixelData.reverse()
    if height % 7 != 0:
        pixelData.extend([[0] * len(pixelData[0]) for i in range(height % 7, 7)])
        height = len(pixelData)
    # And now, time for one helluva list comprehension...
    # This beast takes data presented in rows, turns it into columns with maximum height 7, then adds up the column value given by (isItOn_i * (1 << i))
    colData = [[chr(sum([pixelData[r][c] * (1 << (r % 7)) for r in range(s,s+7)])) for c in range(0, len(pixelData[0]))] for s in xrange(0, height, 7)]
    print colData
    # Add one spacer column at the end
    serialMsg = [deque(d) for d in colData]
    for r in range(0, len(serialMsg)):
        serialMsg[r].append(chr(0))
    return serialMsg    

class serialThread (threading.Thread):
    def __init__(self):
        # Carry out the rest of the "serial welcome" here by posting initial messages: default is "Awaiting Messages"
        updateMessages()
        # Start the thread
        super(serialThread, self).__init__()
        console.cwrite("IO Thread is now running; when it stops may not necessarily be advertised...")
    
    def run(self):
        global errFlag, frames
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
            for frame in frames:      # iterate through each frame of the "text animation"
                try:                  # write the frame to the marquee
                    # TODO: This had to change recently
                    #       Join the chars in frame ahead of time to optimize this
                    globals.cxn1.write(''.join([chr(ord(char)) for char in frame]))
                except Exception as e:               # something unexpected happened
                    console.cwrite("Serial communication disconnected")
                    errFlag = True
                    break
                # Now just sleep for a wee bit before we go to the next character column
                sleep(globals.delay)
            # MESSAGE EXPIRATION
            console.cwrite("Updating messages...\n")
            updateMessages()
            
def updateMessages():
    global frames
    # NOTE: This is where we used to print messages to the console.  If we want to do this again, put it here
    serialMsgRed = []             # array holds deques containing red pixel data for all messages
    serialMsgGreen = []           # array holds deques containing green pixel data for all messages
    for msg in globals.richMsgs:
        # Fill the new data structures with pixel data
        zipMessageString(makeRMessageString(msg), serialMsgRed)
        zipMessageString(makeGMessageString(msg), serialMsgGreen)
        #zipMessageString(makeMessageStringFromFont(msg, "red"), serialMsgRed)
        #zipMessageString(makeMessageStringFromFont(msg, "green"), serialMsgGreen)
    # Make the frames
    frames.clear()
    for f in range(0, len(serialMsgRed[0])):
        frame = deque()
        # each board has an x & y assigned by the "marquee arrangement" UI; sort the boards by y first then x
        # this will help ensure a nice, smooth scrolling effect (assuming we aren't scrolling top-down)
        sortedBoards = sorted(globals.boards, key=itemgetter(0, 1))
        for b in sortedBoards:
            # b[0] := x with respect to the marquee; b[1] = y; b[2] = board index
            # b[0] + f := x with respect to the whole message
            # add the board address of the red chip and its data to the serial message
            x = b[0] * 5
            frame.extend( chr(int(b[2] + 128)) )
            frame.extend(list( serialMsgRed[b[1]] )[ x + f : x + f + 5 ] )
            # add the board address of the green chip and its data to the serial message
            frame.extend( chr(int(b[2] + 192)) )
            frame.extend(list( serialMsgGreen[b[1]] )[ x + f : x + f + 5 ])
        # don't forget to add the completed work to the deque of frames :-P
        frames.append(frame)
            
def zipMessageString(new, messages):
    # handle the special case if messages is empty
    if len(messages) == 0:
        for row in range(0, len(new)):
            messages.append(new[row])
        return
    # we did that because the first message would always look weird if higher rows always get shifted
    # here's the usual case:
    for row in range(0, len(new)):
        # for each row in the "new" messages,
        try:
            # extend the existing messages' row with the data from the new message
            messages[row].extend(new[row])
        except IndexError:
            # the row doesn't exist yet in the existing messages, so make it.
            try:
                # Pad it with \x00s so the letters will remain coherent if we have taller fonts than last time
                # Chances are that row 0 (the bottom) has been made already
                messages.append(deque(['\x00'] * len(messages[0])))
                messages.append(new[row])
            except IndexError:
                console.cwrite("There was a problem extending the message contents.")

