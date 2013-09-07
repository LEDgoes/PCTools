/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package ledgoes;

import java.io.IOException;

/**
 *
 * @author Stephen
 */
public class DirectDrive extends Thread {
    
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
    static int boards = 8;                  // number of LED display boards in the matrix

    static int maxMsgs = 1;                 // Declare that we will store 1 message
    static int curMsg = 0;                  // This is the message number to fill - set to 0 to fill the 1st message
    static int index_ETX = -1;              // Index of the ETX (end of transmission) character to denote end of message
    static String tmpMsg = "";              // Constructing the message string from the incoming parts over serial

    /**
     * Entry point for the thread.  
     */
    public void run() {
        // Prepare our initial output string
        for (int i = 1; i < 10; i++)
            App.messages[i] = "";
        makeRMessageString(App.messages[0]);
        makeGMessageString(App.messages[0]);
        
        while (true) { // mind you, this is the implementation coming straight from the firmware ;)
            // WRITING THE MESSAGE ON THE BOARD
            for (byte i = 0; i < boards; i++) {    // iterate through the amount of characters we have on the board
                eom[0] = i;                 // Each processor looks for its own special "code"
                writeString(i);             // Write the portion of the string pertaining to the active processor
            }
            counter++;                      // Now go on to show the next character column
            // MESSAGE EXPIRATION
            if (counter >= bufLen) {        // If we've reached the end of the message,
                boolean scrollOnce = false;
                if (scrollOnce) {
                    counter = 0;
                    return;						// On the mobile version, Iteration 1 only has messages scroll by once
                } else {
                    counter = 0;                // reset the column counter to 0
                    redString = "";             // reset the red string to empty
                    greenString = "";           // reset the green string to empty
                    for (int i = maxMsgs - 1; i >= 0; i--)
                    {
                        if (App.messages[i].length() == 0)
                            continue;
                        emptyString = new String();
                        for (int j = 0; j < App.messages[i].length(); j++)  // Make an empty string equal in length to the current message
                            emptyString += ' ';
                        redString += ((i % 2 == 0) ? App.messages[i] : emptyString) + "  ";     // set the red string
                        greenString += ((i % 2 != 0) ? App.messages[i] : emptyString) + "  ";   // set the green string
                    }
                    makeRMessageString(redString);
                    makeGMessageString(greenString);
                }
            }
        }
    }

    public void writeString(int offset) {
        int shift;
        // Figure out what serial port to use
        // Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
        int adjustment = offset * 5;
        // Grab the 5 columns, shift if necessary, and save it into an actual byte array
        shift = 0;
        for (int i = 0; i < 5; i++) {
            // How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
            rPart[i] = (byte) ((rBuf[counter + adjustment + i] >> shift) & 0x7F);
            gPart[i] = (byte) ((gBuf[counter + adjustment + i] >> shift) & 0x7F);
        }
        // Write to the panel
        try {
            // Write red portion
            eom[0] |= 0x80;                    // red chips are looking for a message ID of 0x80 to 0xBF
            App.os1.write(eom);      // write the chip we want to write to over serial
            App.os1.write(rPart);
            //Debug.Print(rBuf[counter].ToString());
            // Write green portion
            eom[0] |= 0x40;                    // green chips are looking for a message ID of 0xC0 to 0xFF
            App.os1.write(eom);      // write the chip we want to write to over serial
            App.os1.write(gPart);
            //Debug.Print(gBuf[counter].ToString());
            // Now just sleep 1/10th of a second before we go to the next character column
            //Thread.Sleep(25);
            // Check for any thread interruptions here
            if (Thread.interrupted()) {
                throw new InterruptedException();
            }
        } catch (InterruptedException e) {
            // We've been interrupted: no more messages.
            return;
        } catch (IOException e) {
            return;
        }
    }

    public void makeRMessageString(String message) {   // Make the message to appear in Red
        rBuf = makeMessageString(message);
    }

    public void makeGMessageString(String message) {   // Make the message to appear in Green
        gBuf = makeMessageString(message);
    }

