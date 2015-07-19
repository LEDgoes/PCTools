# BriteBlox RSS Parser
# v0.0.1
# Currently, this only parses the NASDAQ RSS feed for stock quotes

import LEDgoesGlobals as globals    # Global variables this module should know about
import LEDgoesConsole as console    # Used to debug the marquee & the software
import xml.etree.ElementTree as ET  # Element tree to parse the RSS feed & any other XML it might contain
import feedparser                   # This fetches an RSS feed
import re                           # Regex to help with splitting list of stocks on [ ,]
import threading                    # Allows to run this off the main UI thread and do wait signaling
from time import sleep              # Don't spin-lock the CPU

setColor = '\n<span style="color:#%s;">'
endColor = '</span>'
red = '800000'
green = '008000'
yellow = '808000'
counter = 0
stockInstance = None


# Handle button click for "Get Quotes" from the main UI
def toggleQuotes(tickerString):
    global stockInstance
    if len(tickerString) == 0:
        console.cwrite("You must enter at least one ticker symbol in order to use this feature.")
        return
    # For now, treat this as a static class (one instance)
    # TODO: Make a mechanism to handle toggling multiple class instances
    # Initialize a new instance of the Nasdaq RSS feed
    if stockInstance is not None:
        stockInstance.active = False
        stockInstance.join()
        stockInstance = None
        console.cwrite("Stock quote thread terminated.")
    else:
        stockInstance = stockThread(tickerString)
        stockInstance.setDaemon(True)
        stockInstance.start()

# Each stockThread object will fetch up to 10 quotes and update the scrolling message JIT (just-in-time)
class stockThread (threading.Thread):
    def __init__(self, tickerString):
        # Find out if there is enough space in the message list to start this thread
        # Start the thread; call it active, and register the event
        super(stockThread, self).__init__()
        self.active = True
        self.evt = threading.Event()
        self.evt.set()
        globals.asyncEvts.append(self.evt)
        # TODO: Add an item to the main UI list to show that this is taking place
        # FIXME: For now, this will be Message #1
        stocks = re.split(" |,", tickerString)
        stocks = filter(None, stocks)
        if len(stocks) < 1:
            console.cwrite("You did not enter any valid ticker symbols.")
            return;
        self.feedURL = 'http://www.nasdaq.com/aspxcontent/NasdaqRSS.aspx?data=quotes&symbol=%s' % ("&symbol=".join(stocks))
        console.cwrite("Stock quote thread is now running...")
    
    def run(self):
        while self.active:  # The user can toggle if this RSS feed is actively being read
            sleep(1)
            if not self.evt.is_set():
                # Get the feed, and massage it so we can parse it
                # TODO: use the user's desired quotes
                console.cwrite("Stock quote thread: Fetching quotes...")
                d = "dummy"
                try:
                    d = feedparser.parse(self.feedURL)
                except:
                    console.cwrite("There was an error in fetching the requested RSS document.")
                    self.active = False
                    continue
                info = []
                feed = "<body>%s</body>" % d.entries[0].summary_detail.value.replace("&nbsp;", "")
                tree = ET.ElementTree(ET.fromstring(feed))
                root = tree.getroot()
                # Find the last updated time
                last = root.find(".//table[@width='180']/tr/td")
                info.append("%s%s  %s" % ((setColor % yellow), last.text.strip(), endColor))
                # Find all the quotes
                counter = 0
                for elem in root.findall(".//table[@width='200']"):
                    for elem2 in elem.findall(".//td"):
                        for text in elem2.itertext():
                            idx = counter % 13
                            if idx == 0:  # Ticker symbol
                                info.append("%s%s " % ((setColor % yellow), text.strip()))
                            if idx == 3:  # Last trade
                                info.append("%s %s" % (text.strip(), endColor))
                            if idx == 5:  # Change sign
                                sign = text.strip()
                                info.append("%s%s" % ((setColor % (green if sign == "+" else red)), sign))
                            if idx == 6:  # Change amount
                                info.append("%s %s" % (text.strip(), endColor))
                            counter += 1
                # We're done parsing, so join everything together
                newMessage = globals.html % ''.join(info)
                # FIXME: For now, this will be Message #1
                globals.richMsgs[0] = newMessage
                self.evt.set()
        # After the while loop terminates, remove references to the event
        globals.asyncEvts.remove(self.evt)

