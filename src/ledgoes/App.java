/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package ledgoes;

import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.util.Enumeration;
import java.util.HashMap;
import gnu.io.CommPort;
import gnu.io.CommPortIdentifier;
import gnu.io.NoSuchPortException;
import gnu.io.PortInUseException;
import gnu.io.SerialPort;
import gnu.io.UnsupportedCommOperationException;
import java.awt.Color;
import javax.swing.JOptionPane;

/**
 *
 * @author Stephen
 */
public class App {
    
    public static OutputStream os1, os2;
    public static boolean multiplexed;
    public static String[] messages;
    
    private static CommPortIdentifier thePortID;
    private static CommPort thePort;
    private static HashMap map;
    private static DirectDrive directDrive;
    
    /**
     * VERY IMPORTANT! If using Windows, install the RXTX JAR & supporting DLLs
     */
    public static void populate() {
        Enumeration pList = CommPortIdentifier.getPortIdentifiers();
        map = new HashMap();

        // Process the list, putting serial and parallel into ComboBoxes
        while (pList.hasMoreElements()) {
            CommPortIdentifier cpi = (CommPortIdentifier)pList.nextElement();
            // System.out.println("Port " + cpi.getName());
            if (cpi.getPortType() == CommPortIdentifier.PORT_SERIAL) {
                map.put(cpi.getName(), cpi);
                LEDgoesInterface.COMChoice1.addItem(cpi.getName());
                LEDgoesInterface.COMChoice2.addItem(cpi.getName());
            }
        }
    }
    
    public static void SerialPortOpen(java.awt.event.MouseEvent evt) {

        javax.swing.JButton btn = (javax.swing.JButton) evt.getComponent();

        // Get the CommPortIdentifier.
        if (btn.getName().equals("1")) {
            thePortID = (CommPortIdentifier) map.get(LEDgoesInterface.COMChoice1.getSelectedItem().toString());
        } else {
            thePortID = (CommPortIdentifier) map.get(LEDgoesInterface.COMChoice2.getSelectedItem().toString());
        }
        
        // Now actually open the port.
        // This form of openPort takes an Application Name and a timeout.
        //
        try {
            System.out.println("Trying to open " + thePortID.getName() + "...");
        } catch (Exception e) {
            infoBox("Select a valid, active serial port.", "Error");
            return;
        }

        SerialPort myPort;
        try {
            thePort = thePortID.open("LEDgoes", 5 * 1000);
            myPort = (SerialPort) thePort;
        } catch (PortInUseException e) {
            return;
        }

        // set up the serial port
        try {
            myPort.setSerialPortParams(9600, SerialPort.DATABITS_8,
                SerialPort.STOPBITS_1, SerialPort.PARITY_NONE);
        } catch (UnsupportedCommOperationException e) {
            return;
        }
            
        // Get the output stream so we can write to the board
        OutputStream os;
        try {
            if (btn.getName().equals("1")) {
                os1 = new PrintStream(thePort.getOutputStream(), true);
                os = os1;
            } else {
                os2 = new PrintStream(thePort.getOutputStream(), true);
                os = os2;
            }
        } catch (IOException e) {
            return;
        }
        
        try {
            os.write(" ".getBytes());
            os.write(((byte)0x3));
        } catch (Exception e) {
            infoBox("Your serial port failed to initialize", "Error");
            return;
        }
        
        // Change the button state to Ready to Connect
        btn.setBackground(Color.red);
        btn.setText("Disconnect");
        // If we're only pushing to one row, or if the other serial port is active, let's start output now
        if (readyToSend()) {
            serialWelcome();
            // Also disable the other settings-related GUI items until the matrix is disconnected
            LEDgoesInterface.rowCount.setEnabled(false);
            LEDgoesInterface.isMultiplexed.setEnabled(false);
        }
    }
    
    public static void serialWelcome() {
        if (directDrive == null) {
            App.messages[0] = " :: AWAITING MESSAGES  ";
            directDrive = new DirectDrive();
            directDrive.run();
        } else {
            if (directDrive.isInterrupted()) {
                // directDrive.
            }
        }
    }
    
    public static void SerialPortClose(java.awt.event.MouseEvent evt) { 

        try {              // Kill the output thread
            //outputThread.Abort();
        } catch (Exception e) {
            // no one cares
        }
        try {              // Kill the animation thread
            //animationThread.Abort();
        } catch (Exception e) {
            // no one cares
        }

        OutputStream os;
        javax.swing.JButton btn = (javax.swing.JButton) evt.getComponent();
        
        try {
            if (btn.getName().equals("1")) {
                os1.close();
                os1 = null;
            } else {
                os2.close();
                os2 = null;
            }
        } catch (IOException e) {
            return;
        }

        // Change the button state to Ready to Connect
        btn.setBackground(Color.GREEN); // = Color.DarkSeaGreen;
        btn.setText("Connect");
        // If both serial ports are now disconnected, re-enable settings
        if (os1 == null || os2 == null) {
            LEDgoesInterface.rowCount.setEnabled(true);
            LEDgoesInterface.isMultiplexed.setEnabled(true);
        }
    }
    
    public static void infoBox(String infoMessage, String infoTitle)
    {
        JOptionPane.showMessageDialog(null, infoMessage, infoTitle, JOptionPane.INFORMATION_MESSAGE);
    }
    
    private static boolean readyToSend() {
        javax.swing.JButton a = LEDgoesInterface.btnCOM1Connect;
        javax.swing.JButton b = LEDgoesInterface.btnCOM2Connect;
        javax.swing.JCheckBox c = LEDgoesInterface.isMultiplexed;
        if ((c.isSelected() && a.getText().equals("Disconnect")) ||
            (!c.isSelected() && a.getText().equals("Disconnect") && b.getText().equals("Disconnect")))
            return true;
        return false;
    }

}