    public int[] makeMessageString(String message)
    {
        // Make the message string from the letters
        // If rows == 1,
        // Each character takes up 5 columns plus 1 spacer; each board is 5 columns wide
        int[] buf = new int[(message.length() * 6) + (boards * 5)];
        char[] msgText = message.toCharArray();
        for (int i = 0; i < 5; i++)
            buf[i] = 0;
        for (int i = 0, j = 5; i < message.length(); i++, j += 6) {
            // Find out what the letter is
            // Alphabetics - Uppercase
            if (msgText[i] == 'A') { buf[j] = 63; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 63; };
            if (msgText[i] == 'B') { buf[j] = 127; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 54; };
            if (msgText[i] == 'C') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 34; };
            if (msgText[i] == 'D') { buf[j] = 127; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 62; };
            if (msgText[i] == 'E') { buf[j] = 127; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 73; };
            if (msgText[i] == 'F') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 72; };
            if (msgText[i] == 'G') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 46; };
            if (msgText[i] == 'H') { buf[j] = 127; buf[j + 1] = 8; buf[j + 2] = 8; buf[j + 3] = 8; buf[j + 4] = 127; };
            if (msgText[i] == 'I') { buf[j] = 65; buf[j + 1] = 65; buf[j + 2] = 127; buf[j + 3] = 65; buf[j + 4] = 65; };
            if (msgText[i] == 'J') { buf[j] = 2; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'K') { buf[j] = 127; buf[j + 1] = 8; buf[j + 2] = 20; buf[j + 3] = 34; buf[j + 4] = 65; };
            if (msgText[i] == 'L') { buf[j] = 127; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 1; };
            if (msgText[i] == 'M') { buf[j] = 127; buf[j + 1] = 32; buf[j + 2] = 16; buf[j + 3] = 32; buf[j + 4] = 127; };
            if (msgText[i] == 'N') { buf[j] = 127; buf[j + 1] = 32; buf[j + 2] = 16; buf[j + 3] = 8; buf[j + 4] = 127; };
            if (msgText[i] == 'O') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 62; };
            if (msgText[i] == 'P') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 48; };
            if (msgText[i] == 'Q') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 69; buf[j + 3] = 66; buf[j + 4] = 61; };
            if (msgText[i] == 'R') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 76; buf[j + 4] = 51; };
            if (msgText[i] == 'S') { buf[j] = 50; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 38; };
            if (msgText[i] == 'T') { buf[j] = 64; buf[j + 1] = 64; buf[j + 2] = 127; buf[j + 3] = 64; buf[j + 4] = 64; };
            if (msgText[i] == 'U') { buf[j] = 126; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'V') { buf[j] = 124; buf[j + 1] = 2; buf[j + 2] = 1; buf[j + 3] = 2; buf[j + 4] = 124; };
            if (msgText[i] == 'W') { buf[j] = 126; buf[j + 1] = 1; buf[j + 2] = 14; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'X') { buf[j] = 99; buf[j + 1] = 20; buf[j + 2] = 8; buf[j + 3] = 20; buf[j + 4] = 99; };
            if (msgText[i] == 'Y') { buf[j] = 112; buf[j + 1] = 8; buf[j + 2] = 7; buf[j + 3] = 8; buf[j + 4] = 112; };
            if (msgText[i] == 'Z') { buf[j] = 67; buf[j + 1] = 69; buf[j + 2] = 73; buf[j + 3] = 81; buf[j + 4] = 97; };
            // Alphabetics - Lowercase (TODO: still being written as uppercase)
            if (msgText[i] == 'a') { buf[j] = 63; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 63; };
            if (msgText[i] == 'b') { buf[j] = 127; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 54; };
            if (msgText[i] == 'c') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 34; };
            if (msgText[i] == 'd') { buf[j] = 127; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 62; };
            if (msgText[i] == 'e') { buf[j] = 127; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 73; };
            if (msgText[i] == 'f') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 72; };
            if (msgText[i] == 'g') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 46; };
            if (msgText[i] == 'h') { buf[j] = 127; buf[j + 1] = 8; buf[j + 2] = 8; buf[j + 3] = 8; buf[j + 4] = 127; };
            if (msgText[i] == 'i') { buf[j] = 65; buf[j + 1] = 65; buf[j + 2] = 127; buf[j + 3] = 65; buf[j + 4] = 65; };
            if (msgText[i] == 'j') { buf[j] = 2; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'k') { buf[j] = 127; buf[j + 1] = 8; buf[j + 2] = 20; buf[j + 3] = 34; buf[j + 4] = 65; };
            if (msgText[i] == 'l') { buf[j] = 127; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 1; };
            if (msgText[i] == 'm') { buf[j] = 127; buf[j + 1] = 32; buf[j + 2] = 16; buf[j + 3] = 32; buf[j + 4] = 127; };
            if (msgText[i] == 'n') { buf[j] = 127; buf[j + 1] = 32; buf[j + 2] = 16; buf[j + 3] = 8; buf[j + 4] = 127; };
            if (msgText[i] == 'o') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 62; };
            if (msgText[i] == 'p') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 72; buf[j + 4] = 48; };
            if (msgText[i] == 'q') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 69; buf[j + 3] = 66; buf[j + 4] = 61; };
            if (msgText[i] == 'r') { buf[j] = 127; buf[j + 1] = 72; buf[j + 2] = 72; buf[j + 3] = 76; buf[j + 4] = 51; };
            if (msgText[i] == 's') { buf[j] = 50; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 38; };
            if (msgText[i] == 't') { buf[j] = 64; buf[j + 1] = 64; buf[j + 2] = 127; buf[j + 3] = 64; buf[j + 4] = 64; };
            if (msgText[i] == 'u') { buf[j] = 126; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'v') { buf[j] = 124; buf[j + 1] = 2; buf[j + 2] = 1; buf[j + 3] = 2; buf[j + 4] = 124; };
            if (msgText[i] == 'w') { buf[j] = 126; buf[j + 1] = 1; buf[j + 2] = 14; buf[j + 3] = 1; buf[j + 4] = 126; };
            if (msgText[i] == 'x') { buf[j] = 99; buf[j + 1] = 20; buf[j + 2] = 8; buf[j + 3] = 20; buf[j + 4] = 99; };
            if (msgText[i] == 'y') { buf[j] = 112; buf[j + 1] = 8; buf[j + 2] = 7; buf[j + 3] = 8; buf[j + 4] = 112; };
            if (msgText[i] == 'z') { buf[j] = 67; buf[j + 1] = 69; buf[j + 2] = 73; buf[j + 3] = 81; buf[j + 4] = 97; };

            // Numbers
            if (msgText[i] == '1') { buf[j] = 1; buf[j + 1] = 33; buf[j + 2] = 127; buf[j + 3] = 1; buf[j + 4] = 1; };
            if (msgText[i] == '2') { buf[j] = 39; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 49; };
            if (msgText[i] == '3') { buf[j] = 34; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 54; };
            if (msgText[i] == '4') { buf[j] = 120; buf[j + 1] = 8; buf[j + 2] = 8; buf[j + 3] = 8; buf[j + 4] = 127; };
            if (msgText[i] == '5') { buf[j] = 122; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 70; };
            if (msgText[i] == '6') { buf[j] = 62; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 6; };
            if (msgText[i] == '7') { buf[j] = 64; buf[j + 1] = 64; buf[j + 2] = 71; buf[j + 3] = 72; buf[j + 4] = 112; };
            if (msgText[i] == '8') { buf[j] = 54; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 54; };
            if (msgText[i] == '9') { buf[j] = 48; buf[j + 1] = 73; buf[j + 2] = 73; buf[j + 3] = 73; buf[j + 4] = 62; };
            if (msgText[i] == '0') { buf[j] = 62; buf[j + 1] = 69; buf[j + 2] = 73; buf[j + 3] = 81; buf[j + 4] = 62; };

            // Symbols in keyboard order
            if (msgText[i] == '~') { buf[j] = 8; buf[j + 1] = 16; buf[j + 2] = 8; buf[j + 3] = 4; buf[j + 4] = 8; };
            if (msgText[i] == '`') { buf[j] = 0; buf[j + 1] = 64; buf[j + 2] = 32; buf[j + 3] = 0; buf[j + 4] = 0; };
            if (msgText[i] == '!') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 125; buf[j + 3] = 0; buf[j + 4] = 0; };
            if (msgText[i] == '@') { buf[j] = 62; buf[j + 1] = 65; buf[j + 2] = 93; buf[j + 3] = 85; buf[j + 4] = 56; };
            if (msgText[i] == '#') { buf[j] = 20; buf[j + 1] = 62; buf[j + 2] = 20; buf[j + 3] = 62; buf[j + 4] = 20; };
            if (msgText[i] == '$') { buf[j] = 18; buf[j + 1] = 42; buf[j + 2] = 127; buf[j + 3] = 42; buf[j + 4] = 36; };
            if (msgText[i] == '%') { buf[j] = 99; buf[j + 1] = 100; buf[j + 2] = 8; buf[j + 3] = 19; buf[j + 4] = 99; };
            if (msgText[i] == '^') { buf[j] = 16; buf[j + 1] = 32; buf[j + 2] = 64; buf[j + 3] = 32; buf[j + 4] = 16; };
            if (msgText[i] == '&') { buf[j] = 54; buf[j + 1] = 73; buf[j + 2] = 53; buf[j + 3] = 2; buf[j + 4] = 13; };
            if (msgText[i] == '*') { buf[j] = 20; buf[j + 1] = 8; buf[j + 2] = 62; buf[j + 3] = 8; buf[j + 4] = 20; };
            if (msgText[i] == '(') { buf[j] = 0; buf[j + 1] = 28; buf[j + 2] = 34; buf[j + 3] = 65; buf[j + 4] = 0; };
            if (msgText[i] == ')') { buf[j] = 0; buf[j + 1] = 65; buf[j + 2] = 34; buf[j + 3] = 28; buf[j + 4] = 0; };
            if (msgText[i] == '-') { buf[j] = 8; buf[j + 1] = 8; buf[j + 2] = 8; buf[j + 3] = 8; buf[j + 4] = 8; };
            if (msgText[i] == '_') { buf[j] = 1; buf[j + 1] = 1; buf[j + 2] = 1; buf[j + 3] = 1; buf[j + 4] = 1; };
            if (msgText[i] == '+') { buf[j] = 8; buf[j + 1] = 8; buf[j + 2] = 62; buf[j + 3] = 8; buf[j + 4] = 8; };
            if (msgText[i] == '=') { buf[j] = 20; buf[j + 1] = 20; buf[j + 2] = 20; buf[j + 3] = 20; buf[j + 4] = 20; };
            if (msgText[i] == '[') { buf[j] = 0; buf[j + 1] = 127; buf[j + 2] = 65; buf[j + 3] = 65; buf[j + 4] = 0; };
            if (msgText[i] == '{') { buf[j] = 8; buf[j + 1] = 8; buf[j + 2] = 54; buf[j + 3] = 65; buf[j + 4] = 65; };
            if (msgText[i] == ']') { buf[j] = 0; buf[j + 1] = 65; buf[j + 2] = 65; buf[j + 3] = 127; buf[j + 4] = 0; };
            if (msgText[i] == '}') { buf[j] = 65; buf[j + 1] = 65; buf[j + 2] = 54; buf[j + 3] = 8; buf[j + 4] = 8; };
            if (msgText[i] == '\\') { buf[j] = 32; buf[j + 1] = 16; buf[j + 2] = 8; buf[j + 3] = 4; buf[j + 4] = 2; };
            if (msgText[i] == '|') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 127; buf[j + 3] = 0; buf[j + 4] = 0; };
            if (msgText[i] == ';') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 50; buf[j + 3] = 52; buf[j + 4] = 0; };
            if (msgText[i] == ':') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 54; buf[j + 3] = 54; buf[j + 4] = 0; };
            if (msgText[i] == '\'') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 32; buf[j + 3] = 64; buf[j + 4] = 0; };
            if (msgText[i] == '"') { buf[j] = 0; buf[j + 1] = 96; buf[j + 2] = 0; buf[j + 3] = 96; buf[j + 4] = 0; };
            if (msgText[i] == ',') { buf[j] = 0; buf[j + 1] = 1; buf[j + 2] = 2; buf[j + 3] = 0; buf[j + 4] = 0; };
            if (msgText[i] == '<') { buf[j] = 8; buf[j + 1] = 20; buf[j + 2] = 20; buf[j + 3] = 34; buf[j + 4] = 34; };
            if (msgText[i] == '.') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 3; buf[j + 3] = 3; buf[j + 4] = 0; };
            if (msgText[i] == '>') { buf[j] = 34; buf[j + 1] = 34; buf[j + 2] = 20; buf[j + 3] = 20; buf[j + 4] = 8; };
            if (msgText[i] == '/') { buf[j] = 2; buf[j + 1] = 4; buf[j + 2] = 8; buf[j + 3] = 16; buf[j + 4] = 32; };
            if (msgText[i] == '?') { buf[j] = 32; buf[j + 1] = 64; buf[j + 2] = 77; buf[j + 3] = 72; buf[j + 4] = 48; };
            if (msgText[i] == ' ') { buf[j] = 0; buf[j + 1] = 0; buf[j + 2] = 0; buf[j + 3] = 0; buf[j + 4] = 0; };
            buf[j + 5] = 0;
        }
        for (int i = buf.length - (boards * 5); i < buf.length; i++)
            buf[i] = 0;
        bufLen = buf.length - (boards * 5);
        return buf;
    }
}
