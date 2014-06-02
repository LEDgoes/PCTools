This is the Python source code for the LEDgoes PC Tools application.

Windows standalone installer: LEDgoes Setup.msi

Other platforms can run the software with Python 2.7.6:

python LEDgoesPCInterface.py

This version should be stable enough to facilitate production deployment.  There are some known issues but there should be very few unhandled exceptions and undocumented undesired behaviors.

DRIVERS:

To run LEDgoes from a USB Communicator, you will need drivers for the FTDI Chip so it appears as a Virtual COM Port.  Obtain these from http://www.ftdichip.com/Drivers/VCP.htm

REQUIREMENTS/DEPENDENCIES:
(You will not need to worry about these if using the Windows installer:)

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

Twitter mode is set to rely on a circular buffer that can contain a user-defined number of messages (you set this number in the "Message Limit" field on the Raw Text tab.  The buffer will fill all message slots before overwriting earlier messages.  If the marquee does not scroll through all of the queued messages by the time the maximum messages are received through the Twitter stream, then not all messages will be seen.  Also, the program is currently set to display Tweets in English only; this is easily changeable in the code.

The Twitter API allows users to customize their stream to look for multiple keywords/hashtags/handles and filter by location.  Currently our user interface only allows you to filter by one keyword.  You can add more filters in the code.  Eventually we will devise an interface to allow users to add all the desired filters.

In the latest version of the LEDgoes software, you can now display Tweets and raw text concurrently.  If the Twitter feed is fast-moving, and/or you want to make sure your message is seen periodically, make sure to check the "Sticky" checkbox so your message does not get overwritten when its turn comes up in the circular buffer.

ANIMATIONS:

This is still a bit hacky.  Input the path to a GIF image in the appropriate text field, then hit "Send."  The program will send each frame of the GIF image to the marquee based on the "Update Delay" -- currently, any timing information in the GIF files is discarded.

The reason this is still hacky is because the code is set up to display an animation 4 boards * 2 rows in size, and the board IDs must be 56-59 on the bottom row from left to right and 60-63 on the top row.  If you have a GIF of a different size, you will need to change the code.

Since LEDgoes only displays one shade of red, green, and yellow, GIFs are interpreted in this manner: Any RGB pixel with a red value > 127 (#7F0000) will show as red on the marquee.  Any RGB pixel with a green value > 127 (#007F00) will show as green on the marquee.  If both red & green are greater than 127 (#7F7F00), then the marquee will illuminate that pixel as yellow.  The digits for blue are ignored, and reserved for future use in an RGB-compatible program.

FONTS:

There is one font provided at this time: the "LEDgoes Default Font."  It must be placed in the same directory as the program.  Currently, it supports one size and one boldness.  The specification of this file is in JSON, and can be easily edited in any text editor.  However, it will be easier for you to create and edit your own fonts once we publish the specification and port the "LEDgoes Font Maker" program to Python.

ADVANCED CONTROLS AND TOPICS:

When you first enable communication to the matrix, boards with an auto-assigned ID "one below" the value the program expects will reprogram themselves to the expected ID.  For a two-board matrix, the program expects board IDs 0 and 32.  If the boards come up as 0 and 31, the software will prevent you from having to reset the second board's ID by hand.

This next section describes the features of the "Firmware" tab.

The "Show Test Pattern" button will show the test pattern (board ID) on the board specified in the text field.  If you hit "Let Me Stop Guessing!", all boards in your marquee will show their board ID.  These are useful diagnostic tools to use when boards are not showing the desired text or animation or have seemed to stop working.  Showing a test pattern on a value of 0-63 (0x0-0x3F) will show the pattern on that board, assuming it exists.  (Remember the 2nd board in a 2-board matrix usually doesn't have the ID of 1; it is usually 31 or 32.)  Using a value of 64-127 (0x40-0x7F) will show the ID of all boards.  To activate the ID on specific colors, use the chip addresses 128-191 (0x80-0xBF) for green, and 192-255 (0xC0-0xFF) for red.

If the board IDs have come out completely whacked, you can "Reset All Chip IDs".

If there is a board whose ID you wish to increase by one, enter its value in the field next to the "Increment A Chip ID" button, then hit that button.  You can specify a board ID from 0-63, or affect a particular chip.  You must add 128 to the board ID to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

If there is a board whose ID you wish to decrease by one, enter its value in the field next to the "Decrement A Chip ID" button, then hit that button.  You can specify a board ID from 0-63, or affect a particular chip.  You must add 128 to the shown value to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

If there is a board whose ID you wish to change completely, enter its current value in the "Current ID" field, then enter the value you wish to change it to in the "Desired ID" field.  Hit the "Set A Chip ID" button to effect the change.  You can specify a board ID from 0-63, or affect a particular chip.  You must add 128 to the shown value to affect the red chip, and 192 to affect the green chip.  You can enter the value in hex or decimal.

Compress Chip IDs:  This will take the IDs calculated by the auto-addressing scheme and compress them into numerical order by 1.  For instance, an 8-panel marquee with addresses [0, 8, 15, 23, 31, 39, 47, 56] would get squished down into [0, 1, 2, 3, 4, 5, 6, 7].  This is useful when trying to set up a large marquee.  By specifying a number in the "Start from:" field, you can set a non-zero starting value for the compression.  If you set the value too high, the board IDs will wrap around, e.g. [60, 61, 62, 63, 0, 1, 2, 3].  It is not recommended to do this on more than eight panels at a time.

Board firmware revision 3.2 supports these features:

Save Chip ID: The chip ID can now be saved in the EEPROM of each chip so that it will keep the same ID no matter how many times you power it off and on, until you clear or overwrite the EEPROM.  Enter a board ID from 0-63 or a chip ID from 128-255 in the "On:" field, then hit the button.  Or, hit "All" to save all chip IDs in the whole marquee to the chip's EEPROM.

There is also a Clear Chip ID instruction in Board Firmware 3.2, but it has not been added to the LEDgoes PC Interface software yet.

All backers are receiving Board Firmware 3.2, except for the Gen 1 & Gen 2 protos which were already shipped out a long time ago.

ERRATA:

* Stop the Twitter thread before closing the program, or else the program will stop responding and you'll probably have to close it through Task Manager.
* Cutting & pasting external text into the Raw Text Composition Box has not been thoroughly tested.  If your text already has formatting, it might behave erratically.  At least make sure it has a red, green, or yellow color first.
* Reducing the message limit to a number below the messages already in the queue will have an unpredictable effect.  You will need to delete messages manually, because the marquee will always show all messages in the queue, not just how many messages it is limited to.  We will make this automatic in a future release.
* Program icons don't show up in the shortcut & taskbar when using the Windows installer to install the software.

ENHANCEMENT WISHLIST:

* Animations (Different sizes, BMP frames, AVI movies)
* Enhance Twitter interactions & stream customizations for different languages & character sets
* Read from an RSS feed
* Proper Rich Text box to handle different fonts & colors in the same message
* Implementation of remaining control signals understood by the firmware to do debugging/development
* IFTTT protocol support
* Allowing 3rd-party & external plugins to integrate easily
