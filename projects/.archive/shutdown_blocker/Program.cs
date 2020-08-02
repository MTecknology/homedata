using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows.Forms;

namespace EMAR_Reset {
    static class Program {
        /// <summary>
        /// The main entry point for the application.
        /// </summary>
        [STAThread]
        static void Main(string[] args) {
            // Check argument passed
            if (args.Length != 1) {
                Console.WriteLine("Invalid arguments passed. Need an interface name.");
                Environment.Exit(1);
            }

            // Set interface name from argument
            Globals.ifName = args[0];
            //Globals.ifName = "Wireless Network Connection"; // for testing only

            // Register and load application
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new frmMain());
        }
    }
}
