import LEDgoesGlobals as globals
import threading
import twitter

twitterEvt = threading.Event()   # Thread will check if the event has gone to False, and then wait
twitterEvt.set()                 # Standard Python events allow threads to continue running if event flag is set


class twitterStreamThread (threading.Thread):
    def __init__(self):
        super(twitterStreamThread, self).__init__()
        print "Twitter thread is now running; when it stops may not necessarily be advertised..."
    
    def run(self):
        global twitterApi, twitterProperties, twitterEvt
        maxTweets = 10
        curIndex = 0
        for item in twitterApi.GetStreamFilter(track=[twitterProperties]):
            if item.has_key('text'):
                try:
                    # Output all Tweets including language
                    print "===== %s " % item['lang']
                    print item['text']
                    # Display only English tweets (change as you see fit)
                    if item['lang'] == "en":
                        tweetText = "@%s %s" % (item['user']['screen_name'], item['text'])
                        try:
                            globals.richMsgs[curIndex] = tweetText
                        except:
                            globals.richMsgs.append(tweetText)
                        curIndex = (curIndex + 1) % maxTweets
                except Exception as ex:
                    print ex
            if not twitterEvt.is_set():
                print "Twitter stream shut down!"
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
            print "Shutting down Twitter stream..."
            twitterEvt.clear()
        else:
            _twitterStart(properties)
    except:
        _twitterStart(properties)
    
def _twitterStart(properties):
    global twitterThread, twitterProperties
    print "Starting Twitter stream with properties %s" % properties
    twitterProperties = properties
    twitterThread = twitterStreamThread()
    twitterThread.start()        