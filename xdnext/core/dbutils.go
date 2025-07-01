package core

import (
	md5 "crypto/md5"
	"crypto/sha256"
	"encoding/base64"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"time"

	"github.com/boltdb/bolt"
	"github.com/glebarez/sqlite"
	"gorm.io/gorm/logger"

	// "github.com/glebarez/sqlite"
	log "github.com/sirupsen/logrus"
	"gorm.io/gorm"
)

type UserAccess struct{}
type NoteAccess struct{}

var Userdb *bolt.DB
var Notedb *bolt.DB

type TaskAccess struct{}

var Taskdb *gorm.DB

// Create a ID based on a string if the ID is not available
func (c UserAccess) GetUserID(username string) []byte {
	h := sha256.New()
	h.Write([]byte(username))
	hash := base64.URLEncoding.EncodeToString(h.Sum(nil))
	userid := string(hash[:])
	return []byte(userid)
}

func (c UserAccess) GetUsers(db *bolt.DB) []User {

	bucket := "Users"
	numr := 0
	_ = db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		Stats := b.Stats()
		numr = Stats.KeyN
		return nil
	})

	var users = make([]User, numr)

	index := 0
	_ = db.View(func(tx *bolt.Tx) error {
		// Assume bucket exists and has keys
		b := tx.Bucket([]byte(bucket))
		b.ForEach(func(k, v []byte) error {
			var user User
			json.Unmarshal(v, &user)
			users[index] = user
			index++
			return nil
		})
		return nil
	})

	return users
}

func (c UserAccess) GetUser(db *bolt.DB, ID string) (User, error) {

	var user User
	var err error

	log.Println("Looking for > ", ID)
	key := ID
	bucket := "Users"
	_ = db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		v := b.Get([]byte(key))
		if v == nil {
			log.Error(key, ": Not Found\n", key)
			err = errors.New("not found")
			return err
		}
		if len(v) > 0 {
			json.Unmarshal(v, &user)
		}
		return err
	})
	log.Println("User: ", user)
	return user, err
}

func (c UserAccess) AddUser(db *bolt.DB, User User) error {

	bucket := "Users"
	key := User.ID
	val, _ := json.Marshal(User)
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Put([]byte(key), val)
		return err
	})
	return err
}

func (c UserAccess) UpdateUser(db *bolt.DB, User User) error {

	bucket := "Users"

	key := User.ID
	log.Info("Updating uid: " + key)
	// User.ID = string(key)
	val, _ := json.Marshal(User)
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Put([]byte(key), val)
		return err
	})

	return err
}

func (c UserAccess) RemoveUser(db *bolt.DB, ID string) error {

	key := ID
	bucket := "Users"
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Delete([]byte(key))
		return err
	})
	return err
}

type dbTask struct {
	gorm.Model
	ID        string    `json:"id"`        // ID of the task itself
	Text      string    `json:"text"`      // Content of the Task
	Completed bool      `json:"completed"` // of this is completed
	Due       time.Time `json:"due"`       // Due date
	UID       string    `json:"uid"`       // User ID to which this belongs
}

func CreateTableTask(db *gorm.DB) error {
	log.Info("Creating Tasks")
	db.AutoMigrate(&dbTask{})
	// Create
	db.Create(&dbTask{ID: "24242424", Text: "Have fun", Completed: true,
		Due: time.Now(), UID: "BDE455687CADDE",
	})
	var task dbTask
	db.First(&task, "ID = ?", "24242424")
	db.Model(&task).Update("Text", "Eat Lunch!")
	db.First(&task, "24242424")
	// db.Delete(&task)
	db.Commit()

	return nil
}

func (t TaskAccess) ListTasks(db *gorm.DB) []Task {
	var dtasks []dbTask
	var tasks []Task
	db.Find(&dtasks)
	for _, item := range dtasks {
		var task Task
		task.ID = item.ID
		task.Text = item.Text
		task.Completed = item.Completed
		task.Due = item.Due
		task.UID = item.UID
		tasks = append(tasks, task)
	}
	return tasks
}

func (taccess TaskAccess) AddTask(db *gorm.DB, task Task) error {
	log.Debug("Adding task ", task.ID)

	dtask := dbTask{ID: task.ID, Text: task.Text,
		Completed: task.Completed, Due: task.Due, UID: task.UID}
	// db.Clauses(clause.Insert{Modifier: "or ignore"})
	err := db.Transaction(func(tx *gorm.DB) error {
		if err := tx.Create(&dtask).Error; err != nil {
			log.Error(err)
			return err
		}
		return nil
	})

	return err
}

