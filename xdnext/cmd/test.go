package cmd

import (
	"errors"
	"fmt"
	"xdnext/core"

	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
)

var testCmd = &cobra.Command{
	Use:   "test",
	Short: "Initialize the settings for the tsx server ",
	Long:  `Initialize the settings for the tsx server`,
	Run: func(cmd *cobra.Command, args []string) {

		if len(args) > 0 {
			fmt.Println("Starting ", args[0], " tests ...")
			testname := args[0]
			err := InitDB()
			if err != nil {
				fmt.Println("Unable to access DB ", err)
				return
			}
			fmt.Println(testname, " tests ...")
			if testname == "user" {
				fmt.Println("User tests")
				UserTest(Cfg)
			} else if testname == "task" {
				fmt.Println("Task tests")
				TaskTest(Cfg)
			} else if testname == "notes" {
				fmt.Println("Notes tests")
			} else if testname == "show" {
				fmt.Println("Show tests")
				ShowTest(Cfg)
			} else {
				fmt.Println("Unknown test ", testname)
				fmt.Println("test [ user | task | notes ]")
				return
			}
			fmt.Println("Tests completed")
		} else {
			fmt.Println("test [ user | task | notes ]")
		}
	},
}

func init() {
	rootCmd.AddCommand(testCmd)
}

func UserTest(Cfg core.Config) {
	var user core.User

	user.ID = "FFFFFE"
	user.Email = "me@funnybar"
	user.FirstName = "MeMe"
	user.LastName = "FunnyMan"

	var err error
	var uaccess core.UserAccess
	// Add a Record
	err = uaccess.UpdateUser(core.Userdb, user)
	if err != nil {
		log.Errorln(err)
		return
	}
	// Get a record
	u, err := uaccess.GetUser(core.Userdb, "FFFFFE")
	if err != nil {
		log.Errorln(err)
		return
	}
	log.Println("User: ", u)
	// Update the record
	u.FirstName = "hola"
	err = uaccess.UpdateUser(core.Userdb, u)
	if err != nil {
		log.Errorln(err)
		return
	}
	log.Println("User: ", u)
	// delete
	err = uaccess.RemoveUser(core.Userdb, "FFFFFE")
	if err != nil {
		log.Errorln(err)
		return
	}
	// get
	log.Println("Looking for ", "FFFFFE")
	u, err = uaccess.GetUser(core.Userdb, "FFFFFE")
	if err == nil {
		log.Errorln(err)
		return
	}
	fmt.Println("User tests completed")
}

func TaskTest(cfg core.Config) {

	var task core.Task

	task.ID = "ABCDEFABCDEF"
	task.Text = "Keep moving"
	task.UID = "FFFFFF"
	task.Completed = false

	var taccess core.TaskAccess
	// Add a Record
	err := taccess.AddTask(core.Taskdb, task)
	if err != nil {
		log.Errorln(err)
		return
	}
	// Get a record
	ID := "ABCDEFABCDEF"
	UID := "FFFFFF"
	t, err := taccess.GetTask(core.Taskdb, UID, ID)
	if err != nil {
		log.Errorln(err)
		return
	}
	if t.ID != task.ID {
		log.Errorln(errors.New("Mismatched ID"))
		return
	}
	task.Text = "Foo bar update"
	// Update the record
	err = taccess.UpdateTask(core.Taskdb, task)
	if err != nil {
		log.Errorln(err)
		return
	}
	// delete
	err = taccess.DeleteTask(core.Taskdb, UID, ID)
	if err != nil {
		log.Errorln(err)
		return
	}
	// get
	t, err = taccess.GetTask(core.Taskdb, UID, ID)
	if err == nil {
		log.Errorln(err)
		return
	}
	fmt.Println("Task tests completed")
}

func ShowTest(Cfg core.Config) {

	var uaccess core.UserAccess
	userlist := uaccess.GetUsers(core.Userdb)
	for k, v := range userlist {
		fmt.Println(k, " = ", v)
	}

	var taccess core.TaskAccess
	tasks := taccess.ListTasks(core.Taskdb)
	for k, v := range tasks {
		fmt.Println(k, " = ", v)
	}
}
