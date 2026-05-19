using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Management;
using System.Net.NetworkInformation;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using System.Windows.Forms;

namespace EMAR_Reset {
    public partial class frmMain : Form {
        public frmMain() {
            /* Initialize main form */
            InitializeComponent();
        }

        /* Register session ending block */
        [DllImport("user32.dll")]
        public extern static bool ShutdownBlockReasonCreate(IntPtr hWnd, [MarshalAs(UnmanagedType.LPWStr)] string pwszReason);

        /* Register session ending unblock */
        [DllImport("user32.dll")]
        public extern static bool ShutdownBlockReasonDestroy(IntPtr hWnd);

        private void frmMain_Load(object sender, EventArgs e) {
            /* On form load, block session ending */
            block_shutdown("!!! WARNING !!!   The EMAR Backup Access system is still running! Close before logging out!   !!! WARNING !!!");
            Globals.ifMAC = get_mac(Globals.ifName);
        }

        private void btnExit_Click(object sender, EventArgs e) {
            /* Reset networking, unblock session ending, exit */
            reset_network();
            reset_shutdown();
            Application.Exit();
        }

        protected override void WndProc(ref Message aMessage) {
            /* Handle Windows Process messages */
            const int WM_QUERYENDSESSION = 0x0011;
            const int WM_ENDSESSION = 0x0016;

            if (Globals.isBlocked && (aMessage.Msg == WM_QUERYENDSESSION || aMessage.Msg == WM_ENDSESSION)) {
                if (aMessage.Msg == WM_QUERYENDSESSION) {
                    // If Windows is trying to end, reset the networking.
                    //reset_network(); // This would be great, but the session is already ending so we can't load DLL's. :(
                    reset_network_alt();
                    reset_shutdown();
                    Application.Exit();
                }
                return;
            }

            base.WndProc(ref aMessage);
        }

        private void block_shutdown(string strMessage) {
            /* Process a shutdown block request */
            try {
                //strMessage == Message to display in shutdown/logoff box
                if (ShutdownBlockReasonCreate(this.Handle, strMessage)) {
                    Globals.isBlocked = true;
                    Console.WriteLine("++ StopShutdown successful");
                }
                else {
                    Console.WriteLine("++ StopShutdown failed");
                }
            }
            catch (Exception ext) {
                MessageBox.Show("++ StopShutdown Error:    " + ext.Message + " " + ext.StackTrace);
            }
        }

        private void reset_shutdown() {
            /* Process a shutdown block release request */
            try {
                if (ShutdownBlockReasonDestroy(this.Handle)) {
                    Globals.isBlocked = false;
                    Console.WriteLine("++ ResetShutdown successful");
                }
                else {
                    Console.WriteLine("++ ResetShutdown failed");
                }
            }
            catch (Exception ext) {
                MessageBox.Show("++ ResetShutdown Error:    " + ext.Message + " " + ext.StackTrace);
            }
        }

        private void reset_network() {
            /* Set networking back to DHCP */

            // Create process resource
            Process p = new Process();
            p.StartInfo.WindowStyle = ProcessWindowStyle.Hidden;
            p.StartInfo.UseShellExecute = false;

            // Reset DNS
            p.StartInfo.FileName = "netsh.exe";
            p.StartInfo.Arguments = "interface ip set dns \"" + Globals.ifName + "\" dhcp";
            p.Start();

            // Reset IP Address
            p.StartInfo.FileName = "netsh.exe";
            p.StartInfo.Arguments = "interface ip set address \"" + Globals.ifName + "\" dhcp";
            p.Start();

            // Renew IP Address
            p.StartInfo.FileName = "ipconfig";
            p.StartInfo.Arguments = "/renew";
            p.Start();
        }

        public void reset_network_alt() {
            /* Set networking back to DHCP -- Alternative method */
            /* This method is less reliable and slower but doesn't require loading DLL's. */

            ManagementClass net_ac = new ManagementClass("Win32_NetworkAdapterConfiguration");
            ManagementObjectCollection nac_oc = net_ac.GetInstances();

            try {
                foreach (ManagementObject net_if in nac_oc) {
                    if ((string)net_if.GetPropertyValue("MACAddress") == Globals.ifMAC) {
                        ManagementBaseObject newDNS = net_if.GetMethodParameters("SetDNSServerSearchOrder");
                        newDNS["DNSServerSearchOrder"] = null;
                        ManagementBaseObject enableDHCP = net_if.InvokeMethod("EnableDHCP", null, null);
                        ManagementBaseObject setDNS = net_if.InvokeMethod("SetDNSServerSearchOrder", newDNS, null);
                        //Save all Gateways into an array
                        string[] gateways = (string[])net_if["DefaultIPGateway"];

                        ManagementBaseObject newIP = net_if.GetMethodParameters("EnableStatic");
                        ManagementBaseObject newGate = net_if.GetMethodParameters("SetGateways");

                        //Set last value of the array(always the Gateway received by DHCP) as the default Gateway
                        newGate["DefaultIPGateway"] = new string[] { gateways[gateways.Length - 1] };
                        newGate["GatewayCostMetric"] = new int[] { 1 };

                        // Reset Interface
                        net_if.InvokeMethod("ReleaseDhcpLease", null);
                        Thread.Sleep(1000);
                        net_if.InvokeMethod("RenewDhcpLease", null);
                    }
                }
            }
            catch {
                MessageBox.Show("Interface appears to be disabled and can not be modified! CONTACT CFS");
            }
        }

        public string get_mac(string ifNAME) {
            // Get MAC address for interface
            foreach (NetworkInterface nic in NetworkInterface.GetAllNetworkInterfaces()) {
                if (nic.Name == Globals.ifName) {
                    string mac = nic.GetPhysicalAddress().ToString();
                    return mac.Substring(0, 2) + ":" + mac.Substring(2, 2) + ":" + mac.Substring(4, 2) + ":" +
                         mac.Substring(6, 2) + ":" + mac.Substring(8, 2) + ":" + mac.Substring(10, 2);
                }
            }
            return "ERROR: No interface found!";
        }
    }
}

public static class Globals {
    /* Generic globals registration system */
    static string _ifName;
    static string _ifMAC;
    static bool _isBlocked;
    public static string ifName {
        get { return _ifName; }
        set { _ifName = value; }
    }
    public static string ifMAC {
        get { return _ifMAC; }
        set { _ifMAC = value; }
    }
    public static bool isBlocked {
        get { return _isBlocked; }
        set { _isBlocked = value; }
    }
}