func (taccess TaskAccess) UpdateTask(db *gorm.DB, task Task) error {
	log.Debug("Updating task ", task.ID)

	var dbTask dbTask

	dbTask.ID = task.ID
	dbTask.Text = task.Text
	dbTask.Completed = task.Completed
	dbTask.Due = task.Due
	dbTask.UID = task.UID

	result := db.Model(&dbTask).Updates(map[string]interface{}{"ID": task.ID, "Text": task.Text,
		"Completed": task.Completed, "Due": task.Due, "UID": task.UID})

	if result.Error != nil {
		log.Errorln(result.Error)
		return result.Error
	}

	return nil
}

func (taccess TaskAccess) DeleteTask(db *gorm.DB, UID string, TID string) error {
	log.Debug("Deleting task ", TID, " for user ", UID)
	var dbTask dbTask
	dbTask.ID = TID
	dbTask.Text = ""
	dbTask.Completed = false
	dbTask.Due = time.Now()
	dbTask.UID = UID

	// result := db.Delete(&dbTask{}, ID)
	// result := db.Where("id = ?", ID).Delete(&dbTask{})
	// Delete completely without considering DeletedAt
	result := db.Unscoped().Delete(&dbTask)
	if result.Error != nil {
		log.Errorln(result.Error)
		return result.Error
	}
	return nil
}

func (taccess TaskAccess) GetTasksForUser(db *gorm.DB, UID string) ([]Task, error) {
	log.Println("Get tasks for user ", UID)
	var dtasks []dbTask
	var tasks []Task

	// result := db.Find(&dtasks, "uid = ?", UID)
	result := db.Where("UID = ?", UID).Find(&dtasks)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		log.Error(result.Error)
		return tasks, result.Error
	}
	for _, item := range dtasks {
		var task Task
		task.ID = item.ID
		task.Text = item.Text
		task.Completed = item.Completed
		task.Due = item.Due
		task.UID = item.UID
		tasks = append(tasks, task)
	}
	return tasks, nil
}
func (taccess TaskAccess) GetTask(db *gorm.DB, UID string, TID string) (Task, error) {
	log.Debug("Get task ", TID, " for user ", UID)
	var task Task
	var dbTask dbTask

	result := db.First(&dbTask, "ID = ?", TID)
	if errors.Is(result.Error, gorm.ErrRecordNotFound) {
		log.Error(result.Error)
		return task, result.Error
	}
	if UID != dbTask.UID {
		log.Error("User ID does not match")
		return task, errors.New("user ID does not match")
	}
	task.ID = dbTask.ID
	task.Text = dbTask.Text
	task.Completed = dbTask.Completed
	task.Due = dbTask.Due
	task.UID = dbTask.UID
	return task, nil
}

type dbNote struct {
	gorm.Model
	ID        string `json:"id"`
	Content   string `json:"content"`
	CreatedAt string `json:"created_at"`
}

func (n NoteAccess) RemoveNote(db *bolt.DB, ID string) error {

	key := ID
	bucket := "Notes"
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Delete([]byte(key))
		return err
	})
	return err
}

func (n NoteAccess) UpdateNote(db *bolt.DB, Note Note) error {

	bucket := "Notes"

	key := Note.ID
	log.Info("Updating nid: " + key)
	val, _ := json.Marshal(Note)
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Put([]byte(key), val)
		return err
	})

	return err
}

func (n NoteAccess) GetNote(db *bolt.DB, ID string) (Note, error) {

	var note Note
	var err error

	key := ID
	bucket := "Notes"
	_ = db.View(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		v := b.Get([]byte(key))
		if v == nil {
			log.Error(key, ": Not Found\n", key)
			err = errors.New("not found")
			return err
		}
		if len(v) > 0 {
			json.Unmarshal(v, &note)
		}
		return err
	})
	return note, err
}

func (n NoteAccess) AddNote(db *bolt.DB, Note Note) error {

	bucket := "Notes"

	key := Note.ID
	val, _ := json.Marshal(Note)
	var err error
	_ = db.Update(func(tx *bolt.Tx) error {
		b := tx.Bucket([]byte(bucket))
		err = b.Put([]byte(key), val)
		return err
	})
	return err
}

