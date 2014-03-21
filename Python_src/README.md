This is the Python source code for the LEDgoes PC Tools application.  You can run it as follows:

python LEDgoesPCInterface.py

This version should be stable enough to facilitate production deployment.  I'm not guaranteeing it will be exception-free in all cases, but you can certainly get the matrix up and running.

REQUIREMENTS/DEPENDENCIES:

* Qt5
And possibly others...

GETTING STARTED WITH THE PROGRAM:

When you first open the program, set how many panels are in your one-row display by using the Up/Down box.  (Currently, the software does not support multiple-row marquees.)

The "Update Delay" (ms) is how you control the scroll rate.  A higher value here will cause the matrix to scroll slower.

Select a baud rate from the "Speed (bps)" dropdown list.  The boards run at 9600 bps when first turned on, but will be automatically programmed to use whatever baud rate you select in the software.  If you are using the Wireless Communicator, you must choose the rate for which your radio is set to run.  If you are using the USB Communicator, you can pick the fastest rate (1 million baud) if you wish.  Longer marquees will require such a high baud rate.  115200 bps is not recommended because it has the highest error rate among the provided choices.

Next, choose the COM port that represents the USB or Wireless Communicator.  Choosing the incorrect COM port may cause the program to tell you it's not open (in the form of an uncaught exception :-P), and the marquee will not show anything different.

Finally, hit "Connect" next to the COM port selection box.

Send the marquee messages to scroll by selecting the "Raw Text" tab.  Enter messages in the box at the bottom, then hit the "Push" button.

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
* Read from a Twitter feed
* Read from an RSS feed
* Proper Rich Text box to handle different fonts & colors in the same message
* Implementation of control signals understood by the firmware to change the serial baud rate & do debugging/development
