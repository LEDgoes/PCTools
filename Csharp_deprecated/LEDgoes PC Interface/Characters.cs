using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
// Other imports
using System.Threading;
using System.IO.Ports;

namespace LEDgoes_PC_Interface
{
    public partial class Form1
    {
        static int[] rBuf = new int[0];         // entire red buffer
        static int[] gBuf = new int[0];         // entire green buffer
        static byte[] rPart = new byte[5];      // one section of the red buffer
        static byte[] gPart = new byte[5];      // one section of the green buffer
        static byte[] eom = new byte[1];        // "end of message" (actually the beginning) indicates which processor receives the letter
        static int counter;                     // keeps track of where we are in the message
        static int bufLen;                      // remembers the total length of the message
        static int inputLen;                    // length in bytes of the message sent from BT (actually, the # bytes available to read over serial)
        static String messageFromBT;            // the actual message sent over BT
        static String redString, greenString;   // strings comtaining the red & green messages
        static String emptyString;              // spacer to go between redString & greenString when the colors alternate
        static int boards = 2;                 // number of LED display boards in the matrix

        int maxMsgs = 10;                       // Declare that we will store 10 messages
        int curMsg = 0;                         // This is the message number to fill - set to 0 to fill the 1st message
        int index_ETX = -0x01;                     // Index of the ETX (end of transmission) character to denote end of message
        String[] messages;                      // Set up enough strings to contain the desired # of messages
        String tmpMsg = "";                     // Constructing the message string from the incoming parts over serial

        private void serialWelcome()
        {
            messages = new String[maxMsgs];
            messages[0] = " :: AWAITING MESSAGES ";
            for (int i = 0x01; i < 10; i++)
                messages[i] = "";
            makeRMessageString(messages[0]);
            makeGMessageString(messages[0]);
            // Start a thread
            outputThread = new Thread(new ThreadStart(serialThread));
            outputThread.Start();
        }

        private void serialThread() {
            while (true)  // mind you, this is the implementation coming straight from the firmware ;)
            {
                // WRITING THE MESSAGE ON THE BOARD
                for (byte i = 0; i < boards; i++)    // iterate through the amount of characters we have on the board
                {
                    eom[0] = i;
                    writeString(i);             // Write the portion of the string pertaining to the active processor
                }
                counter++;                      // Now go on to show the next character column
                // MESSAGE EXPIRATION
                if (counter >= bufLen)          // If we've reached the end of the message,
                {
                    counter = 0;                // reset the column counter to 0
                    redString = "";             // reset the red string to empty
                    greenString = "";           // reset the green string to empty
                    for (int i = maxMsgs - 1; i >= 0; i--)
                    {
                        if (messages[i].Length == 0)
                            continue;
                        emptyString = new String(' ', messages[i].Length);  // Make an empty string equal in length to the current message
                        //redString += ((i % 2 == 0) ? messages[i] : emptyString) + "  ";     // set the red string
                        //greenString += ((i % 2 != 0) ? messages[i] : emptyString) + "  ";   // set the green string
                        greenString += messages[i] + "  ";     // set the red string
                        redString += messages[i] + "  ";   // set the green string
                    }
                    makeRMessageString(redString);
                    makeGMessageString(greenString);
                }
            }
        }

