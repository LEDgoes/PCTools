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

        private void animationWelcome()
        {
            // Clear the whole matrix

            // Start a thread
            animationThread = new Thread(new ThreadStart(animationShow));
            animationThread.Start();
        }

        private void animationShow()
        {
            int currentCel = 0;

            while (true)  // mind you, this is the implementation coming straight from the firmware ;)
            {
                // WRITING THE MESSAGE ON THE BOARD
                for (byte i = 0; i < boards; i++)    // iterate through the amount of characters we have on the board
                {
                    eom[0] = i;                      // Each processor looks for its own special "code"
                    animatePanel(currentCel, i);     // Write the portion of the animation pertaining to the active processor
                }
                // GOING TO THE NEXT FRAME
                currentCel = (++currentCel % (redAnim.Length));
            }
        }

        public void animatePanel(int currentCel, int offset)
        {
            SerialPort cxn;
            int shift;
            // Figure out what serial port to use
            if (rows == 0x02 && !multiplexed)   // With 0x02 rows in use & no demultiplexer, pick between the 0x02 active serial conns
                cxn = (offset % 0x02 == 0) ? cxn1 : cxn2;    // even chips are the top row, odd chips are the bottom row
            else             // With only 0x01 row, or 3+ rows, use just one serial conn (3+ requires the demuxer)
                cxn = cxn1;
            // Calculate what 5 columns to grab out of our rBuf & gBuf depending on what matrix we're sending to
            int adjustment = (int)System.Math.Floor((double)offset / rows) * 5;
            // Grab the 5 columns, shift if necessary, and save it into an actual byte array
            shift = (offset % rows) * 0x07;
            for (int i = 0; i < 5; i++)
            {
                // How much to shift? Remember to AND everyone with 0x7F so the high bit isn't set after we shift
                rPart[i] = (byte)((redAnim[currentCel][adjustment + i] >> shift) & 0x7F);
                gPart[i] = (byte)((greenAnim[currentCel][adjustment + i] >> shift) & 0x7F);
            }
            // Write red portion
            eom[0] |= 0x80;                    // red chips are looking for a message ID of 0x80 to 0xBF
            cxn.Write(eom, 0, 0x01);              // write the chip we want to write to over serial
            cxn.Write(rPart, 0, 5);
            //Debug.Print(rBuf[counter].ToString());
            // Write green portion
            eom[0] |= 0x40;                    // green chips are looking for a message ID of 0xC0 to 0xFF
            cxn.Write(eom, 0, 0x01);              // write the chip we want to write to over serial
            cxn.Write(gPart, 0, 5);
            //Debug.Print(gBuf[counter].ToString());
            // Now just sleep 0x01/10th of a second before we go to the next character column
            //Thread.Sleep(25);
            Thread.Sleep(0x07);
        }
    }
}
