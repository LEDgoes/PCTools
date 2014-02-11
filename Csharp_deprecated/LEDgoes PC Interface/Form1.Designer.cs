namespace LEDgoes_PC_Interface
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
            System.ComponentModel.ComponentResourceManager resources = new System.ComponentModel.ComponentResourceManager(typeof(Form1));
            this.lblCOM1 = new System.Windows.Forms.Label();
            this.groupRow = new System.Windows.Forms.GroupBox();
            this.lblCOM2 = new System.Windows.Forms.Label();
            this.choiceCOM1 = new System.Windows.Forms.ComboBox();
            this.choiceCOM2 = new System.Windows.Forms.ComboBox();
            this.tabs = new System.Windows.Forms.TabControl();
            this.tabRawText = new System.Windows.Forms.TabPage();
            this.btnReplace = new System.Windows.Forms.Button();
            this.btnPush = new System.Windows.Forms.Button();
            this.txtRawText = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.listSentMsgs = new System.Windows.Forms.ListBox();
            this.tabTwitter = new System.Windows.Forms.TabPage();
            this.textBox2 = new System.Windows.Forms.TextBox();
            this.button3 = new System.Windows.Forms.Button();
            this.label5 = new System.Windows.Forms.Label();
            this.label4 = new System.Windows.Forms.Label();
            this.tabAnim = new System.Windows.Forms.TabPage();
            this.btnChooseAVIPath = new System.Windows.Forms.Button();
            this.btnChooseGIFPath = new System.Windows.Forms.Button();
            this.btnChooseImgFolderPath = new System.Windows.Forms.Button();
            this.txtAVIPath = new System.Windows.Forms.TextBox();
            this.txtGIFPath = new System.Windows.Forms.TextBox();
            this.txtImageFolder = new System.Windows.Forms.TextBox();
            this.button1 = new System.Windows.Forms.Button();
            this.rbAVIPath = new System.Windows.Forms.RadioButton();
            this.rbGIFPath = new System.Windows.Forms.RadioButton();
            this.rbImageFolder = new System.Windows.Forms.RadioButton();
            this.tabSim = new System.Windows.Forms.TabPage();
            this.tabBauds = new System.Windows.Forms.TabPage();
            this.txtMaxRefresh = new System.Windows.Forms.MaskedTextBox();
            this.txtNumPanels = new System.Windows.Forms.MaskedTextBox();
            this.lblBaudTarget = new System.Windows.Forms.Label();
            this.lblMaxRefresh = new System.Windows.Forms.Label();
            this.lblTotPanels = new System.Windows.Forms.Label();
            this.lblBaudRateHelp = new System.Windows.Forms.Label();
            this.btnCOM1Connect = new System.Windows.Forms.Button();
            this.btnCOM2Connect = new System.Windows.Forms.Button();
            this.menuStrip1 = new System.Windows.Forms.MenuStrip();
            this.helpToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.aboutToolStripMenuItem = new System.Windows.Forms.ToolStripMenuItem();
            this.lblSpeed = new System.Windows.Forms.Label();
            this.choiceSpeed = new System.Windows.Forms.ComboBox();
            this.folderBrowser = new System.Windows.Forms.FolderBrowserDialog();
            this.numRows = new System.Windows.Forms.NumericUpDown();
            this.chkMultiplexed = new System.Windows.Forms.CheckBox();
            this.groupRow.SuspendLayout();
            this.tabs.SuspendLayout();
            this.tabRawText.SuspendLayout();
            this.tabTwitter.SuspendLayout();
            this.tabAnim.SuspendLayout();
            this.tabBauds.SuspendLayout();
            this.menuStrip1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numRows)).BeginInit();
            this.SuspendLayout();
            // 
            // lblCOM1
            // 
            this.lblCOM1.AutoSize = true;
            this.lblCOM1.Location = new System.Drawing.Point(150, 58);
            this.lblCOM1.Name = "lblCOM1";
            this.lblCOM1.Size = new System.Drawing.Size(90, 13);
            this.lblCOM1.TabIndex = 0;
            this.lblCOM1.Text = "Row 1 COM Port:";
            // 
            // groupRow
            // 
            this.groupRow.Controls.Add(this.chkMultiplexed);
            this.groupRow.Controls.Add(this.numRows);
            this.groupRow.Location = new System.Drawing.Point(16, 27);
            this.groupRow.Name = "groupRow";
            this.groupRow.Size = new System.Drawing.Size(111, 89);
            this.groupRow.TabIndex = 1;
            this.groupRow.TabStop = false;
            this.groupRow.Text = "Rows";
            // 
            // lblCOM2
            // 
            this.lblCOM2.AutoSize = true;
            this.lblCOM2.Enabled = false;
            this.lblCOM2.Location = new System.Drawing.Point(150, 81);
            this.lblCOM2.Name = "lblCOM2";
            this.lblCOM2.Size = new System.Drawing.Size(90, 13);
            this.lblCOM2.TabIndex = 2;
            this.lblCOM2.Text = "Row 2 COM Port:";
            // 
            // choiceCOM1
            // 
            this.choiceCOM1.FormattingEnabled = true;
            this.choiceCOM1.Location = new System.Drawing.Point(246, 55);
            this.choiceCOM1.Name = "choiceCOM1";
            this.choiceCOM1.Size = new System.Drawing.Size(121, 21);
            this.choiceCOM1.TabIndex = 3;
            // 
            // choiceCOM2
            // 
            this.choiceCOM2.Enabled = false;
            this.choiceCOM2.FormattingEnabled = true;
            this.choiceCOM2.Location = new System.Drawing.Point(246, 78);
            this.choiceCOM2.Name = "choiceCOM2";
            this.choiceCOM2.Size = new System.Drawing.Size(121, 21);
            this.choiceCOM2.TabIndex = 4;
            // 
            // tabs
            // 
            this.tabs.Controls.Add(this.tabRawText);
            this.tabs.Controls.Add(this.tabTwitter);
            this.tabs.Controls.Add(this.tabAnim);
            this.tabs.Controls.Add(this.tabSim);
            this.tabs.Controls.Add(this.tabBauds);
            this.tabs.Location = new System.Drawing.Point(20, 122);
            this.tabs.Name = "tabs";
            this.tabs.SelectedIndex = 0;
            this.tabs.Size = new System.Drawing.Size(460, 356);
            this.tabs.TabIndex = 5;
            // 
            // tabRawText
            // 
            this.tabRawText.Controls.Add(this.btnReplace);
            this.tabRawText.Controls.Add(this.btnPush);
            this.tabRawText.Controls.Add(this.txtRawText);
            this.tabRawText.Controls.Add(this.label3);
            this.tabRawText.Controls.Add(this.listSentMsgs);
            this.tabRawText.Location = new System.Drawing.Point(4, 22);
            this.tabRawText.Name = "tabRawText";
            this.tabRawText.Padding = new System.Windows.Forms.Padding(3);
            this.tabRawText.Size = new System.Drawing.Size(452, 330);
            this.tabRawText.TabIndex = 0;
            this.tabRawText.Text = "Raw Text";
            this.tabRawText.UseVisualStyleBackColor = true;
            // 
            // btnReplace
            // 
            this.btnReplace.Location = new System.Drawing.Point(373, 279);
            this.btnReplace.Name = "btnReplace";
            this.btnReplace.Size = new System.Drawing.Size(61, 23);
            this.btnReplace.TabIndex = 4;
            this.btnReplace.Text = "Replace";
            this.btnReplace.UseVisualStyleBackColor = true;
            // 
            // btnPush
            // 
            this.btnPush.Location = new System.Drawing.Point(306, 279);
            this.btnPush.Name = "btnPush";
            this.btnPush.Size = new System.Drawing.Size(61, 23);
            this.btnPush.TabIndex = 3;
            this.btnPush.Text = "Push";
            this.btnPush.UseVisualStyleBackColor = true;
            this.btnPush.Click += new System.EventHandler(this.btnPush_Click);
            // 
            // txtRawText
            // 
            this.txtRawText.Location = new System.Drawing.Point(20, 282);
            this.txtRawText.Name = "txtRawText";
            this.txtRawText.Size = new System.Drawing.Size(270, 20);
            this.txtRawText.TabIndex = 2;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(17, 12);
            this.label3.MaximumSize = new System.Drawing.Size(420, 217);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(417, 26);
            this.label3.TabIndex = 1;
            this.label3.Text = "Enter a message in the box at the bottom, then hit Push.  It will appear in the l" +
    "ist below, and on the LED matrix after the current cycle has completed.";
            // 
            // listSentMsgs
            // 
            this.listSentMsgs.FormattingEnabled = true;
            this.listSentMsgs.Location = new System.Drawing.Point(40, 48);
            this.listSentMsgs.Name = "listSentMsgs";
            this.listSentMsgs.Size = new System.Drawing.Size(366, 199);
            this.listSentMsgs.TabIndex = 0;
            // 
            // tabTwitter
            // 
            this.tabTwitter.Controls.Add(this.textBox2);
            this.tabTwitter.Controls.Add(this.button3);
            this.tabTwitter.Controls.Add(this.label5);
            this.tabTwitter.Controls.Add(this.label4);
            this.tabTwitter.Location = new System.Drawing.Point(4, 22);
            this.tabTwitter.Name = "tabTwitter";
            this.tabTwitter.Padding = new System.Windows.Forms.Padding(3);
            this.tabTwitter.Size = new System.Drawing.Size(452, 330);
            this.tabTwitter.TabIndex = 1;
            this.tabTwitter.Text = "Twitter Feed";
            this.tabTwitter.UseVisualStyleBackColor = true;
            // 
            // textBox2
            // 
            this.textBox2.Location = new System.Drawing.Point(90, 87);
            this.textBox2.Name = "textBox2";
            this.textBox2.Size = new System.Drawing.Size(245, 20);
            this.textBox2.TabIndex = 3;
            // 
            // button3
            // 
            this.button3.Location = new System.Drawing.Point(356, 85);
            this.button3.Name = "button3";
            this.button3.Size = new System.Drawing.Size(75, 23);
            this.button3.TabIndex = 2;
            this.button3.Text = "Go";
            this.button3.UseVisualStyleBackColor = true;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(18, 90);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(66, 13);
            this.label5.TabIndex = 1;
            this.label5.Text = "Twitter feed:";
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(18, 16);
            this.label4.MaximumSize = new System.Drawing.Size(420, 240);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(413, 39);
            this.label4.TabIndex = 0;
            this.label4.Text = resources.GetString("label4.Text");
            // 
            // tabAnim
            // 
            this.tabAnim.Controls.Add(this.btnChooseAVIPath);
            this.tabAnim.Controls.Add(this.btnChooseGIFPath);
            this.tabAnim.Controls.Add(this.btnChooseImgFolderPath);
            this.tabAnim.Controls.Add(this.txtAVIPath);
            this.tabAnim.Controls.Add(this.txtGIFPath);
            this.tabAnim.Controls.Add(this.txtImageFolder);
            this.tabAnim.Controls.Add(this.button1);
            this.tabAnim.Controls.Add(this.rbAVIPath);
            this.tabAnim.Controls.Add(this.rbGIFPath);
            this.tabAnim.Controls.Add(this.rbImageFolder);
            this.tabAnim.Location = new System.Drawing.Point(4, 22);
            this.tabAnim.Name = "tabAnim";
            this.tabAnim.Size = new System.Drawing.Size(452, 330);
            this.tabAnim.TabIndex = 4;
            this.tabAnim.Text = "Animation";
            this.tabAnim.UseVisualStyleBackColor = true;
            // 
            // btnChooseAVIPath
            // 
            this.btnChooseAVIPath.Location = new System.Drawing.Point(349, 106);
            this.btnChooseAVIPath.Name = "btnChooseAVIPath";
            this.btnChooseAVIPath.Size = new System.Drawing.Size(74, 23);
            this.btnChooseAVIPath.TabIndex = 9;
            this.btnChooseAVIPath.Text = "Choose...";
            this.btnChooseAVIPath.UseVisualStyleBackColor = true;
            // 
            // btnChooseGIFPath
            // 
            this.btnChooseGIFPath.Location = new System.Drawing.Point(349, 65);
            this.btnChooseGIFPath.Name = "btnChooseGIFPath";
            this.btnChooseGIFPath.Size = new System.Drawing.Size(74, 23);
            this.btnChooseGIFPath.TabIndex = 8;
            this.btnChooseGIFPath.Text = "Choose...";
            this.btnChooseGIFPath.UseVisualStyleBackColor = true;
            // 
            // btnChooseImgFolderPath
            // 
            this.btnChooseImgFolderPath.Location = new System.Drawing.Point(349, 26);
            this.btnChooseImgFolderPath.Name = "btnChooseImgFolderPath";
            this.btnChooseImgFolderPath.Size = new System.Drawing.Size(74, 23);
            this.btnChooseImgFolderPath.TabIndex = 7;
            this.btnChooseImgFolderPath.Text = "Choose...";
            this.btnChooseImgFolderPath.UseVisualStyleBackColor = true;
            this.btnChooseImgFolderPath.Click += new System.EventHandler(this.btnChooseImgFolderPath_Click);
            // 
            // txtAVIPath
            // 
            this.txtAVIPath.Enabled = false;
            this.txtAVIPath.Location = new System.Drawing.Point(113, 108);
            this.txtAVIPath.Name = "txtAVIPath";
            this.txtAVIPath.Size = new System.Drawing.Size(230, 20);
            this.txtAVIPath.TabIndex = 6;
            this.txtAVIPath.Text = "Coming soon";
            // 
            // txtGIFPath
            // 
            this.txtGIFPath.Enabled = false;
            this.txtGIFPath.Location = new System.Drawing.Point(113, 67);
            this.txtGIFPath.Name = "txtGIFPath";
            this.txtGIFPath.Size = new System.Drawing.Size(230, 20);
            this.txtGIFPath.TabIndex = 5;
            this.txtGIFPath.Text = "Coming soon";
            // 
            // txtImageFolder
            // 
            this.txtImageFolder.Location = new System.Drawing.Point(113, 28);
            this.txtImageFolder.Name = "txtImageFolder";
            this.txtImageFolder.Size = new System.Drawing.Size(230, 20);
            this.txtImageFolder.TabIndex = 4;
            this.txtImageFolder.TextChanged += new System.EventHandler(this.textBox1_TextChanged);
            // 
            // button1
            // 
            this.button1.Location = new System.Drawing.Point(164, 181);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(111, 31);
            this.button1.TabIndex = 3;
            this.button1.Text = "Send Animation";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // rbAVIPath
            // 
            this.rbAVIPath.AutoSize = true;
            this.rbAVIPath.Location = new System.Drawing.Point(18, 109);
            this.rbAVIPath.Name = "rbAVIPath";
            this.rbAVIPath.Size = new System.Drawing.Size(70, 17);
            this.rbAVIPath.TabIndex = 2;
            this.rbAVIPath.TabStop = true;
            this.rbAVIPath.Text = "AVI Path:";
            this.rbAVIPath.UseVisualStyleBackColor = true;
            // 
            // rbGIFPath
            // 
            this.rbGIFPath.AutoSize = true;
            this.rbGIFPath.Location = new System.Drawing.Point(18, 68);
            this.rbGIFPath.Name = "rbGIFPath";
            this.rbGIFPath.Size = new System.Drawing.Size(70, 17);
            this.rbGIFPath.TabIndex = 1;
            this.rbGIFPath.TabStop = true;
            this.rbGIFPath.Text = "GIF Path:";
            this.rbGIFPath.UseVisualStyleBackColor = true;
            // 
            // rbImageFolder
            // 
            this.rbImageFolder.AutoSize = true;
            this.rbImageFolder.Location = new System.Drawing.Point(18, 29);
            this.rbImageFolder.Name = "rbImageFolder";
            this.rbImageFolder.Size = new System.Drawing.Size(89, 17);
            this.rbImageFolder.TabIndex = 0;
            this.rbImageFolder.TabStop = true;
            this.rbImageFolder.Text = "Image Folder:";
            this.rbImageFolder.UseVisualStyleBackColor = true;
            // 
            // tabSim
            // 
            this.tabSim.Location = new System.Drawing.Point(4, 22);
            this.tabSim.Name = "tabSim";
            this.tabSim.Size = new System.Drawing.Size(452, 330);
            this.tabSim.TabIndex = 2;
            this.tabSim.Text = "Simulator";
            this.tabSim.UseVisualStyleBackColor = true;
            // 
            // tabBauds
            // 
            this.tabBauds.Controls.Add(this.txtMaxRefresh);
            this.tabBauds.Controls.Add(this.txtNumPanels);
            this.tabBauds.Controls.Add(this.lblBaudTarget);
            this.tabBauds.Controls.Add(this.lblMaxRefresh);
            this.tabBauds.Controls.Add(this.lblTotPanels);
            this.tabBauds.Controls.Add(this.lblBaudRateHelp);
            this.tabBauds.Location = new System.Drawing.Point(4, 22);
            this.tabBauds.Name = "tabBauds";
            this.tabBauds.Size = new System.Drawing.Size(452, 330);
            this.tabBauds.TabIndex = 3;
            this.tabBauds.Text = "Baud Rate";
            this.tabBauds.UseVisualStyleBackColor = true;
            // 
            // txtMaxRefresh
            // 
            this.txtMaxRefresh.Location = new System.Drawing.Point(222, 91);
            this.txtMaxRefresh.Mask = "000000";
            this.txtMaxRefresh.Name = "txtMaxRefresh";
            this.txtMaxRefresh.Size = new System.Drawing.Size(50, 20);
            this.txtMaxRefresh.TabIndex = 7;
            this.txtMaxRefresh.TextChanged += new System.EventHandler(this.BaudCalculator_TextChanged);
            // 
            // txtNumPanels
            // 
            this.txtNumPanels.Location = new System.Drawing.Point(222, 61);
            this.txtNumPanels.Mask = "00";
            this.txtNumPanels.Name = "txtNumPanels";
            this.txtNumPanels.Size = new System.Drawing.Size(50, 20);
            this.txtNumPanels.TabIndex = 6;
            this.txtNumPanels.ValidatingType = typeof(int);
            this.txtNumPanels.TextChanged += new System.EventHandler(this.BaudCalculator_TextChanged);
            // 
            // lblBaudTarget
            // 
            this.lblBaudTarget.AutoSize = true;
            this.lblBaudTarget.Location = new System.Drawing.Point(175, 130);
            this.lblBaudTarget.Name = "lblBaudTarget";
            this.lblBaudTarget.Size = new System.Drawing.Size(41, 13);
            this.lblBaudTarget.TabIndex = 5;
            this.lblBaudTarget.Text = "Target:";
            // 
            // lblMaxRefresh
            // 
            this.lblMaxRefresh.AutoSize = true;
            this.lblMaxRefresh.Location = new System.Drawing.Point(106, 94);
            this.lblMaxRefresh.Name = "lblMaxRefresh";
            this.lblMaxRefresh.Size = new System.Drawing.Size(110, 13);
            this.lblMaxRefresh.TabIndex = 3;
            this.lblMaxRefresh.Text = "Maximum refresh rate:";
            // 
            // lblTotPanels
            // 
            this.lblTotPanels.AutoSize = true;
            this.lblTotPanels.Location = new System.Drawing.Point(62, 64);
            this.lblTotPanels.Name = "lblTotPanels";
            this.lblTotPanels.Size = new System.Drawing.Size(154, 13);
            this.lblTotPanels.TabIndex = 1;
            this.lblTotPanels.Text = "Total # of panels in your matrix:";
            // 
            // lblBaudRateHelp
            // 
            this.lblBaudRateHelp.AutoSize = true;
            this.lblBaudRateHelp.Location = new System.Drawing.Point(21, 20);
            this.lblBaudRateHelp.MaximumSize = new System.Drawing.Size(420, 240);
            this.lblBaudRateHelp.Name = "lblBaudRateHelp";
            this.lblBaudRateHelp.Size = new System.Drawing.Size(402, 26);
            this.lblBaudRateHelp.TabIndex = 0;
            this.lblBaudRateHelp.Text = "For the scroll to look good, the serial port must run at a baud rate such that th" +
    "e LED matrix can refresh at least 25-30 times per second.";
            // 
            // btnCOM1Connect
            // 
            this.btnCOM1Connect.BackColor = System.Drawing.Color.GreenYellow;
            this.btnCOM1Connect.Location = new System.Drawing.Point(395, 53);
            this.btnCOM1Connect.Name = "btnCOM1Connect";
            this.btnCOM1Connect.Size = new System.Drawing.Size(81, 22);
            this.btnCOM1Connect.TabIndex = 6;
            this.btnCOM1Connect.Tag = "1";
            this.btnCOM1Connect.Text = "Connect";
            this.btnCOM1Connect.UseVisualStyleBackColor = false;
            this.btnCOM1Connect.Click += new System.EventHandler(this.btnCOMConnect_Click);
            // 
            // btnCOM2Connect
            // 
            this.btnCOM2Connect.BackColor = System.Drawing.Color.GreenYellow;
            this.btnCOM2Connect.Enabled = false;
            this.btnCOM2Connect.Location = new System.Drawing.Point(395, 76);
            this.btnCOM2Connect.Name = "btnCOM2Connect";
            this.btnCOM2Connect.Size = new System.Drawing.Size(81, 22);
            this.btnCOM2Connect.TabIndex = 7;
            this.btnCOM2Connect.Tag = "2";
            this.btnCOM2Connect.Text = "Connect";
            this.btnCOM2Connect.UseVisualStyleBackColor = false;
            this.btnCOM2Connect.Click += new System.EventHandler(this.btnCOMConnect_Click);
            // 
            // menuStrip1
            // 
            this.menuStrip1.Items.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.helpToolStripMenuItem});
            this.menuStrip1.Location = new System.Drawing.Point(0, 0);
            this.menuStrip1.Name = "menuStrip1";
            this.menuStrip1.Size = new System.Drawing.Size(503, 24);
            this.menuStrip1.TabIndex = 8;
            this.menuStrip1.Text = "menuStrip1";
            // 
            // helpToolStripMenuItem
            // 
            this.helpToolStripMenuItem.DropDownItems.AddRange(new System.Windows.Forms.ToolStripItem[] {
            this.aboutToolStripMenuItem});
            this.helpToolStripMenuItem.Name = "helpToolStripMenuItem";
            this.helpToolStripMenuItem.Size = new System.Drawing.Size(44, 20);
            this.helpToolStripMenuItem.Text = "Help";
            // 
            // aboutToolStripMenuItem
            // 
            this.aboutToolStripMenuItem.Name = "aboutToolStripMenuItem";
            this.aboutToolStripMenuItem.Size = new System.Drawing.Size(116, 22);
            this.aboutToolStripMenuItem.Text = "About...";
            this.aboutToolStripMenuItem.Click += new System.EventHandler(this.aboutToolStripMenuItem_Click);
            // 
            // lblSpeed
            // 
            this.lblSpeed.AutoSize = true;
            this.lblSpeed.Location = new System.Drawing.Point(173, 35);
            this.lblSpeed.Name = "lblSpeed";
            this.lblSpeed.Size = new System.Drawing.Size(67, 13);
            this.lblSpeed.TabIndex = 9;
            this.lblSpeed.Text = "Speed (bps):";
            // 
            // choiceSpeed
            // 
            this.choiceSpeed.AutoCompleteMode = System.Windows.Forms.AutoCompleteMode.SuggestAppend;
            this.choiceSpeed.FormattingEnabled = true;
            this.choiceSpeed.Items.AddRange(new object[] {
            "9600",
            "19200",
            "38400",
            "57600",
            "115200",
            "230400"});
            this.choiceSpeed.Location = new System.Drawing.Point(246, 32);
            this.choiceSpeed.Name = "choiceSpeed";
            this.choiceSpeed.Size = new System.Drawing.Size(121, 21);
            this.choiceSpeed.TabIndex = 10;
            this.choiceSpeed.Text = "9600";
            // 
            // folderBrowser
            // 
            this.folderBrowser.Description = "Select the folder that contains a sequence of bitmap files (*.BMP) consisting of " +
    "the animation you wish to show.";
            this.folderBrowser.ShowNewFolderButton = false;
            // 
            // numRows
            // 
            this.numRows.Location = new System.Drawing.Point(8, 24);
            this.numRows.Maximum = new decimal(new int[] {
            128,
            0,
            0,
            0});
            this.numRows.Minimum = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.numRows.Name = "numRows";
            this.numRows.Size = new System.Drawing.Size(46, 20);
            this.numRows.TabIndex = 0;
            this.numRows.Value = new decimal(new int[] {
            1,
            0,
            0,
            0});
            this.numRows.ValueChanged += new System.EventHandler(this.numRows_ValueChanged);
            // 
            // chkMultiplexed
            // 
            this.chkMultiplexed.AutoSize = true;
            this.chkMultiplexed.Checked = true;
            this.chkMultiplexed.CheckState = System.Windows.Forms.CheckState.Checked;
            this.chkMultiplexed.Location = new System.Drawing.Point(8, 55);
            this.chkMultiplexed.Name = "chkMultiplexed";
            this.chkMultiplexed.Size = new System.Drawing.Size(79, 17);
            this.chkMultiplexed.TabIndex = 1;
            this.chkMultiplexed.Text = "Multiplexed";
            this.chkMultiplexed.UseVisualStyleBackColor = true;
            this.chkMultiplexed.CheckedChanged += new System.EventHandler(this.chkMultiplexed_CheckedChanged);
            // 
            // Form1
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 13F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(503, 502);
            this.Controls.Add(this.choiceSpeed);
            this.Controls.Add(this.lblSpeed);
            this.Controls.Add(this.btnCOM2Connect);
            this.Controls.Add(this.btnCOM1Connect);
            this.Controls.Add(this.tabs);
            this.Controls.Add(this.choiceCOM2);
            this.Controls.Add(this.choiceCOM1);
            this.Controls.Add(this.lblCOM2);
            this.Controls.Add(this.groupRow);
            this.Controls.Add(this.lblCOM1);
            this.Controls.Add(this.menuStrip1);
            this.MainMenuStrip = this.menuStrip1;
            this.Name = "Form1";
            this.Text = "LEDgoes PC Interface";
            this.Load += new System.EventHandler(this.Form1_Load);
            this.groupRow.ResumeLayout(false);
            this.groupRow.PerformLayout();
            this.tabs.ResumeLayout(false);
            this.tabRawText.ResumeLayout(false);
            this.tabRawText.PerformLayout();
            this.tabTwitter.ResumeLayout(false);
            this.tabTwitter.PerformLayout();
            this.tabAnim.ResumeLayout(false);
            this.tabAnim.PerformLayout();
            this.tabBauds.ResumeLayout(false);
            this.tabBauds.PerformLayout();
            this.menuStrip1.ResumeLayout(false);
            this.menuStrip1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.numRows)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.Label lblCOM1;
        private System.Windows.Forms.GroupBox groupRow;
        private System.Windows.Forms.Label lblCOM2;
        private System.Windows.Forms.ComboBox choiceCOM1;
        private System.Windows.Forms.ComboBox choiceCOM2;
        private System.Windows.Forms.TabControl tabs;
        private System.Windows.Forms.TabPage tabRawText;
        private System.Windows.Forms.Button btnReplace;
        private System.Windows.Forms.Button btnPush;
        private System.Windows.Forms.TextBox txtRawText;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.ListBox listSentMsgs;
        private System.Windows.Forms.TabPage tabTwitter;
        private System.Windows.Forms.TextBox textBox2;
        private System.Windows.Forms.Button button3;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TabPage tabSim;
        private System.Windows.Forms.Button btnCOM1Connect;
        private System.Windows.Forms.Button btnCOM2Connect;
        private System.Windows.Forms.MenuStrip menuStrip1;
        private System.Windows.Forms.ToolStripMenuItem helpToolStripMenuItem;
        private System.Windows.Forms.ToolStripMenuItem aboutToolStripMenuItem;
        private System.Windows.Forms.TabPage tabBauds;
        private System.Windows.Forms.Label lblBaudTarget;
        private System.Windows.Forms.Label lblMaxRefresh;
        private System.Windows.Forms.Label lblTotPanels;
        private System.Windows.Forms.Label lblBaudRateHelp;
        private System.Windows.Forms.MaskedTextBox txtMaxRefresh;
        private System.Windows.Forms.MaskedTextBox txtNumPanels;
        private System.Windows.Forms.Label lblSpeed;
        private System.Windows.Forms.ComboBox choiceSpeed;
        private System.Windows.Forms.TabPage tabAnim;
        private System.Windows.Forms.Button btnChooseAVIPath;
        private System.Windows.Forms.Button btnChooseGIFPath;
        private System.Windows.Forms.Button btnChooseImgFolderPath;
        private System.Windows.Forms.TextBox txtAVIPath;
        private System.Windows.Forms.TextBox txtGIFPath;
        private System.Windows.Forms.TextBox txtImageFolder;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.RadioButton rbAVIPath;
        private System.Windows.Forms.RadioButton rbGIFPath;
        private System.Windows.Forms.RadioButton rbImageFolder;
        private System.Windows.Forms.FolderBrowserDialog folderBrowser;
        private System.Windows.Forms.CheckBox chkMultiplexed;
        private System.Windows.Forms.NumericUpDown numRows;
    }
}

