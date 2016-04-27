package main

import (
	"fmt"
	"os"
	"os/signal"
	"strings"
	"time"

	"github.com/bwmarrin/discordgo"
)

func init() {
	config.DiscordToken = os.Getenv("DISCORD_KEY")
	//config.Debug = os.Getenv("STATE") == "debug"
    config.Debug = true
}

func main() {
	discord, err := discordgo.New(config.DiscordToken)
	if err != nil {
		fmt.Println(err)
		return
	}
	// Get the account information.
	u, err := discord.User("@me")
	if err != nil {
		fmt.Println("error obtaining account details,", err)
	}

	// Store the account ID for later use.
	config.BotID = u.ID

	discord.AddHandler(messageCreate)

	err = discord.Open()
	if err != nil {
		fmt.Println(err)
	}

	fmt.Println("MoeBot is up and running!")
	handleExit()
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	// log message
	if config.Debug {
		fmt.Printf("%20s %10s %10s > %s\n", m.ChannelID, time.Now().Format(time.Stamp), m.Author.Username, m.Content)
	}
	if m.Author.ID != config.BotID {
		parseMessage(s, m)
	}
}

func parseMessage(session *discordgo.Session, message *discordgo.MessageCreate) {
	content := strings.ToLower(message.Content)
	if strings.HasPrefix(content, "hi moebot") || strings.HasPrefix(content, "hello moebot") {
		session.ChannelMessageSend(message.ChannelID, "Hello "+message.Author.Username+"!")
	} else if strings.HasPrefix(content, "moebot what's moe") || strings.HasPrefix(content, "moebot what is moe") {
		session.ChannelMessageSend(message.ChannelID, "Check this out: https://vimeo.com/70285271")
	}
}

func handleExit() {
	sigs := make(chan os.Signal, 1)
	exit := make(chan bool, 1)
	signal.Notify(sigs)

	go func() {
		sig := <-sigs
		fmt.Println()
		fmt.Println(sig)
		exit <- true
	}()

	<-exit
	fmt.Println("Disconnectiong from Discord")
	fmt.Println("Exiting from MoeBot...")
}

var config struct {
	Debug        bool
	DiscordToken string
	BotID        string
}
