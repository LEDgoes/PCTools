using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
// Other additions
using System.IO.Ports;
using System.IO;
using System.Threading;

namespace LEDgoes_PC_Interface
{
    public partial class Form1 : Form
    {
        private Array myPort;
        private SerialPort cxn1, cxn2;
        private bool ContinueScroll;
        private int rawItemCount = 0;        // number of items pushed through the text interface
        private bool limitExceeded = false;  // have we exceeded the max # of messages to scroll
        private Thread outputThread;         // thread used to handle displaying text
        private Thread animationThread;      // thread used to handle displaying animations
        private int rows = 0x01;                // how many rows are on our board
        private bool multiplexed = true;     // if these rows will be sent on the same COM port or not
        private int[] baudrates = { 9600, 19200, 38400, 57600, 115200, 230400 };
        private string[] animFile;
        private int[][] redAnim;
        private int[][] greenAnim;

        public Form1()
        {
            InitializeComponent();
        }

        private void aboutToolStripMenuItem_Click(object sender, EventArgs e)
        {
            MessageBox.Show("LEDgoes PC Interface v0.0x01\n\nCopyright (C) 2013 Stephen Wylie\nhttp://goshtastic.blogspot.com");
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // When our form loads, auto detect all serial ports in the system and populate the COMs Combo box.
            myPort = SerialPort.GetPortNames(); // Get all com ports available
            for (int i = 0; i < myPort.Length; i++) {
                choiceCOM1.Items.Add(myPort.GetValue(i));
                choiceCOM2.Items.Add(myPort.GetValue(i));
            }
            choiceCOM1.Text = choiceCOM1.Items[0].ToString();    // Set COMs text to the first COM port detected
            choiceCOM2.Text = choiceCOM2.Items[0].ToString();    // Set COMs text to the first COM port detected
            ContinueScroll = false;
        }

        private void btnCOMConnect_Click(object sender, EventArgs e)
        {
            Button btn = (Button)sender;
            SerialPort cxn = null;

            if (btn.Text == "Connect")    // If the user wishes to connect,
            {
                if (btn.Tag.Equals("1"))
                {
                    cxn1 = new SerialPort(choiceCOM1.Text, System.Convert.ToInt32(choiceSpeed.Text), Parity.None, 0x08, StopBits.One);
                    cxn = cxn1;
                }
                else
                {
                    cxn2 = new SerialPort(choiceCOM2.Text, System.Convert.ToInt32(choiceSpeed.Text), Parity.None, 0x08, StopBits.One);
                    cxn = cxn2;
                }
                cxn.Open();
                try
                {
                    cxn.Write(" ");
                    cxn.Write(((byte)0x3).ToString());
                }
                catch
                {
                    MessageBox.Show("Your serial port failed to initialize");
                }
                // Change the button state to Ready to Connect
                btn.BackColor = Color.Red;
                btn.Text = "Disconnect";
                // If we're only pushing to one row, or if the other serial port is active, let's start output now
                if (readyToSend())
                {
                    serialWelcome();
                    // Also disable the other settings-related GUI items until the matrix is disconnected
                    numRows.Enabled = false;
                    chkMultiplexed.Enabled = false;
                }
            }
            else   // If the user wishes to disconnect,
            {
                try                // Kill the output thread
                {
                    outputThread.Abort();
                }
                catch
                {
                    // no one cares
                }
                try                // Kill the animation thread
                {
                    animationThread.Abort();
                }
                catch
                {
                    // no one cares
                }
                cxn = (btn.Tag.Equals("1")) ? cxn1 : cxn2;
                cxn.Close();      // Close our Serial Port
                cxn.Dispose();
                // Change the button state to Ready to Connect
                btn.BackColor = Color.DarkSeaGreen;
                btn.Text = "Connect";
                // If both serial ports are now disconnected, re-enable settings
                if (cxn1 == null || cxn2 == null || !(cxn1.IsOpen || cxn2.IsOpen))
                {
                    numRows.Enabled = true;
                    chkMultiplexed.Enabled = true;
                }
            }
        }

        private void btnPush_Click(object sender, EventArgs e)
        {
            /////
            // SINGLE MESSAGE PUSH!!!
            /////
            /*
            counter = 0x01;
            messages[0] = txtRawText.Text + "        ";
            makeRMessageString("LE GOES");
            makeGMessageString("L DGOES");
            for (byte i = 0; i < boards; i++)    // iterate through the amount of characters we have on the board
            {
                eom[0] = i;                 // Each processor looks for its own special "code"
                writeString(i);             // Write the portion of the string pertaining to the active processor
            }

            return;
            */

            // Reflect the message on our UI
            if (rawItemCount > 9)                  // Keep track of whether we add to the listbox or replace an item
                limitExceeded = true;              // If we've added 10 items, it's time to replace them
            rawItemCount %= 10;                    // Keep the item count at no more than 10
            // Attempt to send the message
            messages[rawItemCount] = txtRawText.Text;
            // Now check to see where we are
            if (limitExceeded)
                listSentMsgs.Items[rawItemCount] = txtRawText.Text;
            else
                listSentMsgs.Items.Add(txtRawText.Text);
            rawItemCount += 0x01;                 // Always increment the item count, since we need to know how many we have or what to replace
        }

