package router

import (
	"net/http"
	"xdnext/core"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func GetTask(c *gin.Context) {
	log.Println("GetTask")
	uid := c.Param("user_id")
	task_id := c.Param("task_id")
	if (len(uid) > 0) && (len(task_id) > 0) {
		log.Debug("task_id: ", task_id, " uid: ", uid)
	}
	log.Println("Task ID: ", task_id, " UID: ", uid)
	var taccess core.TaskAccess
	task, err := taccess.GetTask(core.Taskdb, uid, task_id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error ": err.Error()})
	} else {
		c.IndentedJSON(http.StatusOK, task)
	}
}

func AddTask(c *gin.Context) {
	uid := c.Param("user_id")
	task_id := c.Query("task_id")
	if (len(task_id) > 0) && (len(uid) > 0) {
		log.Debug("id: ", task_id, " uid: ", uid)
	}
	var task core.Task
	if err := c.BindJSON(&task); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Bad request"})
		return
	}
	log.Println("Task: ", task)
	var taccess core.TaskAccess
	err := taccess.AddTask(core.Taskdb, task)
	if err == nil {
		c.IndentedJSON(http.StatusCreated, task)
	} else {
		c.JSON(http.StatusNotFound, gin.H{"error ": "Unable to add task"})
	}
}

func UpdateTask(c *gin.Context) {
	uid := c.Param("user_id")
	task_id := c.Param("task_id")
	if (len(task_id) > 0) && (len(uid) > 0) {
		log.Debug("task_id: ", task_id, " uid: ", uid)
	}
	var task core.Task
	if err := c.BindJSON(&task); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Bad request"})
		return
	}
	var taccess core.TaskAccess
	log.Println("Task: ", task)
	err := taccess.UpdateTask(core.Taskdb, task)
	if err == nil {
		c.IndentedJSON(http.StatusCreated, task)
	} else {
		c.JSON(http.StatusNotFound, gin.H{"error ": "ID Not Found"})
	}
}

func DeleteTask(c *gin.Context) {
	uid := c.Param("user_id")
	task_id := c.Param("task_id")
	if (len(task_id) > 0) && (len(uid) > 0) {
		log.Debug("task: ", task_id, " uid: ", uid)
	}
	var taccess core.TaskAccess
	err := taccess.DeleteTask(core.Taskdb, uid, task_id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error ": "Unable to delete User"})
	} else {
		c.IndentedJSON(http.StatusOK, task_id)
	}
}

func GetTasks(c *gin.Context) {
	log.Println("GetTasks")
	uid := c.Param("user_id")
	if len(uid) == 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User ID is required"})
		return
	}
	log.Println("Fetching tasks for user ID: ", uid)
	var taccess core.TaskAccess
	tasks, err := taccess.GetTasksForUser(core.Taskdb, uid)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Tasks not found for the user"})
	} else {
		c.IndentedJSON(http.StatusOK, tasks)
	}
}
