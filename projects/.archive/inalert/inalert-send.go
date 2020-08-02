package main

import (
       "io/ioutil"
       "log"
       "net"
       "os"
)

func main() {
       // Open socket with server
       conn, err := net.Dial("unix", "/tmp/inalert.sock")
       if err != nil {
	      log.Fatal("connect error:", err)
       }
       defer conn.Close()

       // Read stdin
       stdin, err := ioutil.ReadAll(os.Stdin)
       if err != nil {
	      log.Fatal("read error:", err)
       }

       // Send message to socket
       _, err = conn.Write([]byte(stdin))
       if err != nil {
	      log.Fatal("write error:", err)
       }
}
