package cmd

import (
	"os"
	"xdnext/core"
	"xdnext/router"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

// cfgCmd represents the cfg command
var serverCmd = &cobra.Command{
	Use:   "server",
	Short: "Work with starting and stopping the xdatanext server ",
	Long:  `Work with starting and stopping the xdatanext server`,
	Run: func(cmd *cobra.Command, args []string) {
		if len(args) == 0 {
			cmd.Help()
			os.Exit(0)
		}
	},
}

var serverStartCmd = &cobra.Command{
	Use:   "start",
	Short: "Work with starting and stopping the farmexec service ",
	Long:  `Work with starting and stopping the farmexec service`,
	Run: func(cmd *cobra.Command, args []string) {
		var addr string = ":9901"
		if Cfg.Name == "xdatanext" {
			addr = Cfg.Addr
			log.Println("Using ", addr)
		}

		err := InitDB()
		if err != nil {
			log.Println("Unable to access DB")
			return
		}
		router.ServerRouter(core.Mr.Router, Cfg)
	},
}

func init() {
	rootCmd.AddCommand(serverCmd)
	serverCmd.AddCommand(serverStartCmd)
}

func InitDB() error {
	var err error
	// Now initialize the DB
	log.Println("Starting to initialize ...")

	core.Userdb, err = core.UserDbxInit(Cfg)
	if err != nil {
		log.Error("Error: ", err)
		return err
	}
	core.Taskdb, err = core.TaskDbxInit(Cfg)
	if err != nil {
		log.Error("Error: ", err)
		return err
	}
	log.Println("Init done !")
	return nil
}
