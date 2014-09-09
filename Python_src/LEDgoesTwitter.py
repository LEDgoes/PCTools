import LEDgoesGlobals as globals
import threading
import twitter
# Import the window used for helping debug the marquee & the software
import LEDgoesConsole as console

twitterEvt = threading.Event()   # Thread will check if the event has gone to False, and then wait
twitterEvt.set()                 # Standard Python events allow threads to continue running if event flag is set


class twitterStreamThread (threading.Thread):
    def __init__(self):
        super(twitterStreamThread, self).__init__()
        console.cwrite("Twitter thread is now running; when it stops may not necessarily be advertised...")
    
    def run(self):
        global twitterApi, twitterProperties, twitterEvt
        maxTweets = 10
        curIndex = 0
        for item in twitterApi.GetStreamFilter(track=[twitterProperties]):
            if item.has_key('text'):
                try:
                    # Output all Tweets including language
                    console.cwrite("===== %s " % item['lang'])
                    console.cwrite(item['text'])
                    # Display only English tweets (change as you see fit)
                    if item['lang'] == "en":
                        rawTweetText = '@%s %s' % (item['user']['screen_name'], item['text'])
                        formattedTweetText = '<span style=" color:#ff0000;">@%s </span><span style=" color:#808000;">%s</span>' % (item['user']['screen_name'], item['text'])
                        globals.pushMsg("twitter", rawTweetText, globals.html % formattedTweetText, False)
                except Exception as ex:
                    console.cwrite(ex)
            if not twitterEvt.is_set():
                console.cwrite("Twitter stream shut down!")
                twitterEvt.set()
                return


def twitterAuth(apiKey, apiSecret, tokenKey, tokenSecret):
    global twitterApi
    twitterApi = twitter.Api(consumer_key=apiKey,
        consumer_secret=apiSecret,
        access_token_key=tokenKey,
        access_token_secret=tokenSecret
    )
    return twitterApi
    
def twitterStream(properties):
    global twitterThread
    try:
        if twitterThread.isAlive():
            console.cwrite("Shutting down Twitter stream...")
            twitterEvt.clear()
            return False
        _twitterStart(properties)
        return True
    except:
        _twitterStart(properties)
        return True
    
def _twitterStart(properties):
    global twitterThread, twitterProperties
    console.cwrite("Starting Twitter stream with properties %s" % properties)
    twitterProperties = properties
    twitterThread = twitterStreamThread()
    twitterThread.start()
