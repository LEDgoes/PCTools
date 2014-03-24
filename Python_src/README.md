This is the Python source code for the LEDgoes PC Tools application.  You can run it as follows:

python LEDgoesPCInterface.py

This version should be stable enough to facilitate production deployment.  I'm not guaranteeing it will be exception-free in all cases, but you can certainly get the matrix up and running.

REQUIREMENTS/DEPENDENCIES:

* Qt5
* python-twitter
* Pillow 2.3.1 (Python Imaging Library)
And possibly others...

GETTING STARTED WITH THE PROGRAM:

When you first open the program, set how many panels are in your one-row display by using the Up/Down box.  (Currently, the software does not support multiple-row marquees.)

The "Update Delay" (ms) is how you control the scroll rate.  A higher value here will cause the matrix to scroll slower.

Select a baud rate from the "Speed (bps)" dropdown list.  The boards run at 9600 bps when first turned on, but will be automatically programmed to use whatever baud rate you select in the software.  If you are using the Wireless Communicator, you must choose the rate for which your radio is set to run.  If you are using the USB Communicator, you can pick the fastest rate (1 million baud) if you wish.  Longer marquees will require such a high baud rate.  115200 bps is not recommended because it has the highest error rate among the provided choices.

Next, choose the COM port that represents the USB or Wireless Communicator.  Choosing the incorrect COM port may cause the program to tell you it's not open (in the form of an uncaught exception :-P), and the marquee will not show anything different.

Finally, hit "Connect" next to the COM port selection box.

Send the marquee messages to scroll by selecting the "Raw Text" tab.  Enter messages in the box at the bottom, then hit the "Push" button.

TWITTER:

To display messages from Twitter, you need to have a Twitter account and register an application with it.  To do this, log in to https://dev.twitter.com with your Twitter username & password.  Click at the top where your avatar icon is, and it will activate a drop-down menu.  Click "My applications", then "Create New App".  Enter some information about it.

Once you're done, take note of the API Keys from the "API Keys" tab.  Copy these four values into the text fields in the LEDgoes PC Tools:

Twitter => LEDgoes
1. API Key => Consumer Key
2. API Secret => Consumer Secret
3. Access Token => Access Token
4. Access Token Secret => Access Token Secret

Once you have done this, click the "Authenticate" button on the LEDgoes PC Tools.  You should now be authenticated on Twitter.  Now, enter a Twitter hashtag, handle, or phrase into the box at the bottom and hit "Start".  When you wish to stop receiving Tweets, hit the "Start" button again and upon receiving one more Tweet, it will stop.

Currently, the LEDgoes Default Font does not understand lowercase characters, nor will the program transform lowercase characters into uppercase characters.  This will be fixed in a future revision of the font & program.  You are welcome to make these changes yourself.

Twitter mode is set to rely on a circular buffer that can contain 10 messages.  The buffer will fill all 10 message slots before overwriting earlier messages.  If the marquee does not scroll through all 10 messages by the time 10 messages are received through the Twitter stream, then not all messages will be seen.  Also, the program is currently set to display Tweets in English only; this is easily changeable in the code.

The Twitter API allows users to customize their stream to look for multiple keywords/hashtags/handles and filter by location.  Currently our user interface only allows you to filter by one keyword.  You can add more filters in the code.  Eventually we will devise an interface to allow users to add all the desired filters.

Finally, when using Twitter with LEDgoes, it is not recommended to use Raw Text to transmit messages at the same time.  With a fast-moving Twitter stream, your message will probably get wiped out before the marquee even refreshes what messages it will display.  This is another issue that will probably get cleaned up in a future release.

FONTS:

There is one font provided at this time: the "LEDgoes Default Font."  It must be placed in the same directory as the program.  Currently, it supports one size and one boldness.  The specification of this file should be fairly obvious if you open it up in Notepad++ or a hex editor.  However, it will be easier for you to create and edit your own fonts once we publish the specification and port the "LEDgoes Font Maker" program to Python.

ADVANCED CONTROLS AND TOPICS:

When you first enable communication to the matrix, boards with an auto-assigned ID "one below" the value the program expects will reprogram themselves to the expected ID.  For a two-board matrix, the program expects board IDs 0 and 32.  If the boards come up as 0 and 31, the software will prevent you from having to reset the second board's ID by hand.

This next section describes the features of the "Firmware" tab.

If the board IDs have come out completely whacked, you can "Reset All Chip IDs".

If there is a board whose ID you wish to increase by one, enter its value in the field next to the "Increment A Chip ID" button, then hit that button.  You must add 128 to the shown value to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

If there is a board whose ID you wish to decrease by one, enter its value in the field next to the "Decrement A Chip ID" button, then hit that button.  You must add 128 to the shown value to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

If there is a board whose ID you wish to change completely, enter its current value in the "Current ID" field, then enter the value you wish to change it to in the "Desired ID" field.  Hit the "Set A Chip ID" button to effect the change.  You must add 128 to the shown value to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

If a board isn't showing the desired text or animation or has stopped working, use the "Show Test Pattern" tool.  Showing a test pattern on a value of 0-63 (0x0-0x3F) will show the pattern on that board, assuming it exists.  (Remember the 2nd board in a 2-board matrix doesn't have the ID of 1; it is usually 31 or 32.)  Using a value of 64-127 (0x40-0x7F) will show the ID of all boards.  To activate the ID on specific colors, use the chip addresses 128-191 (0x80-0xBF) for green, and 192-255 (0xC0-0xFF) for red.

ERRATA:

The "Let Me Stop Guessing!" button is supposed to provide a shortcut for entering 0x40 into the "On:" field next to "Show Test Pattern", but it doesn't currently work.

You can only change baud rate once.  The software seems to have problems sending the message to the boards if they are no longer running at 9600 bps.  If you need to change the baud rate more than once, make sure the COM port is disconnected in software, then power off the boards.  Wait a couple seconds, then re-apply power.

ENHANCEMENT WISHLIST:

* Animations (GIF, BMP frames, AVI movies)
* Enhance Twitter interactions & stream customizations
* Read from an RSS feed
* Proper Rich Text box to handle different fonts & colors in the same message
* Implementation of control signals understood by the firmware to change the serial baud rate & do debugging/development
