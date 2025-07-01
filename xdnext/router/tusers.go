package router

import (
	"net/http"
	"xdnext/core"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func GetUser(c *gin.Context) {
	user_id := c.Param("user_id")
	if len(user_id) > 0 {
		log.Debug("user_id: ", user_id)
	}
	log.Println("GetUser ", user_id)
	uaccess := core.UserAccess{}
	user, err := uaccess.GetUser(core.Userdb, user_id)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error ": "User Not Found"})
	} else {
		c.IndentedJSON(http.StatusOK, user)
	}
}

func DeleteUser(c *gin.Context) {
	user_id := c.Param("user_id")
	if len(user_id) > 0 {
		log.Debug("user_id: ", user_id)
	}
	uaccess := core.UserAccess{}
	err := uaccess.RemoveUser(core.Userdb, user_id)
	if err != nil {
		log.Error("Unable to remove "+user_id, err)
		c.JSON(http.StatusNotFound, gin.H{"error ": "Unable to delete User"})
	} else {
		c.IndentedJSON(http.StatusOK, user_id)
	}

}

func UpdateUser(c *gin.Context) {
	user_id := c.Param("user_id")
	if len(user_id) > 0 {
		log.Debug("user_id: ", user_id)
	}
	var user core.User
	if err := c.BindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Bad request"})
		return
	}
	uaccess := core.UserAccess{}
	err := uaccess.UpdateUser(core.Userdb, user)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error ": "ID Not Found"})
	} else {
		c.IndentedJSON(http.StatusCreated, user_id)
	}
}
