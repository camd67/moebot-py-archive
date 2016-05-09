package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strconv"
	"strings"
	"syscall"
	"time"

	"github.com/Nick-Anderssohn/topanime/utils"
	"github.com/bwmarrin/discordgo"
)

var (
	config = make(map[string]string)
)

func init() {
	parseConfig()
}

func main() {
	if config["DEBUG"] == "false" {
		f, err := os.OpenFile(config["LOG"], os.O_RDWR|os.O_CREATE|os.O_APPEND, 0666)
		if err != nil {
			log.Fatalf("error opening file: %v", err)
		}
		defer f.Close()
		log.SetOutput(f)
	}

	discord, err := discordgo.New(config["DISCORD_TOKEN"])
	if err != nil {
		log.Fatal(err)
	}
	// Get the account information.
	u, err := discord.User("@me")
	if err != nil {
		log.Fatal(err)
	}

	// Store the account ID for later use.
	config["BOT_ID"] = u.ID

	discord.AddHandler(messageCreate)
	discord.AddHandler(ready)

	err = discord.Open()
	if err != nil {
		fmt.Println(err)
	}

	log.Println("Moebot is up and running...")
	handleExit()
}

func ready(s *discordgo.Session, event *discordgo.Ready) {
	// set "Playing " to
	s.UpdateStatus(0, "Moe")
}
func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	log.Printf("%20s %10s %10s > %s", m.ChannelID, time.Now().Format(time.Stamp), m.Author.Username, m.Content)
	if m.Author.ID != config["BOT_ID"] {
		parseMessage(s, m)
	}
}

func parseMessage(session *discordgo.Session, message *discordgo.MessageCreate) {
	//TODO: Setup message handling system prefixed with moe
	content := strings.ToLower(message.Content)
	if strings.HasPrefix(content, "hi moebot") || strings.HasPrefix(content, "hello moebot") {
		session.ChannelMessageSend(message.ChannelID, "Hello "+message.Author.Username+"!")
	} else if strings.HasPrefix(content, "moebot what's moe") || strings.HasPrefix(content, "moebot what is moe") {
		session.ChannelMessageSend(message.ChannelID, "Check this out: https://vimeo.com/70285271")
	} else if strings.HasPrefix(content, "moebot top") || strings.HasPrefix(content, "moe top") {
		session.ChannelMessageSend(message.ChannelID, topAnimeMessageHandler(content))
	} else if strings.HasPrefix(content, "moe random") {
		//session.ChannelMessageSend(message.ChannelID, randomMoe())
		//randomMoe()
	}
}

func randomMoe() string {
	// Need to login first!
	response, err := http.Get("http://reddit.com/r/awwnime/hot")
	if err != nil {
		log.Println("!! ERROR !! couldn't connect to reddit/awwnime")
	}
	defer response.Body.Close()
	body, err := ioutil.ReadAll(response.Body)
	if err != nil {
		log.Println("!! ERROR !! couldn't read response body in radnomMoe")
	}
	return string(body)
}

func topAnimeMessageHandler(message string) string {
	tokens := strings.Split(message, " ")
	if 2 < len(tokens) {
		numAnime, err := strconv.Atoi(tokens[2]) //the third token should be the number of anime to show
		if err != nil {
			return "Could not parse int"
		}
		return "The top " + strconv.Itoa(numAnime) + " according to myanimelist.net are:\n" + topanime.GetTopAnime(numAnime)
	}
	return "Bad command"
}

func handleExit() {
	sigs := make(chan os.Signal, 1)
	exit := make(chan bool, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGKILL, syscall.SIGTERM)

	go func() {
		sig := <-sigs
		log.Println()
		log.Println(sig)
		exit <- true
	}()

	<-exit
	log.Println("Disconnectiong from Discord")
	log.Println("Exiting from MoeBot...")
}

func parseConfig() {
	data, err := ioutil.ReadFile("./config/.config")
	if err != nil {
		log.Fatal(err)
	}
	pairs := strings.Split(string(data), "\n")
	for _, value := range pairs {
		if len(value) > 0 {
			line := strings.Split(value, "=")
			config[line[0]] = line[1]
		}
	}
}