        public void writeString(int offset)
        {
            SerialPort cxn;
            int shift;
            // Figure out what serial port to use
            if (rows == 2 && !multiplexed)   // With 0x02 rows in use & no demultiplexer, pick between the 0x02 active serial conns
                cxn = (offset % 2 == 0) ? cxn1 : cxn2;    // even chips are the top row, odd chips are the bottom row
            else             // With only 0x01 row, or 3+ rows, use just one serial conn (3+ requires the demuxer)
                cxn = cxn1;
            // Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
            int adjustment = (int)System.Math.Floor((double) offset / rows) * 5;
            // Grab the 5 columns, shift if necessary, and save it into an actual byte array
            shift = (offset % rows) * 0x07;
            int index;
            for (int i = 0; i < 5; i++)
            {
                index = counter + adjustment + i;
                // How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
                rPart[i] = (byte) ((rBuf[index] >> shift) & 0x7F);
                //if (index > 0x10) { rPart[i] = (byte) (rPart[i] & 0x1F); }
                gPart[i] = (byte) ((gBuf[index] >> shift) & 0x7F);
                //if (index > 0x10) { gPart[i] = (byte) (gPart[i] & 0xFC); }
            }
            // Write red portion
            eom[0] |= 0x80;                    // red chips are looking for a message ID of 0x80 to 0xBF
            cxn.Write(eom, 0, 1);              // write the chip we want to write to over serial
            cxn.Write(rPart, 0, 5);
            //Debug.Print(rBuf[counter].ToString());
            // Write green portion
            eom[0] |= 0x40;                    // green chips are looking for a message ID of 0xC0 to 0xFF
            cxn.Write(eom, 0, 1);              // write the chip we want to write to over serial
            cxn.Write(gPart, 0, 5);
//            Console.Write("Writing " + eom[0].ToString() + " / ");
//            Console.WriteLine(gPart[0].ToString() + " " + gPart[1].ToString() + " " + gPart[2].ToString() + " " + gPart[3].ToString() + " " + gPart[4].ToString());
//            cxn.Write("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA");
            //Debug.Print(gBuf[counter].ToString());
            // Now just sleep 0x01/10th of a second before we go to the next character column
/*            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
            Console.Write(cxn1.ReadByte() + " ");
//            Console.Write(cxn1.ReadByte() + " ");
            Console.WriteLine(cxn1.ReadByte());
*/            Thread.Sleep(4);
        }

        public void makeRMessageString(String message)
        {   // Make the message to appear in Red
            rBuf = makeMessageString(message);
        }
        
        public void makeGMessageString(String message)
        {   // Make the message to appear in Green
            gBuf = makeMessageString(message);
        }

