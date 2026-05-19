package main

import (
	"bytes"
	"crypto/md5"
	"encoding/hex"
	"flag"
	"log"
	"net"
	"net/smtp"
	"os"
	"regexp"
	"strings"
	"sync"
	"time"

	// https://godoc.org/github.com/garyburd/redigo/redis
	"github.com/garyburd/redigo/redis"
)

// Settings
var (
	redisPool      *redis.Pool
	redisServer    = flag.String("redisServer", "127.0.0.1:6379", "Location of redis server")
	redisPassword  = flag.String("redisPassword", "", "Password used to connect to redis server")
	socketLocation = flag.String("socketLocation", "/tmp/inalert.sock", "Socket location to listen for messages")
	debugEnabled   = flag.Bool("debugEnabled", true, "Print extra debugging messages")
	debugMessage   = flag.Bool("debugMessage", false, "Prints the entire message currently being processed")
	shutdownSignal = flag.String("shutdownSignal", `STOPNOW`, "Message to put on socket to shut down daemon")
	fromAddress    = flag.String("fromAddress", "alerts@resistance.report", "Address that messages will be sent from")
	throttleTime   = flag.Int("throttleTime", 600, "Number of seconds before sending a user/portal combination another message.")
)

// Portal
type Portal struct {
	Name      string
	Latitude  string
	Longitude string
	NameHash  string
	GeoHash   string
}

/**
 * Begin listening on a socket and processing messages
 * until the shutdown signal has been received
 */
func main() {
	flag.Parse()
	rStop := regexp.MustCompile(*shutdownSignal)

	// Open unix socket to listen on
	listener, err := net.ListenUnix("unix", &net.UnixAddr{Name: *socketLocation, Net: "unix"})
	if err != nil {
		log.Fatal("listen error:", err)
	}
	defer os.Remove(*socketLocation)

	// Create connection to redis server
	redisPool = new_redis_pool(*redisServer, *redisPassword)
	redi, err := redisPool.Dial()
	if err != nil {
		log.Fatal("redis connect error:", err)
	}
	defer redi.Close()

	// Read all messages coming in on socket
	for {
		conn, err := listener.AcceptUnix()
		if err != nil {
			log.Fatal("accept error:", err)
		}

		// Read message in chunks from buffer until EOF
		buf := make([]byte, 512)
		msg := ""
		for {
			nr, err := conn.Read(buf)
			if err != nil {
				break
			}
			msg += string(buf[0:nr])
		}

		// Check if message was a shutdown signal
		if rStop.MatchString(msg) {
			log.Println("shutting down")
			break
		}

		// Process messages
		go process_message(msg, redi)
	}
}

/**
 * Create a redis connection pool to handle threads
 * Usage: redisPool = new_redis_pool(*redisServer, *redisPassword)
 */
func new_redis_pool(server, password string) *redis.Pool {
	return &redis.Pool{
		MaxIdle:     3,
		IdleTimeout: 240 * time.Second,
		Dial: func() (redis.Conn, error) {
			conn, err := redis.Dial("tcp", server)
			if err != nil {
				return nil, err
			}
			if password != "" {
				if _, err := conn.Do("AUTH", password); err != nil {
					conn.Close()
					return nil, err
				}
			}
			return conn, err
		},
		TestOnBorrow: func(conn redis.Conn, t time.Time) error {
			_, err := conn.Do("PING")
			return err
		},
	}
}

/**
 * Read the contents of an email message, check message contents, and
 * notify user after checking user throttle.
 */
