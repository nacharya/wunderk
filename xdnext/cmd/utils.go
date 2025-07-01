package cmd

import (
	"encoding/json"
	"fmt"
	"io"
	"os"
	"time"
	"xdnext/core"

	"github.com/gin-gonic/contrib/ginrus"
	"github.com/gin-gonic/gin"
	log "github.com/sirupsen/logrus"
)

type ConfigFile interface {
	GetConfigFile() (string, error)
	ReadConfigFile(filename string) (*core.Config, error)
	WriteConfigFile(filename string, config *core.Config) error
}
type JSONConfigFile struct{}

func (j *JSONConfigFile) GetConfigFile() (string, error) {
	var cfile string = ""

	home, err := os.UserHomeDir()
	if err != nil {
		log.Error(err)
		return "", err
	}
	log.Debug("Home directory: ", home)
	filename := home + "/.config/xdnext/config.json"
	_, err = os.Stat(filename)
	if err == nil {
		cfile = filename
	} else if os.IsNotExist(err) {
		log.Println("Config file not found: %s", filename, "\n")
		cfile = "/app" + "/" + "xdnext.json"
	}
	log.Println("Using config file: ", cfile, "\n")
	return cfile, nil
}

func (j *JSONConfigFile) ReadConfigFile(filename string) (*core.Config, error) {
	data, err := os.ReadFile(filename)
	if err != nil {
		return nil, err
	}

	var config core.Config
	err = json.Unmarshal(data, &config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}

func (j *JSONConfigFile) WriteConfigFile(filename string, config *core.Config) error {
	data, err := json.MarshalIndent(config, "", "  ")
	if err != nil {
		return err
	}

	err = os.WriteFile(filename, data, 0644)
	if err != nil {
		return err
	}

	return nil
}

func ConfigInit() error {

	// Create an instance of the JSONConfigFile
	jsonConfigFile := &JSONConfigFile{}
	cfile, err := jsonConfigFile.GetConfigFile()
	if err != nil {
		return err
	}
	readConfig, err := jsonConfigFile.ReadConfigFile(cfile)
	if err != nil {
		log.Println("Error reading config file:", err)
		return err
	}
	Cfg = *readConfig
	return nil
}

func LoggerInit(logfile string, verbose bool) (*log.Logger, *os.File) {
	logger := log.New()

	if verbose {
		logger.Level = log.TraceLevel
	} else {
		logger.Level = log.InfoLevel
	}

	log.SetFormatter(&log.TextFormatter{
		DisableColors: true,
		FullTimestamp: false,
	})
	log.SetReportCaller(true)

	lf, err := os.Create(logfile)
	if err != nil {
		fmt.Println("Unable to create logfile ", logfile, " ", err)
		return logger, lf
	}
	log.SetOutput(lf)
	log.StandardLogger().Out = lf
	// Start a separate goroutine to flush logs periodically
	go func() {
		for range time.Tick(time.Second) {
			if file, ok := log.StandardLogger().Out.(*os.File); ok {
				file.Sync()
			}
		}
	}()

	return logger, lf
}

func GinFrameworkInit(logger *log.Logger, lf *os.File) {
	gin.DisableConsoleColor()
	gin.SetMode(gin.ReleaseMode)
	core.Mr.Router = gin.New()
	core.Mr.Router.Use(ginrus.Ginrus(logger, time.RFC3339, false))
	gin.DefaultWriter = io.MultiWriter(lf)
}