        public int[] makeMessageString(String message)
        {
            // Make the message string from the letters
            if (rows == 0x01)
            {
                // Each character takes up 5 columns plus 0x01 spacer; each board is 5 columns wide
                int[] buf = new int[(message.Length * 6) + (boards * 5)];
                char[] msgText = message.ToCharArray();
                for (int i = 0; i < 5; i++)
                    buf[i] = 0;
                for (int i = 0, j = 0; i < message.Length; i++, j += 6)
                {
                    // Find out what the letter is
                    // Alphabetics - Uppercase
                    if (msgText[i] == 'A') { buf[j] = 0x3F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x3F; };
                    if (msgText[i] == 'B') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == 'C') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x22; };
                    if (msgText[i] == 'D') { buf[j] = 0x7F; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'E') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x49; };
                    if (msgText[i] == 'F') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x48; };
                    if (msgText[i] == 'G') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x2E; };
                    if (msgText[i] == 'H') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'I') { buf[j] = 0x41; buf[j + 1] = 0x41; buf[j + 2] = 0x7F; buf[j + 3] = 0x41; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'J') { buf[j] = 0x02; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'K') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x14; buf[j + 3] = 0x22; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'L') { buf[j] = 0x7F; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == 'M') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x20; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'N') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'O') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'P') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x30; };
                    if (msgText[i] == 'Q') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x45; buf[j + 3] = 0x42; buf[j + 4] = 0x3D; };
                    if (msgText[i] == 'R') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x4C; buf[j + 4] = 0x33; };
                    if (msgText[i] == 'S') { buf[j] = 0x32; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x26; };
                    if (msgText[i] == 'T') { buf[j] = 0x40; buf[j + 1] = 0x40; buf[j + 2] = 0x7F; buf[j + 3] = 0x40; buf[j + 4] = 0x40; };
                    if (msgText[i] == 'U') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'V') { buf[j] = 0x7C; buf[j + 1] = 0x02; buf[j + 2] = 0x01; buf[j + 3] = 0x02; buf[j + 4] = 0x7C; };
                    if (msgText[i] == 'W') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x0E; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'X') { buf[j] = 0x63; buf[j + 1] = 0x14; buf[j + 2] = 0x08; buf[j + 3] = 0x14; buf[j + 4] = 0x63; };
                    if (msgText[i] == 'Y') { buf[j] = 0x70; buf[j + 1] = 0x08; buf[j + 2] = 0x07; buf[j + 3] = 0x08; buf[j + 4] = 0x70; };
                    if (msgText[i] == 'Z') { buf[j] = 0x43; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x61; };
                    // Alphabetics - Lowercase (TODO: still being written as uppercase)
                    if (msgText[i] == 'a') { buf[j] = 0x3F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x3F; };
                    if (msgText[i] == 'b') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == 'c') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x22; };
                    if (msgText[i] == 'd') { buf[j] = 0x7F; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'e') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x49; };
                    if (msgText[i] == 'f') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x48; };
                    if (msgText[i] == 'g') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x2E; };
                    if (msgText[i] == 'h') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'i') { buf[j] = 0x41; buf[j + 1] = 0x41; buf[j + 2] = 0x7F; buf[j + 3] = 0x41; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'j') { buf[j] = 0x02; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'k') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x14; buf[j + 3] = 0x22; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'l') { buf[j] = 0x7F; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == 'm') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x20; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'n') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'o') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'p') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x30; };
                    if (msgText[i] == 'q') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x45; buf[j + 3] = 0x42; buf[j + 4] = 0x3D; };
                    if (msgText[i] == 'r') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x4C; buf[j + 4] = 0x33; };
                    if (msgText[i] == 's') { buf[j] = 0x32; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x26; };
                    if (msgText[i] == 't') { buf[j] = 0x40; buf[j + 1] = 0x40; buf[j + 2] = 0x7F; buf[j + 3] = 0x40; buf[j + 4] = 0x40; };
                    if (msgText[i] == 'u') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'v') { buf[j] = 0x7C; buf[j + 1] = 0x02; buf[j + 2] = 0x01; buf[j + 3] = 0x02; buf[j + 4] = 0x7C; };
                    if (msgText[i] == 'w') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x0E; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'x') { buf[j] = 0x63; buf[j + 1] = 0x14; buf[j + 2] = 0x08; buf[j + 3] = 0x14; buf[j + 4] = 0x63; };
                    if (msgText[i] == 'y') { buf[j] = 0x70; buf[j + 1] = 0x08; buf[j + 2] = 0x07; buf[j + 3] = 0x08; buf[j + 4] = 0x70; };
                    if (msgText[i] == 'z') { buf[j] = 0x43; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x61; };

                    // Numbers
                    if (msgText[i] == '1') { buf[j] = 0x01; buf[j + 1] = 33; buf[j + 2] = 0x7F; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == '2') { buf[j] = 39; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 49; };
                    if (msgText[i] == '3') { buf[j] = 0x22; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == '4') { buf[j] = 120; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == '5') { buf[j] = 122; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 70; };
                    if (msgText[i] == '6') { buf[j] = 0x3E; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 6; };
                    if (msgText[i] == '7') { buf[j] = 0x40; buf[j + 1] = 0x40; buf[j + 2] = 71; buf[j + 3] = 0x48; buf[j + 4] = 0x70; };
                    if (msgText[i] == '8') { buf[j] = 0x36; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == '9') { buf[j] = 0x30; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x3E; };
                    if (msgText[i] == '0') { buf[j] = 0x3E; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x3E; };

                    // Symbols in keyboard order
                    if (msgText[i] == '~') { buf[j] = 0x08; buf[j + 1] = 0x10; buf[j + 2] = 0x08; buf[j + 3] = 4; buf[j + 4] = 0x08; };
                    if (msgText[i] == '`') { buf[j] = 0; buf[j + 1] = 0x40; buf[j + 2] = 0x20; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '!') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 125; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '@') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 93; buf[j + 3] = 85; buf[j + 4] = 56; };
                    if (msgText[i] == '#') { buf[j] = 0x14; buf[j + 1] = 0x3E; buf[j + 2] = 0x14; buf[j + 3] = 0x3E; buf[j + 4] = 0x14; };
                    if (msgText[i] == '$') { buf[j] = 18; buf[j + 1] = 42; buf[j + 2] = 0x7F; buf[j + 3] = 42; buf[j + 4] = 36; };
                    if (msgText[i] == '%') { buf[j] = 0x63; buf[j + 1] = 100; buf[j + 2] = 0x08; buf[j + 3] = 19; buf[j + 4] = 0x63; };
                    if (msgText[i] == '^') { buf[j] = 0x10; buf[j + 1] = 0x20; buf[j + 2] = 0x40; buf[j + 3] = 0x20; buf[j + 4] = 0x10; };
                    if (msgText[i] == '&') { buf[j] = 0x36; buf[j + 1] = 0x49; buf[j + 2] = 53; buf[j + 3] = 0x02; buf[j + 4] = 13; };
                    if (msgText[i] == '*') { buf[j] = 0x14; buf[j + 1] = 0x08; buf[j + 2] = 0x3E; buf[j + 3] = 0x08; buf[j + 4] = 0x14; };
                    if (msgText[i] == '(') { buf[j] = 0; buf[j + 1] = 28; buf[j + 2] = 0x22; buf[j + 3] = 0x41; buf[j + 4] = 0; };
                    if (msgText[i] == ')') { buf[j] = 0; buf[j + 1] = 0x41; buf[j + 2] = 0x22; buf[j + 3] = 28; buf[j + 4] = 0; };
                    if (msgText[i] == '-') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '_') { buf[j] = 0x01; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == '+') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x3E; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '=') { buf[j] = 0x14; buf[j + 1] = 0x14; buf[j + 2] = 0x14; buf[j + 3] = 0x14; buf[j + 4] = 0x14; };
                    if (msgText[i] == '[') { buf[j] = 0; buf[j + 1] = 0x7F; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0; };
                    if (msgText[i] == '{') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x36; buf[j + 3] = 0x41; buf[j + 4] = 0x41; };
                    if (msgText[i] == ']') { buf[j] = 0; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x7F; buf[j + 4] = 0; };
                    if (msgText[i] == '}') { buf[j] = 0x41; buf[j + 1] = 0x41; buf[j + 2] = 0x36; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '\\') { buf[j] = 0x20; buf[j + 1] = 0x10; buf[j + 2] = 0x08; buf[j + 3] = 4; buf[j + 4] = 0x02; };
                    if (msgText[i] == '|') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x7F; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == ';') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x32; buf[j + 3] = 52; buf[j + 4] = 0; };
                    if (msgText[i] == ':') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x36; buf[j + 3] = 0x36; buf[j + 4] = 0; };
                    if (msgText[i] == '\'') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x20; buf[j + 3] = 0x40; buf[j + 4] = 0; };
                    if (msgText[i] == '"') { buf[j] = 0; buf[j + 1] = 96; buf[j + 2] = 0; buf[j + 3] = 96; buf[j + 4] = 0; };
                    if (msgText[i] == ',') { buf[j] = 0; buf[j + 1] = 0x01; buf[j + 2] = 0x02; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '<') { buf[j] = 0x08; buf[j + 1] = 0x14; buf[j + 2] = 0x14; buf[j + 3] = 0x22; buf[j + 4] = 0x22; };
                    if (msgText[i] == '.') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 3; buf[j + 3] = 3; buf[j + 4] = 0; };
                    if (msgText[i] == '>') { buf[j] = 0x22; buf[j + 1] = 0x22; buf[j + 2] = 0x14; buf[j + 3] = 0x14; buf[j + 4] = 0x08; };
                    if (msgText[i] == '/') { buf[j] = 0x02; buf[j + 1] = 4; buf[j + 2] = 0x08; buf[j + 3] = 0x10; buf[j + 4] = 0x20; };
                    if (msgText[i] == '?') { buf[j] = 0x20; buf[j + 1] = 0x40; buf[j + 2] = 77; buf[j + 3] = 0x48; buf[j + 4] = 0x30; };
                    if (msgText[i] == ' ') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0; buf[j + 3] = 0; buf[j + 4] = 0; };
                    buf[j + 5] = 0;
                }
                for (int i = buf.Length - (boards * 5); i < buf.Length; i++)
                    buf[i] = 0;
                bufLen = buf.Length - (boards * 5);
                return buf;
            }
            else if (rows == 0x02)
            {


                // Make the message string from the letters
                int[] buf = new int[(message.Length * 11) + (boards * 5)];
                char[] msgText = message.ToCharArray();
                for (int i = 0; i < 10; i++)
                    buf[i] = 0;
                for (int i = 0, j = 10; i < message.Length; i++, j += 11)
                {
                    // Find out what the letter is
                    // Alphabetics - Uppercase
                    if (msgText[i] == 'A') { buf[j] = 8191; buf[j + 1] = 16383; buf[j + 2] = 12384; buf[j + 3] = 12384; buf[j + 4] = 12384; buf[j + 5] = 12384; buf[j + 6] = 12384; buf[j + 0x07] = 12384; buf[j + 0x08] = 16383; buf[j + 9] = 8191; };
                    if (msgText[i] == 'B') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12483; buf[j + 3] = 12483; buf[j + 4] = 12483; buf[j + 5] = 12483; buf[j + 6] = 12483; buf[j + 0x07] = 14823; buf[j + 0x08] = 8063; buf[j + 9] = 3644; };
                    if (msgText[i] == 'C') { buf[j] = 4092; buf[j + 1] = 8190; buf[j + 2] = 15375; buf[j + 3] = 12291; buf[j + 4] = 12291; buf[j + 5] = 12291; buf[j + 6] = 12291; buf[j + 0x07] = 14343; buf[j + 0x08] = 7182; buf[j + 9] = 3084; };
                    if (msgText[i] == 'D') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12291; buf[j + 3] = 12291; buf[j + 4] = 12291; buf[j + 5] = 12291; buf[j + 6] = 12291; buf[j + 0x07] = 14343; buf[j + 0x08] = 8190; buf[j + 9] = 4092; };
                    if (msgText[i] == 'E') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12483; buf[j + 3] = 12483; buf[j + 4] = 12483; buf[j + 5] = 12483; buf[j + 6] = 12483; buf[j + 0x07] = 12291; buf[j + 0x08] = 12291; buf[j + 9] = 12291; };
                    if (msgText[i] == 'F') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12480; buf[j + 3] = 12480; buf[j + 4] = 12480; buf[j + 5] = 12480; buf[j + 6] = 12480; buf[j + 0x07] = 12288; buf[j + 0x08] = 12288; buf[j + 9] = 12288; };
                    if (msgText[i] == 'G') { buf[j] = 8190; buf[j + 1] = 16383; buf[j + 2] = 12291; buf[j + 3] = 12291; buf[j + 4] = 12291; buf[j + 5] = 12387; buf[j + 6] = 12387; buf[j + 0x07] = 12387; buf[j + 0x08] = 15487; buf[j + 9] = 7294; };
                    if (msgText[i] == 'H') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 192; buf[j + 3] = 192; buf[j + 4] = 192; buf[j + 5] = 192; buf[j + 6] = 192; buf[j + 0x07] = 192; buf[j + 0x08] = 16383; buf[j + 9] = 16383; };
                    if (msgText[i] == 'I') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 12291; buf[j + 3] = 12291; buf[j + 4] = 16383; buf[j + 5] = 16383; buf[j + 6] = 12291; buf[j + 0x07] = 12291; buf[j + 0x08] = 0; buf[j + 9] = 0; };
                    if (msgText[i] == 'J') { buf[j] = 0x02; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'K') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 192; buf[j + 3] = 480; buf[j + 4] = 816; buf[j + 5] = 1560; buf[j + 6] = 3084; buf[j + 0x07] = 6150; buf[j + 0x08] = 12291; buf[j + 9] = 8193; };
                    if (msgText[i] == 'L') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 3; buf[j + 3] = 3; buf[j + 4] = 3; buf[j + 5] = 3; buf[j + 6] = 3; buf[j + 0x07] = 3; buf[j + 0x08] = 3; buf[j + 9] = 3; };
                    if (msgText[i] == 'M') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 7680; buf[j + 3] = 1792; buf[j + 4] = 896; buf[j + 5] = 896; buf[j + 6] = 1792; buf[j + 0x07] = 7680; buf[j + 0x08] = 16383; buf[j + 9] = 16383; };
                    if (msgText[i] == 'N') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 7680; buf[j + 3] = 1792; buf[j + 4] = 448; buf[j + 5] = 224; buf[j + 6] = 56; buf[j + 0x07] = 30; buf[j + 0x08] = 16383; buf[j + 9] = 16383; };
                    if (msgText[i] == 'O') { buf[j] = 4092; buf[j + 1] = 8190; buf[j + 2] = 15375; buf[j + 3] = 12291; buf[j + 4] = 12291; buf[j + 5] = 12291; buf[j + 6] = 12291; buf[j + 0x07] = 15375; buf[j + 0x08] = 8190; buf[j + 9] = 4092; };
                    if (msgText[i] == 'P') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12480; buf[j + 3] = 12480; buf[j + 4] = 12480; buf[j + 5] = 12480; buf[j + 6] = 12480; buf[j + 0x07] = 14784; buf[j + 0x08] = 8064; buf[j + 9] = 3840; };
                    if (msgText[i] == 'Q') { buf[j] = 4092; buf[j + 1] = 8190; buf[j + 2] = 15375; buf[j + 3] = 12291; buf[j + 4] = 12315; buf[j + 5] = 12319; buf[j + 6] = 12302; buf[j + 0x07] = 15391; buf[j + 0x08] = 8187; buf[j + 9] = 4083; };
                    if (msgText[i] == 'R') { buf[j] = 16383; buf[j + 1] = 16383; buf[j + 2] = 12480; buf[j + 3] = 12480; buf[j + 4] = 12480; buf[j + 5] = 12512; buf[j + 6] = 12536; buf[j + 0x07] = 14814; buf[j + 0x08] = 8071; buf[j + 9] = 3843; };
                    if (msgText[i] == 'S') { buf[j] = 7950; buf[j + 1] = 16371; buf[j + 2] = 0x7F39; buf[j + 3] = 12483; buf[j + 4] = 12483; buf[j + 5] = 12483; buf[j + 6] = 12483; buf[j + 0x07] = 12515; buf[j + 0x08] = 15487; buf[j + 9] = 7230; };
                    if (msgText[i] == 'T') { buf[j] = 12288; buf[j + 1] = 12288; buf[j + 2] = 12288; buf[j + 3] = 12288; buf[j + 4] = 16383; buf[j + 5] = 16383; buf[j + 6] = 12288; buf[j + 0x07] = 12288; buf[j + 0x08] = 12288; buf[j + 9] = 12288; };
                    if (msgText[i] == 'U') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'V') { buf[j] = 0x7C; buf[j + 1] = 0x02; buf[j + 2] = 0x01; buf[j + 3] = 0x02; buf[j + 4] = 0x7C; };
                    if (msgText[i] == 'W') { buf[j] = 16382; buf[j + 1] = 16383; buf[j + 2] = 3; buf[j + 3] = 3; buf[j + 4] = 0x7E; buf[j + 5] = 0x7E; buf[j + 6] = 3; buf[j + 0x07] = 3; buf[j + 0x08] = 16383; buf[j + 9] = 16382; };
                    if (msgText[i] == 'X') { buf[j] = 0x63; buf[j + 1] = 0x14; buf[j + 2] = 0x08; buf[j + 3] = 0x14; buf[j + 4] = 0x63; };
                    if (msgText[i] == 'Y') { buf[j] = 0x70; buf[j + 1] = 0x08; buf[j + 2] = 0x07; buf[j + 3] = 0x08; buf[j + 4] = 0x70; };
                    if (msgText[i] == 'Z') { buf[j] = 0x43; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x61; };
                    // Alphabetics - Lowercase (TODO: still being written as uppercase)
                    if (msgText[i] == 'a') { buf[j] = 0x3F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x3F; };
                    if (msgText[i] == 'b') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == 'c') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x22; };
                    if (msgText[i] == 'd') { buf[j] = 0x7F; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'e') { buf[j] = 0x7F; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x49; };
                    if (msgText[i] == 'f') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x48; };
                    if (msgText[i] == 'g') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x2E; };
                    if (msgText[i] == 'h') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'i') { buf[j] = 0x41; buf[j + 1] = 0x41; buf[j + 2] = 0x7F; buf[j + 3] = 0x41; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'j') { buf[j] = 0x02; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'k') { buf[j] = 0x7F; buf[j + 1] = 0x08; buf[j + 2] = 0x14; buf[j + 3] = 0x22; buf[j + 4] = 0x41; };
                    if (msgText[i] == 'l') { buf[j] = 0x7F; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == 'm') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x20; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'n') { buf[j] = 0x7F; buf[j + 1] = 0x20; buf[j + 2] = 0x10; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == 'o') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0x3E; };
                    if (msgText[i] == 'p') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x48; buf[j + 4] = 0x30; };
                    if (msgText[i] == 'q') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 0x45; buf[j + 3] = 0x42; buf[j + 4] = 0x3D; };
                    if (msgText[i] == 'r') { buf[j] = 0x7F; buf[j + 1] = 0x48; buf[j + 2] = 0x48; buf[j + 3] = 0x4C; buf[j + 4] = 0x33; };
                    if (msgText[i] == 's') { buf[j] = 0x32; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x26; };
                    if (msgText[i] == 't') { buf[j] = 0x40; buf[j + 1] = 0x40; buf[j + 2] = 0x7F; buf[j + 3] = 0x40; buf[j + 4] = 0x40; };
                    if (msgText[i] == 'u') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'v') { buf[j] = 0x7C; buf[j + 1] = 0x02; buf[j + 2] = 0x01; buf[j + 3] = 0x02; buf[j + 4] = 0x7C; };
                    if (msgText[i] == 'w') { buf[j] = 0x7E; buf[j + 1] = 0x01; buf[j + 2] = 0x0E; buf[j + 3] = 0x01; buf[j + 4] = 0x7E; };
                    if (msgText[i] == 'x') { buf[j] = 0x63; buf[j + 1] = 0x14; buf[j + 2] = 0x08; buf[j + 3] = 0x14; buf[j + 4] = 0x63; };
                    if (msgText[i] == 'y') { buf[j] = 0x70; buf[j + 1] = 0x08; buf[j + 2] = 0x07; buf[j + 3] = 0x08; buf[j + 4] = 0x70; };
                    if (msgText[i] == 'z') { buf[j] = 0x43; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x61; };

                    // Numbers
                    if (msgText[i] == '1') { buf[j] = 0x01; buf[j + 1] = 33; buf[j + 2] = 0x7F; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == '2') { buf[j] = 39; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 49; };
                    if (msgText[i] == '3') { buf[j] = 0x22; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == '4') { buf[j] = 120; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x7F; };
                    if (msgText[i] == '5') { buf[j] = 122; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 70; };
                    if (msgText[i] == '6') { buf[j] = 0x3E; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 6; };
                    if (msgText[i] == '7') { buf[j] = 0x40; buf[j + 1] = 0x40; buf[j + 2] = 71; buf[j + 3] = 0x48; buf[j + 4] = 0x70; };
                    if (msgText[i] == '8') { buf[j] = 0x36; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x36; };
                    if (msgText[i] == '9') { buf[j] = 0x30; buf[j + 1] = 0x49; buf[j + 2] = 0x49; buf[j + 3] = 0x49; buf[j + 4] = 0x3E; };
                    if (msgText[i] == '0') { buf[j] = 0x3E; buf[j + 1] = 0x45; buf[j + 2] = 0x49; buf[j + 3] = 0x51; buf[j + 4] = 0x3E; };

                    // Symbols in keyboard order
                    if (msgText[i] == '~') { buf[j] = 0x08; buf[j + 1] = 0x10; buf[j + 2] = 0x08; buf[j + 3] = 4; buf[j + 4] = 0x08; };
                    if (msgText[i] == '`') { buf[j] = 0; buf[j + 1] = 0x40; buf[j + 2] = 0x20; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '!') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 125; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '@') { buf[j] = 0x3E; buf[j + 1] = 0x41; buf[j + 2] = 93; buf[j + 3] = 85; buf[j + 4] = 56; };
                    if (msgText[i] == '#') { buf[j] = 0x14; buf[j + 1] = 0x3E; buf[j + 2] = 0x14; buf[j + 3] = 0x3E; buf[j + 4] = 0x14; };
                    if (msgText[i] == '$') { buf[j] = 18; buf[j + 1] = 42; buf[j + 2] = 0x7F; buf[j + 3] = 42; buf[j + 4] = 36; };
                    if (msgText[i] == '%') { buf[j] = 0x63; buf[j + 1] = 100; buf[j + 2] = 0x08; buf[j + 3] = 19; buf[j + 4] = 0x63; };
                    if (msgText[i] == '^') { buf[j] = 0x10; buf[j + 1] = 0x20; buf[j + 2] = 0x40; buf[j + 3] = 0x20; buf[j + 4] = 0x10; };
                    if (msgText[i] == '&') { buf[j] = 0x36; buf[j + 1] = 0x49; buf[j + 2] = 53; buf[j + 3] = 0x02; buf[j + 4] = 13; };
                    if (msgText[i] == '*') { buf[j] = 0x14; buf[j + 1] = 0x08; buf[j + 2] = 0x3E; buf[j + 3] = 0x08; buf[j + 4] = 0x14; };
                    if (msgText[i] == '(') { buf[j] = 0; buf[j + 1] = 28; buf[j + 2] = 0x22; buf[j + 3] = 0x41; buf[j + 4] = 0; };
                    if (msgText[i] == ')') { buf[j] = 0; buf[j + 1] = 0x41; buf[j + 2] = 0x22; buf[j + 3] = 28; buf[j + 4] = 0; };
                    if (msgText[i] == '-') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x08; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '_') { buf[j] = 0x01; buf[j + 1] = 0x01; buf[j + 2] = 0x01; buf[j + 3] = 0x01; buf[j + 4] = 0x01; };
                    if (msgText[i] == '+') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x3E; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '=') { buf[j] = 0x14; buf[j + 1] = 0x14; buf[j + 2] = 0x14; buf[j + 3] = 0x14; buf[j + 4] = 0x14; };
                    if (msgText[i] == '[') { buf[j] = 0; buf[j + 1] = 0x7F; buf[j + 2] = 0x41; buf[j + 3] = 0x41; buf[j + 4] = 0; };
                    if (msgText[i] == '{') { buf[j] = 0x08; buf[j + 1] = 0x08; buf[j + 2] = 0x36; buf[j + 3] = 0x41; buf[j + 4] = 0x41; };
                    if (msgText[i] == ']') { buf[j] = 0; buf[j + 1] = 0x41; buf[j + 2] = 0x41; buf[j + 3] = 0x7F; buf[j + 4] = 0; };
                    if (msgText[i] == '}') { buf[j] = 0x41; buf[j + 1] = 0x41; buf[j + 2] = 0x36; buf[j + 3] = 0x08; buf[j + 4] = 0x08; };
                    if (msgText[i] == '\\') { buf[j] = 0x20; buf[j + 1] = 0x10; buf[j + 2] = 0x08; buf[j + 3] = 4; buf[j + 4] = 0x02; };
                    if (msgText[i] == '|') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x7F; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == ';') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x32; buf[j + 3] = 52; buf[j + 4] = 0; };
                    if (msgText[i] == ':') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x36; buf[j + 3] = 0x36; buf[j + 4] = 0; };
                    if (msgText[i] == '\'') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0x20; buf[j + 3] = 0x40; buf[j + 4] = 0; };
                    if (msgText[i] == '"') { buf[j] = 0; buf[j + 1] = 96; buf[j + 2] = 0; buf[j + 3] = 96; buf[j + 4] = 0; };
                    if (msgText[i] == ',') { buf[j] = 0; buf[j + 1] = 0x01; buf[j + 2] = 0x02; buf[j + 3] = 0; buf[j + 4] = 0; };
                    if (msgText[i] == '<') { buf[j] = 0x08; buf[j + 1] = 0x14; buf[j + 2] = 0x14; buf[j + 3] = 0x22; buf[j + 4] = 0x22; };
                    if (msgText[i] == '.') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 3; buf[j + 3] = 3; buf[j + 4] = 0; };
                    if (msgText[i] == '>') { buf[j] = 0x22; buf[j + 1] = 0x22; buf[j + 2] = 0x14; buf[j + 3] = 0x14; buf[j + 4] = 0x08; };
                    if (msgText[i] == '/') { buf[j] = 0x02; buf[j + 1] = 4; buf[j + 2] = 0x08; buf[j + 3] = 0x10; buf[j + 4] = 0x20; };
                    if (msgText[i] == '?') { buf[j] = 0x20; buf[j + 1] = 0x40; buf[j + 2] = 77; buf[j + 3] = 0x48; buf[j + 4] = 0x30; };
                    if (msgText[i] == ' ') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0; buf[j + 3] = 0; buf[j + 4] = 0; };
                    buf[j + 5] = 0;
                }
                for (int i = buf.Length - (boards * 5); i < buf.Length; i++)
                    buf[i] = 0;
                bufLen = buf.Length - (boards * 5);
                return buf;
            
            
            
            }
            else
            {
                return null;
            }
        }
    }
}
