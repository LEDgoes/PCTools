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
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
            
def processImage(path, results):
    size = results.size
    mode = results.mode
    # Open the image
    im = Image.open(path)
    # Get the global palette
    p = im.getpalette()
    last_frame = im.convert('RGBA')
    
    # Iterate through the entire gif
    redFrames = deque()     # collective red data
    greenFrames = deque()   # collective green data
    # Each "frame" will have a series of rows, and each row contains the data of 0-127 or 0-255
    try:
        while 1:
            redFrame = deque()     # individual frame red data
            greenFrame = deque()   # individual frame green data
            # Apply the global palette to the frame, if necessary
            if not im.getpalette():
                im.putpalette(p)
            # Store this frame in memory
            new_frame = Image.new('RGBA', im.size)
            # Apply the changes to the last image if this is a partial-mode GIF
            if mode == 'partial':
                new_frame.paste(last_frame)
            # Something...
            new_frame.paste(im, (0,0), im.convert('RGBA'))
            # Now, get the data from the image into our animation data structure
            redRow = [0] * im.size.x       # row data for 7 or 8 rows (1 panel)
            greenRow = [0] * im.size.x     # row data for 7 or 8 rows (1 panel) 
            rowNum = 6             # if the panel is 7 rows tall, set this to 6 (so we can do 2^6 later)
            for y in range(0, im.size.y):
                # Save existing deques & make new deques if row number mod panel height == 0
#                if y % 7 == 0 and y != 0:
#                    redFrame.extend(redRow)
#                    greenFrame.extend(greenRow)
#                    redRow = [0] * im.size.x
#                    greenRow = [0] * im.size.x
#                    rowNum = 6
                # Add the image data to the redRow & greenRow deques
                for x in range(0, im.size.x):
                    #redRow |= (1 << rowNum) if im[x, y] == 456
                    pass
            # Go on to the next frame
            last_frame = new_frame
            im.seek(im.tell()+1)
    except EOFError:
        pass # end of sequence