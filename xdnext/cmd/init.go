package cmd

import (
	"fmt"

	"github.com/spf13/cobra"
)

var initCmd = &cobra.Command{
	Use:   "init",
	Short: "Initialize the settings for the tsx server ",
	Long:  `Initialize the settings for the tsx server`,
	Run: func(cmd *cobra.Command, args []string) {
		err := InitDB()
		if err != nil {
			fmt.Println("Unable to access DB")
			return
		}
	},
}

func init() {
	rootCmd.AddCommand(initCmd)
}
