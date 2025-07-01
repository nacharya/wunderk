package core

import (
	"time"

	"github.com/gin-gonic/gin"
)

type Mroutes struct {
	Router *gin.Engine
}

var Mr Mroutes

type Config struct {
	Name    string `json:"name"`
	Verbose bool   `json:"verbose"`
	Addr    string `json:"addr"`
	Datavol string `json:"datavol"`
	Users   string `json:"users"`
	Tasks   string `json:"tasks"`
	Loglevel string `json:"loglevel"`
}

type Event struct {
	Update time.Time `json:"update"`
}
