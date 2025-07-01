package router

import (
	"net/http"
	"xdnext/core"

	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

func BaseServer_Handlers(mr *gin.Engine) {
	mr.GET("/healthcheck", func(c *gin.Context) {
		c.JSON(
			http.StatusOK,
			gin.H{
				"status": "ok",
			},
		)
	})

	mr.GET("/ready", func(c *gin.Context) {
		c.JSON(
			http.StatusOK,
			gin.H{
				"status": "ok",
			},
		)
	})

	mr.GET("/live", func(c *gin.Context) {
		c.JSON(
			http.StatusOK,
			gin.H{
				"status": "ok",
			},
		)
	})

}

func APIServer_Handlers(mr *gin.Engine) {
	log.Println("APIServer_Handlers")
	apigroup := mr.Group("/api/v1")
	// User routes
	apigroup.GET("/user/:user_id", GetUser)
	apigroup.PUT("/user/:user_id", UpdateUser)
	apigroup.DELETE("/user/:user_id", DeleteUser)

	// Task routes for Users
	apigroup.GET("/user/:user_id/tasks/:task_id", GetTask)
	apigroup.DELETE("/user/:user_id/tasks/:task_id", DeleteTask)
	apigroup.GET("/user/:user_id/tasks", GetTasks)
	apigroup.PUT("/user/:user_id/tasks/:task_id", UpdateTask)

}

func ServerRouter(mr *gin.Engine, Cfg core.Config) {
	mr.Use(gin.Recovery())
	BaseServer_Handlers(mr)
	APIServer_Handlers(mr)
	log.Println("Listening on ", Cfg.Addr)
	mr.Run(Cfg.Addr)
}
