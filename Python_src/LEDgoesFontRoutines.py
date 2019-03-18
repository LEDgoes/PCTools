import math

def readOfSize(size, signed=False):
    bytes = fo.read(size)
    string = "".join([format(ord(char), "x").zfill(2) for char in bytes])
    val = int(string, 16)
    if not signed:
        return val
    bits = size * 8
    if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bits)        # compute negative value
    return val                         # return positive value as is

def readByte(fo, signed=False):
    return readOfSize(1, signed)

def readShort(fo, signed=False):
    return readOfSize(2, signed)

def readLong(fo, signed=False):
    return readOfSize(4, signed)

def findTable(tableName):
    fo.seek(0)
    # TODO: PUT IN ERROR HANDLING (EOF)
    # AND PARSE THE TABLE DIRECTORY
    while True:
        str = fo.read(4)
        if str == tableName.lower() or str == tableName.upper():
            fo.seek(fo.tell() + 4)
            return readLong(fo)

def getNumberOfHMetrics():
    fo.seek(findTable("hhea") + 34)
    return readShort(fo)

def getWidestHMetric():
    numberOfHMetrics = getNumberOfHMetrics()
    fo.seek(findTable("hmtx"))
    widest = 0
    for i in range(0, numberOfHMetrics):
        advanceWidth = readShort(fo)
        widest = advanceWidth if advanceWidth > widest else widest
        fo.seek(fo.tell() + 2)
    return widest

def getHeight():
    fo.seek(findTable("OS/2") + 68)
    sTypoAscender = readShort(fo, True)
    sTypoDescender = abs(readShort(fo, True))
    return sTypoAscender + sTypoDescender + 0.0

def getMaxFontSize():
    ppiScale = 96.0 / 72.0
    unitsPerEm = 2048.0
    marqueeHeight = 14
    scale = (getHeight() / ppiScale) * marqueeHeight / unitsPerEm
    return round(scale, 1)

def getImageSizeFor(str):
    fontSize = 10.0
    unitsPerEm = 2048.0
    ppiScale = 96.0 / 72.0
    scalingFactor = fontSize * ppiScale / unitsPerEm
    from ttfquery import describe, glyphquery
    myfont = describe.openFont("C:\\Windows\\Fonts\\arial.ttf")
    width = 0
    widestWidth = getWidestHMetric() * scalingFactor
    for char in str:
        try:
            print "Width of char %s: %f" % (char, (glyphquery.width(myfont, char) * scalingFactor))
            width += glyphquery.width(myfont, char) * scalingFactor
        except:
            print "Exception thrown on", char
            width += widestWidth
        print "Total width:", width
    height = getHeight() * scalingFactor
    return (int(math.ceil(width)), int(math.ceil(height)))

def makeImageOf(str):
    textImage = Image.new("RGB", getImageSizeFor(str), (0,0,0))
    textCanvas = ImageDraw.Draw(textImage)
    textCanvas.fontmode = "1"
    font = ImageFont.truetype("C:\\Windows\\Fonts\\arial.ttf", 10)
    textCanvas.text((0, 0), str, (255,255,0), font=font)
    textImage.save("text.bmp")