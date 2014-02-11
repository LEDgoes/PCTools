using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.IO.Ports;
using System.Threading;

namespace LEDgoes_Programming_Assistant
{
    public partial class Form1 : Form
    {
        private Array myPort;
        private bool isExePath;
        static string avrPath;
        static string[] outputArray = new string[2];

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            // When our form loads, auto detect all serial ports in the system and populate the COMs Combo box.
            myPort = SerialPort.GetPortNames(); // Get all com ports available
            for (int i = 0; i < myPort.Length; i++)
            {
                choiceCOM1.Items.Add(myPort.GetValue(i));
                choiceCOM2.Items.Add(myPort.GetValue(i));
            }
            choiceCOM1.Text = choiceCOM1.Items[0].ToString();    // Set COMs text to the first COM port detected
            choiceCOM2.Text = choiceCOM2.Items[0].ToString();    // Set COMs text to the second COM port detected
        }

        private void btnProgram_Click(object sender, EventArgs e)
        {
            avrPath = txtAVRdudePath.Text;
            String avrConf = txtAVRdudeConf.Text;
            bool isError = false;

            // First time
            lblStatus.Text = "Status:\nProgramming Green...";
            System.Diagnostics.Process proc1 = new System.Diagnostics.Process();
            proc1.StartInfo.Arguments = "-C \"" + avrConf + "\" -v -v -v -v -p atmega168 -c usbtiny -U flash:w:LEDgoes-green-and-bootloader.hex:i -B 0.666";
            Thread th = new Thread(Form1.runProcess);
            th.Start(proc1);
            while (th.ThreadState != ThreadState.Stopped)
            {
                Application.DoEvents();
            }
            isError |= analyze();
            // Second time
            lblStatus.Text += "\nDone programming Green.  Programming Red...";
            System.Diagnostics.Process proc2 = new System.Diagnostics.Process();
            proc2.StartInfo.Arguments = "-C \"" + avrConf + "\" -v -v -v -v -p atmega168 -c usbtiny -U flash:w:LEDgoes-red-and-bootloader.hex:i -B 0.666";
            th = new Thread(Form1.runProcess);
            th.Start(proc2);
            while (th.ThreadState != ThreadState.Stopped)
            {
                Application.DoEvents();
            }            
            isError |= analyze();
            // Done message
            lblStatus.Text += "\nFinished" + (isError ? " with errors" : "") + ".";
        }

        private static void runProcess(object input)
        {
            System.Diagnostics.Process proc = (System.Diagnostics.Process) input;
            proc.StartInfo.FileName = "\"" + avrPath + "\"";
            //proc.StartInfo.RedirectStandardOutput = true;
            proc.StartInfo.RedirectStandardError = true;
            proc.StartInfo.UseShellExecute = false;
            StringBuilder avrBuffer = new StringBuilder();
            StringBuilder avrError = new StringBuilder();
            //MessageBox.Show(proc.StartInfo.FileName + " " + proc.StartInfo.Arguments);
            proc.Start();
            while (!proc.HasExited)
            {
                //avrBuffer.Append(proc.StandardOutput.ReadToEnd());
                avrError.Append(proc.StandardError.ReadToEnd());
            }
            //avrBuffer.Append(proc.StandardOutput.ReadToEnd());
            avrError.Append(proc.StandardError.ReadToEnd());
            outputArray[0] = "hi"; // avrBuffer.ToString();
            outputArray[1] = avrError.ToString();
        }

        private bool analyze()
        {
            // Look for errors
            String avrBuffer = outputArray[0];
            String avrError = outputArray[1];
            String errMsg;

            // Programmer not connected
            errMsg = "Could not find USBtiny device";
            if (avrBuffer.Contains(errMsg) || avrError.Contains(errMsg))
            {
                lblStatus.Text += "\nProgrammer not connected.";
                return true;
            }
            // avrdude couldn't contact the chip
            errMsg = "not in sync";
            if (avrBuffer.Contains(errMsg) || avrError.Contains(errMsg))
            {
                lblStatus.Text += "\nProgrammer not in sync; check wiring & connections.";
                return true;
            }
            // avrdude contacted the chip, but something's flaky with the connection
            errMsg = "Expected signature for ATMEGA168 is 1E 94 06";
            if (avrBuffer.Contains(errMsg) || avrError.Contains(errMsg))
            {
                lblStatus.Text += "\nDevice signature mismatch; check wiring & connections.";
                return true;
            }
            errMsg = "verification error; content mismatch";
            if (avrBuffer.Contains(errMsg) || avrError.Contains(errMsg))
            {
                lblStatus.Text += "\nProgrammer lost connection in mid-flight; try again.";
                return true;
            }
            // If we made it this far, we must have been OK
            errMsg = "10x3E94 bytes of flash verified";
            if (avrBuffer.Contains(errMsg) || avrError.Contains(errMsg))
                return false;
            // If the status is unknown, say so
            lblStatus.Text += "\nSuccess status not found; try again.";
            return false;
        }

        private void btnAVRexeBrowse_Click(object sender, EventArgs e)
        {
            isExePath = true;
            OFD.ShowDialog();
        }

        private void OFD_FileOk(object sender, CancelEventArgs e)
        {
            if (isExePath)
                txtAVRdudePath.Text = OFD.FileName;
            else
                txtAVRdudeConf.Text = OFD.FileName;
        }

        private void btnAVRconfBrowse_Click(object sender, EventArgs e)
        {
            isExePath = false;
            OFD.ShowDialog();
        }
    }
}