func process_message(data string, redi redis.Conn) {
	// Find portal name, location, hash
	portals := get_portal(data)
	//TODO
	portal := portals[0]
	//TODO for ? {
	if portal.Name == "" {
		log.Println("parse error: no data found")
		return
	}

	// Get portal contacts from redis (this is blocking)
	ret, err := redis.String(redi.Do("GET", "portal:"+portal.GeoHash))
	if err != nil {
		// no contacts to notify
		if *debugEnabled {
			log.Println("no contacts for portal")
		}
		return
	}

	// Create wait group for goroutines
	var wg sync.WaitGroup

	// Send Alerts
	for _, contact := range strings.Split(ret, ";") {
		if user_throttled(get_hash(contact), portal.GeoHash, redi) {
			// user/portal throttled
			if *debugEnabled {
				log.Println("send alert to", contact, ": NOT DONE :: throttled")
			}
			continue
		}
		// Increment counter
		wg.Add(1)
		go func(c string, portal Portal) {
			defer wg.Done()
			send_alert(c, portal.Name)
			if *debugEnabled {
				log.Println("send alert to", contact, ": done")
			}
		}(contact, portal)
	}

	//TODO }

	// Wait for processes to exit
	wg.Wait()
}

/**
 * Read message contents and return a list of portals
 */
func get_portal(data string) []Portal {
	// Display message contents on console
	if *debugMessage {
		log.Println("regex blob:", data)
	}

	portals := []Portal{}
	blob := strings.Replace(strings.Replace(string(data), "=\n", "", -1), "=3D", "=", -1)
	rMsg := regexp.MustCompile(`>(?P<name>[^<]+)<(?:[^<]+<){2}a.+?href.+?pll=(?P<latitude>[0-9\.\-]+),(?P<longitude>[0-9\.\-]+)`)
	match := rMsg.FindAllStringSubmatch(blob, -1)
	if len(match) == 0 {
		// no match found
		if *debugEnabled {
			log.Println("regex matching failed")
		}
		//return Portal{"", "", "", "", ""}
		return nil
	}

	for _, tmp := range match {
		// Create map of regex captures
		m := map[string]string{}
		n1 := rMsg.SubexpNames()
		for i, n := range tmp {
			m[n1[i]] = n
		}

		// Find portal hash
		m["geohash"] = get_hash(m["longitude"] + "X" + m["latitude"])
		m["namehash"] = get_hash(m["name"])

		if *debugEnabled {
			log.Println("Portal :: ", m["name"], " : ", m["longitude"], m["latitude"], " : ", m["hash"])
		}

		portals = append(portals, Portal{
			Name:      m["name"],
			Longitude: m["longitude"],
			Latitude:  m["latitude"],
			GeoHash:   m["geohash"],
			NameHash:  m["namehash"]})

	}

	return portals
}

/**
 * Checks to see whether a user/portal combination has been alerted in the last
 * *throttleTime seconds. Returns true if a throttle still exists or false if
 * the user should be messaged again.
 */
func user_throttled(user, portal string, redi redis.Conn) bool {
	key := "throttle:"+user+":"+portal
	ret, err := redis.String(redi.Do("GETSET", key, "1"))
	_, e := redis.Int(redi.Do("EXPIRE", key, *throttleTime))
	if e != nil {
		log.Println("Unable to set throttle expiration for:", key, " :: ", e)
	}
	if err != nil {
		// no throttle lock found
		return false
	}
	if ret == "1" {
		// throttle lock found
		return true
	}
	log.Println("unknown lock error")
	// fail open
	return false
}

/**
 * Send an alert to a user via email
 */
func send_alert(contact, portal string) {
	//TODO: Leave until ready to send mass messages
	return

	if *debugEnabled {
		log.Println("MESSAGE TO:", contact, "PORTAL:", portal)
	}

	s, err := smtp.Dial("127.0.0.1:25")
	if err != nil {
		log.Println("smtp connect error:", err)
		return
	}
	defer s.Close()

	s.Mail(*fromAddress)
	s.Rcpt(contact)

	wc, err := s.Data()
	if err != nil {
		log.Println("smtp data error:", err)
		return
	}
	defer wc.Close()

	buf := bytes.NewBufferString("PORTAL ALERT: " + portal)
	if _, err = buf.WriteTo(wc); err != nil {
		log.Println("smtp send error:", err)
		return
	}
}

/**
 * Returns a string representation of an md5sum hash
 */
func get_hash(text string) string {
	hash := md5.Sum([]byte(text))
	return hex.EncodeToString(hash[:])
}