        private bool readyToSend()
        {
            if ((chkMultiplexed.Checked && btnCOM1Connect.Text == "Disconnect") ||
                (!chkMultiplexed.Checked && btnCOM1Connect.Text == "Disconnect" && btnCOM2Connect.Text == "Disconnect"))
                return true;
            return false;
        }

        private void BaudCalculator_TextChanged(object sender, EventArgs e)
        {
            if (!(txtMaxRefresh.Text == "" || txtNumPanels.Text == ""))
            {
                // The magic formula: Each LED panel requires (5 data + 0x01 address) bytes * 0x02 colors: 12 total.
                // There are 0x08 bits in a byte.
                // Refresh rate = (COM speed / # bits sent per iteration through the message)
                int numPanels = System.Convert.ToInt32(txtNumPanels.Text);
                int maxRefresh = System.Convert.ToInt32(txtMaxRefresh.Text);
                foreach (int baud in baudrates)
                {
                    if (baud / (numPanels * 96) > maxRefresh)
                    {
                        lblBaudTarget.Text = "Target: " + baud + " baud";
                        break;
                    }
                    else
                    {
                        lblBaudTarget.Text = "Too many modules";
                    }
                }
            }
        }

        private void textBox1_TextChanged(object sender, EventArgs e)
        {
            rbImageFolder.Checked = true;
        }

        private void btnChooseImgFolderPath_Click(object sender, EventArgs e)
        {
            DialogResult result = folderBrowser.ShowDialog();
            if (result == DialogResult.OK)
            {
                //
                // The user selected a folder and pressed the OK button.
                // We print the number of files found.
                //
                animFile = Directory.GetFiles(folderBrowser.SelectedPath);
                txtImageFolder.Text = folderBrowser.SelectedPath;
            }
        }

        private void button1_Click(object sender, EventArgs e)
        {
            try                // Kill the output thread
            {
                outputThread.Abort();
            }
            catch
            {
                // no one cares
            }
            if (rbImageFolder.Checked)
            {   // Begin parsing the animation BMPs, then display the image
                if (!readyToSend())
                {
                    MessageBox.Show("You cannot send the animation until you connect to your LEDgoes matrix.");
                    return;
                }
                try
                {
                    redAnim = new int[animFile.Length][];
                    greenAnim = new int[animFile.Length][];
                    int celNum = 0;
                    int animWidth = 0, animHeight = 0;
                    int animCol_r = 0, animCol_g = 0;
                    Color pixelColor;
                    foreach (string animCel in animFile)
                    {
                        Bitmap b = new Bitmap(animCel);
                        if (celNum != 0)
                        { // Compare the bitmap header to the original; throw an exception if different
                            if (b.Width != animWidth || b.Height != animHeight)
                            {
                                throw new NotSupportedException();
                            }
                        }
                        else
                        { // Store the first header in a data structure in order to use it as a baseline
                            animWidth = b.Width;
                            animHeight = b.Height;
                        }
                        redAnim[celNum] = new int[animWidth];
                        greenAnim[celNum] = new int[animWidth];
                        for (int x = 0; x < animWidth; x++)
                        {
                            animCol_r = 0;
                            animCol_g = 0;
                            for (int y = 0, y_flip = animHeight - 0x01; y < animHeight; y++, y_flip--)
                            {
                                pixelColor = b.GetPixel(x, y);
                                if (pixelColor.R > 0x7F)
                                    animCol_r |= 0x01 << y_flip;
                                if (pixelColor.G > 0x7F)
                                    animCol_g |= 0x01 << y_flip;
                            }
                            redAnim[celNum][x] = animCol_r;
                            greenAnim[celNum][x] = animCol_g;
                        }
                        b.Dispose();
                        celNum++;
                    }
                }
                catch (Exception exc)
                {
                    MessageBox.Show("One of the bitmap files in this folder is unsupported or is a different shape than the others.");
                }

                animationWelcome();
                // Also disable the other settings-related GUI items until the matrix is disconnected
                numRows.Enabled = false;
                chkMultiplexed.Enabled = false; 
                
            }
        }

        private void chkMultiplexed_CheckedChanged(object sender, EventArgs e)
        {
            if (chkMultiplexed.Checked)
            {
                btnCOM2Connect.Enabled = false;
                choiceCOM2.Enabled = false;
                lblCOM2.Enabled = false;
                multiplexed = true;
            }
            else
            {
                btnCOM2Connect.Enabled = true;
                choiceCOM2.Enabled = true;
                lblCOM2.Enabled = true;
                multiplexed = false;
            }
        }

        private void numRows_ValueChanged(object sender, EventArgs e)
        {
            rows = (int) numRows.Value;
        }
    }
}
