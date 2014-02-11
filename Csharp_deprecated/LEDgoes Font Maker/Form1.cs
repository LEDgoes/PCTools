using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Windows;

namespace LEDgoes_Font_Maker
{
    public partial class Form1 : Form
    {
        public Button[] buttonArray;
        public bool mouseDown;

        public Form1()
        {
            InitializeComponent();
        }

        private void Form1_Load(object sender, EventArgs e)
        {
            CreatingNewButtons();
        }

        private void CreatingNewButtons()
        {
            buttonArray = new Button[140];
            int horizontal = 30;
            int vertical = 550;

            for (int i = 0; i < buttonArray.Length; i++)
            {
                buttonArray[i] = new Button();
                buttonArray[i].Size = new Size(39, 39);
                buttonArray[i].Location = new Point(horizontal, vertical);
                buttonArray[i].AllowDrop = true;
                buttonArray[i].MouseDown += new MouseEventHandler(this.Onb2Down);
                buttonArray[i].MouseUp += new MouseEventHandler(this.Onb2Up);
                buttonArray[i].DragEnter += new System.Windows.Forms.DragEventHandler(this.Onb2Enter);
                buttonArray[i].Tag = i.ToString();
                buttonArray[i].BackColor = Color.DarkGray;
                if ((i + 1) % 14 == 0)
                {
                    vertical = 550;
                    horizontal += 40;
                }
                else
                    vertical -= 40;
                this.Controls.Add(buttonArray[i]);
            }
        }

        void Onb2Down(object sender, EventArgs e)
        {
            mouseDown = true;
            DoDragDrop(0, System.Windows.Forms.DragDropEffects.All);
            Console.WriteLine("MouseDown");
        }

        void Onb2Up(object sender, EventArgs e)
        {
            mouseDown = false;
            Console.WriteLine("MouseUp");
        }

        void Onb2Enter(object sender, System.Windows.Forms.DragEventArgs e)
        {
            if (!mouseDown)
                return;
            Console.WriteLine("MouseOver");
            Button btn = (Button)sender;
            if (btn.BackColor == Color.Red)
                btn.BackColor = Color.DarkGray;
            else
                btn.BackColor = Color.Red;
        }

        private void btnCode_Click(object sender, EventArgs e)
        {
            int[] buf = new int[10];
            // Solve for which buttons were clicked
            for (int i = 0; i < buttonArray.Length / 14; i++)
            {
                // i = the column index
                for (int j = i * 14, k = 0; j < (i + 1) * 14; j++, k++)
                {
                    // j = the button ID within the column
                    // k = the LED index within the column, starting from the bottom; equals j - (i * 14)
                    if (buttonArray[j].BackColor == Color.Red)
                        buf[i] |= (1 << k);
                }
            }
            // Post what the code is to make this character happen
            txtCode.Text = "if (msgText[i] == '" + txtLetter.Text + "') { ";
            for (int i = 0; i < 10; i++) {
                txtCode.Text += "buf[j";
                if (i > 0)
                    txtCode.Text += " + " + i;
                txtCode.Text += "] = " + buf[i] + "; ";
            }
            txtCode.Text += "};";
        }

        private void btnClearAll_Click(object sender, EventArgs e)
        {
            for (int i = 0; i < buttonArray.Length; i++)
            {
                buttonArray[i].BackColor = Color.DarkGray;
            }
            txtCode.Text = "";
        }
    }
}
