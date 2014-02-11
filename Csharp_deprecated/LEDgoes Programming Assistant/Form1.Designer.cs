namespace LEDgoes_Programming_Assistant
{
    partial class Form1
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.choiceCOM2 = new System.Windows.Forms.ComboBox();
            this.choiceCOM1 = new System.Windows.Forms.ComboBox();
            this.lblCOM2 = new System.Windows.Forms.Label();
            this.lblCOM1 = new System.Windows.Forms.Label();
            this.btnProgram = new System.Windows.Forms.Button();
            this.lblStatus = new System.Windows.Forms.Label();
            this.label1 = new System.Windows.Forms.Label();
            this.txtAVRdudePath = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.txtAVRdudeConf = new System.Windows.Forms.TextBox();
            this.choiceSCLK = new System.Windows.Forms.ComboBox();
            this.label3 = new System.Windows.Forms.Label();
            this.btnAVRexeBrowse = new System.Windows.Forms.Button();
            this.btnAVRconfBrowse = new System.Windows.Forms.Button();
            this.OFD = new System.Windows.Forms.OpenFileDialog();
            this.SuspendLayout();
            // 
            // choiceCOM2
            // 
            this.choiceCOM2.FormattingEnabled = true;
            this.choiceCOM2.Location = new System.Drawing.Point(122, 29);
            this.choiceCOM2.Name = "choiceCOM2";
            this.choiceCOM2.Size = new System.Drawing.Size(121, 21);
            this.choiceCOM2.TabIndex = 8;
            // 
            // choiceCOM1
            // 
            this.choiceCOM1.FormattingEnabled = true;
            this.choiceCOM1.Location = new System.Drawing.Point(122, 6);
            this.choiceCOM1.Name = "choiceCOM1";
            this.choiceCOM1.Size = new System.Drawing.Size(121, 21);
            this.choiceCOM1.TabIndex = 7;
            // 
            // lblCOM2
            // 
            this.lblCOM2.AutoSize = true;
            this.lblCOM2.Location = new System.Drawing.Point(12, 32);
            this.lblCOM2.Name = "lblCOM2";
            this.lblCOM2.Size = new System.Drawing.Size(104, 13);
            this.lblCOM2.TabIndex = 6;
            this.lblCOM2.Text = "Arduino 2 COM Port:";
            // 
            // lblCOM1
            // 
            this.lblCOM1.AutoSize = true;
            this.lblCOM1.Location = new System.Drawing.Point(12, 9);
            this.lblCOM1.Name = "lblCOM1";
            this.lblCOM1.Size = new System.Drawing.Size(104, 13);
            this.lblCOM1.TabIndex = 5;
            this.lblCOM1.Text = "Arduino 1 COM Port:";
            // 
            // btnProgram
            // 
            this.btnProgram.Location = new System.Drawing.Point(15, 143);
            this.btnProgram.Name = "btnProgram";
            this.btnProgram.Size = new System.Drawing.Size(228, 45);
            this.btnProgram.TabIndex = 9;
            this.btnProgram.Text = "Program LEDgoes Boards";
            this.btnProgram.UseVisualStyleBackColor = true;
            this.btnProgram.Click += new System.EventHandler(this.btnProgram_Click);
            // 
            // lblStatus
            // 
            this.lblStatus.AutoSize = true;
            this.lblStatus.Location = new System.Drawing.Point(269, 125);
            this.lblStatus.Name = "lblStatus";
            this.lblStatus.Size = new System.Drawing.Size(43, 13);
            this.lblStatus.TabIndex = 10;
            this.lblStatus.Text = "Status: ";
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(12, 58);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(106, 13);
            this.label1.TabIndex = 11;
            this.label1.Text = "Path to avrdude.exe:";
            // 
            // txtAVRdudePath
            // 
            this.txtAVRdudePath.Location = new System.Drawing.Point(122, 55);
            this.txtAVRdudePath.Name = "txtAVRdudePath";
            this.txtAVRdudePath.Size = new System.Drawing.Size(344, 20);
            this.txtAVRdudePath.TabIndex = 12;
            this.txtAVRdudePath.Text = "C:\\Program Files (x86)\\Arduino\\hardware\\tools\\avr\\bin\\avrdude.exe";
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(12, 80);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(110, 13);
            this.label2.TabIndex = 13;
            this.label2.Text = "Path to avrdude.conf:";
            // 
            // txtAVRdudeConf
            // 
            this.txtAVRdudeConf.Location = new System.Drawing.Point(122, 77);
            this.txtAVRdudeConf.Name = "txtAVRdudeConf";
            this.txtAVRdudeConf.Size = new System.Drawing.Size(344, 20);
            this.txtAVRdudeConf.TabIndex = 14;
            this.txtAVRdudeConf.Text = "C:\\Program Files (x86)\\Arduino\\hardware\\tools\\avr\\etc\\avrdude.conf";
            // 
            // choiceSCLK
            // 
            this.choiceSCLK.FormattingEnabled = true;
            this.choiceSCLK.Items.AddRange(new object[] {
            "0.666",
            "1"});
            this.choiceSCLK.Location = new System.Drawing.Point(122, 102);
            this.choiceSCLK.Name = "choiceSCLK";
            this.choiceSCLK.Size = new System.Drawing.Size(121, 21);
            this.choiceSCLK.TabIndex = 16;
            this.choiceSCLK.Text = "0.666";
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(12, 105);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(104, 13);
            this.label3.TabIndex = 15;
            this.label3.Text = "Serial Clock Scaling:";
            // 
            // btnAVRexeBrowse
            // 
            this.btnAVRexeBrowse.Location = new System.Drawing.Point(472, 53);
            this.btnAVRexeBrowse.Name = "btnAVRexeBrowse";
            this.btnAVRexeBrowse.Size = new System.Drawing.Size(75, 23);
            this.btnAVRexeBrowse.TabIndex = 17;
            this.btnAVRexeBrowse.Text = "Browse...";
            this.btnAVRexeBrowse.UseVisualStyleBackColor = true;
            this.btnAVRexeBrowse.Click += new System.EventHandler(this.btnAVRexeBrowse_Click);
            // 
            // btnAVRconfBrowse
            // 
            this.btnAVRconfBrowse.Location = new System.Drawing.Point(472, 74);
            this.btnAVRconfBrowse.Name = "btnAVRconfBrowse";
            this.btnAVRconfBrowse.Size = new System.Drawing.Size(75, 23);
            this.btnAVRconfBrowse.TabIndex = 18;
            this.btnAVRconfBrowse.Text = "Browse...";
            this.btnAVRconfBrowse.UseVisualStyleBackColor = true;
            this.btnAVRconfBrowse.Click += new System.EventHandler(this.btnAVRconfBrowse_Click);
            // 
            // OFD
            // 
            this.OFD.FileName = "avrdude.exe";
            this.OFD.Title = "Select avrdude.exe";
            this.OFD.FileOk += new System.ComponentModel.CancelEventHandler(this.OFD_FileOk);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(559, 262);
            this.Controls.Add(this.btnAVRconfBrowse);
            this.Controls.Add(this.btnAVRexeBrowse);
            this.Controls.Add(this.choiceSCLK);
            this.Controls.Add(this.label3);
            this.Controls.Add(this.txtAVRdudeConf);
            this.Controls.Add(this.label2);
            this.Controls.Add(this.txtAVRdudePath);
            this.Controls.Add(this.label1);
            this.Controls.Add(this.lblStatus);
            this.Controls.Add(this.btnProgram);
            this.Controls.Add(this.choiceCOM2);
            this.Controls.Add(this.choiceCOM1);
            this.Controls.Add(this.lblCOM2);
            this.Controls.Add(this.lblCOM1);
            this.Name = "Form1";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.ComboBox choiceCOM2;
        private System.Windows.Forms.ComboBox choiceCOM1;
        private System.Windows.Forms.Label lblCOM2;
        private System.Windows.Forms.Label lblCOM1;
        private System.Windows.Forms.Button btnProgram;
        private System.Windows.Forms.Label lblStatus;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox txtAVRdudePath;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.TextBox txtAVRdudeConf;
        private System.Windows.Forms.ComboBox choiceSCLK;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.Button btnAVRexeBrowse;
        private System.Windows.Forms.Button btnAVRconfBrowse;
        private System.Windows.Forms.OpenFileDialog OFD;
    }
}

