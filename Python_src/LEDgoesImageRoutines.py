from collections import deque
import LEDgoesGlobals as globals
import math
from PIL import Image
import threading
from time import sleep
# Import the window used for helping debug the marquee & the software
import LEDgoesConsole as console

def doThreshold(pixel):
    return 1 if pixel > 127 else 0

def analyzeImage(path):
    im = Image.open(path)
    results = {
        'size': im.size,
        'mode': 'full',
    }
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results['mode'] = 'partial'
                    return results
            im.seek(im.tell() + 1)
    except EOFError:
        console.cwrite("Unexpected end of file in your GIF.  Your image does not conform to GIF 87a or 89a, or could be corrupt.")
        return
    except:
        console.cwrite("Unhandled exception while parsing GIF animation.")
        return

def processImage(path, results):
    console.cwrite("Incoming results: %s" % results)
    size = results['size']
    mode = results['mode']
    # Open the image
    im = Image.open(path)
    # Convert to RGBA so we can do mathematical processing easier
    last_frame = im.convert('RGBA')

    # Iterate through the entire gif
    redFrames = deque()     # collective red data
    greenFrames = deque()   # collective green data
    # Each "frame" will have a series of rows, and each row contains the data of 0-127 or 0-255
    try:
        while 1:
            console.cwrite("Analyzing frame %d" % im.tell())
            # make a couple new frames
            # FIXME: 7 is a magic number designating the number of rows per board
            rowsPerBoard = 7
            # size[0] = width, size[1] = height
            rowsOfBoards = int(math.ceil(1.0 * results['size'][1] / rowsPerBoard))
            redFrame = [ [ 0 for i in range(rowsOfBoards) ] for j in range(results['size'][0]) ]
            greenFrame = [ [ 0 for i in range(rowsOfBoards) ] for j in range(results['size'][0]) ]
            # Apply the global palette to the frame, if necessary
            if not im.getpalette():
                im.putpalette(p)
            # Store this frame in memory
            new_frame = Image.new('RGBA', im.size)
            # Apply the current "partial" frame to the last frame if this is a partial-mode GIF
            if mode == 'partial':
                new_frame.paste(last_frame)
            # Paste the current frame of the GIF onto the blank canvas
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            # Run analysis on each band of each pixel to decide if it should be illuminated
            bands = Image.eval(new_frame, doThreshold)
            # This makes a list of tuples containing the results: 4 channels, 1 if illuminated, 0 if not
            colorPresent = list(bands.getdata())
            
            board = 0          # which row of boards we're concerned with
            yOnBoard = 0       # which row we're accessing w.r.t. the current board
            # along the x axis of the image...
            for x in range(0, new_frame.size[0]):
                # Reset variables
                yOnBoard = 0
                board = 0
                # Add the image data to the redRow & greenRow deques from along the y axis
                #print redFrame, greenFrame
                for y in range(new_frame.size[1] - 1, -1, -1):
                    pix = (y * new_frame.size[0]) + x
                    # Red band
                    if colorPresent[pix][0] == 1:
                        redFrame[x][board] |= (1 << yOnBoard)
                    # Green band
                    if colorPresent[pix][1] == 1:
                        greenFrame[x][board] |= (1 << yOnBoard)
                    # If we cared about the blue band, we would call on colorPresent[pix][2]
                    yOnBoard += 1
                    if yOnBoard >= rowsPerBoard:
                        yOnBoard = 0
                        board += 1

            # Add the converted frames to the respective deques
            redFrames.extend(redFrame)
            greenFrames.extend(greenFrame)
            # Go on to the next frame
            last_frame = new_frame
            im.seek(im.tell()+1)
    except EOFError:
        # return a tuple containing the deques of redFrames & greenFrames
        console.cwrite("Final length: %d * %d" % (len(redFrames), len(greenFrames)))
        return (redFrames, greenFrames)

        

class animationThread (threading.Thread):
    def __init__(self):
        super(animationThread, self).__init__()
        console.cwrite("Animation thread is now running; when it stops may not necessarily be advertised...")
    
    def run(self):
        currentCel = 0;
        
        # TODO FIXME
        #boards = deque([0, 7, 15, 23, 39, 47, 55, 63])
        boards = deque([56, 57, 58, 59, 60, 61, 62, 63])
        
        # Find out a little bit more about the frames & bands present
        console.cwrite("Num bands: %d" % len(globals.animTuple))
        totCols = len(globals.animTuple[0])          # The deque stores each frame continuously along the x axis
        console.cwrite("Total # of columns: %d" % totCols)
        boardRows = len(globals.animTuple[0][0])     # Number of rows of boards in the animation
        console.cwrite("Height in boards: %d" % boardRows)
        while not globals.exitFlag:  # mind you, this is the implementation coming straight from the firmware ;)
            # CHECKING FOR CONTROL MESSAGES
            if not globals.evt.is_set():
                globals.cxn1.write(globals.evtDefinition['message'])
                try:      # if a delay has been set, sleep for that length of time
                    sleep(globals.evtDefinition['delay'])
                    globals.evt.set()
                except:   # otherwise, do not resume until an external event happens which resets the event flag
                    globals.evt.wait()
            # WRITING THE MESSAGE ON THE BOARD
            # FIXME: 20 is a magic number describing the width of LEDgoes_anim.gif (the Pacman animation)
            x = 20 * currentCel
            for board in range(0, len(boards)):
                row = 0 if board < 4 else 1
                rPart = chr(boards[board] | 0x80)
                gPart = chr(boards[board] | 0xC0)
                myRange = range(x, x + 5) # if row % 2 == 0 else range(x - 5, x)
                for i in myRange:
                    try:
                        rPart += chr(globals.animTuple[0][i][row])
                    except IndexError:
                        rPart += '\x00'
                    try:
                        gPart += chr(globals.animTuple[1][i][row])
                    except IndexError:
                        rPart += '\x00'
                globals.cxn1.write(rPart)
                globals.cxn1.write(gPart)
                # This next line is only important if we have only one COM port per line
#                if row == 0:
                x += 5
#                elif row == 1:
#                    x -= 5
            # GOING TO THE NEXT FRAME
            # FIXME: 140 is how many frames are in LEDgoes_anim.gif (the Pacman animation)
            currentCel = (currentCel + 1) % 140
            sleep(globals.delay)