func GetMD5Hash(text string) string {
	hash := md5.Sum([]byte(text))
	return hex.EncodeToString(hash[:])
}

func UserDbxInit(Cfg Config) (*bolt.DB, error) {

	dbpath := Cfg.Datavol + "/" + "users.db"
	var bdb *bolt.DB

	if _, err := os.Stat(dbpath); os.IsNotExist(err) {
		bdb, err = OpenBolt(dbpath)
		if err != nil {
			log.Error(err)
			return nil, err
		}
		bucket := "Users"
		Bucket_create(bdb, bucket)
		bucket = "Notes"
		Bucket_create(bdb, bucket)

	} else {
		bdb, err = OpenBolt(dbpath)
		if err != nil {
			log.Error(err)
			return nil, err
		}
	}
	var uaccess UserAccess
	var user User
	user.ID = "BDE455687CADDE"
	user.Email = "foo@bar"
	user.FirstName = "Foo"
	user.LastName = "Bar"
	user.Realms = []string{"Realm1", "dc64eb006aa3d785d44b5bad84389b45"}
	user.CreatedAt = time.Now().String()
	user.LastAccess = time.Now().String()
	user.AuthProvider = "Firebase"
	user.Role = "Owner"
	uaccess.AddUser(bdb, user)
	return bdb, nil
}

func TaskDbxInit(Cfg Config) (*gorm.DB, error) {

	var dbhandle *gorm.DB
	dbpath := Cfg.Datavol + "/" + "tasks.db"
	if _, err := os.Stat(dbpath); os.IsNotExist(err) {
		dbhandle, err = ConnectDB(dbpath)
		if err != nil {
			log.Error(err)
			return nil, err
		}
		if err = CreateTableTask(dbhandle); err != nil {
			log.Error(err)
			return nil, err
		}
	} else {
		dbhandle, err = OpenSQL(dbpath)
		if err != nil {
			log.Error(err)
			return nil, err
		}
	}
	return dbhandle, nil
}

func ConnectDB(path string) (*gorm.DB, error) {

	db, err := gorm.Open(sqlite.Open(path), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Info),
	})
	if err != nil {
		log.Error("Failed to connect to database: ", path)
		return nil, err
	}
	Formatter := new(log.TextFormatter)
	log.SetFormatter(Formatter)
	Formatter.FullTimestamp = true

	// db.Automigrate(&core.Task{})
	return db, nil
}

func OpenBolt(dbname string) (*bolt.DB, error) {

	db, err := bolt.Open(dbname, 0600, nil)
	if err != nil {
		log.Fatalln("Error: ", dbname, " ", err)
		return db, err
	}
	return db, nil
}

func CloseBolt(bdb *bolt.DB) {
	defer bdb.Close()
}

func OpenSQL(dbname string) (*gorm.DB, error) {
	db, err := ConnectDB(dbname)
	if err != nil {
		log.Error(err)
		return nil, err
	}
	return db, nil
}

func CloseSQL(sdb *gorm.DB) {
	db, _ := sdb.DB()
	db.Close()
}

func Bucket_create(db *bolt.DB, bucket string) {
	_ = db.Update(func(tx *bolt.Tx) error {
		_, err := tx.CreateBucketIfNotExists([]byte(bucket))
		if err != nil {
			return fmt.Errorf("create bucket: %s", err)
		}
		return nil
	})
}

func Bucket_delete(db *bolt.DB, bucket string) {
	_ = db.Update(func(tx *bolt.Tx) error {
		err := tx.DeleteBucket([]byte(bucket))
		if err != nil {
			return fmt.Errorf("delete bucket: %s", err)
		}
		return nil
	})
}

func Bucket_show(db *bolt.DB, bucket string) {
	_ = db.View(func(tx *bolt.Tx) error {
		// Assume bucket exists and has keys
		b := tx.Bucket([]byte(bucket))

		b.ForEach(func(k, v []byte) error {
			fmt.Printf("key=%s, value=%s\n", k, v)
			return nil
		})
		return nil
	})
}

func Bucket_list(db *bolt.DB, bucket string) {
	_ = db.View(func(tx *bolt.Tx) error {
		// Assume bucket exists and has keys
		b := tx.Bucket([]byte(bucket))

		b.ForEach(func(k, v []byte) error {
			fmt.Println(string(v))
			return nil
		})
		return nil
	})
}
