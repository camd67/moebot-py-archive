package main

import
//"net/http"
//"os"

(
	"fmt"
	"time"

	"github.com/bwmarrin/discordgo"
)

//"github.com/gin-gonic/gin"

func main() {
	/*
		port := os.Getenv("PORT")

		if port == "" {
			log.Fatal("$PORT must be set")
		}

		router := gin.New()
		router.Use(gin.Logger())
		router.LoadHTMLGlob("templates/*.tmpl.html")
		router.Static("/static", "static")

		router.GET("/", func(c *gin.Context) {
			c.HTML(http.StatusOK, "index.tmpl.html", nil)
		})

		router.Run(":" + port)
	*/
	discord, err := discordgo.New("MTcyNDk1ODI2MjY0OTE1OTY4.Cf8JQg.b5nU5Y6qOUYQwejYPcq0shaGHdk")
	if err != nil {
		fmt.Println(err)
		return
	}
	discord.AddHandler(messageCreate)

	err = discord.Open()
	if err != nil {
		fmt.Println(err)
	}

	fmt.Printf("bot is running, press CTRL+C to exit")
	<-make(chan struct{})
	return
}

func messageCreate(s *discordgo.Session, m *discordgo.MessageCreate) {
	fmt.Printf("%20s %20s %20s > %s\n", m.ChannelID, time.Now().Format(time.Stamp), m.Author.Username, m.Content)
}
