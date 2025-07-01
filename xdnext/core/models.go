package core

import (
	"time"
)

type User struct {
	ID           string   `json:"id"`           // either from the auth provider or internal to vseg
	Email        string   `json:"email"`        // this is a must field
	FirstName    string   `json:"firstname"`    // names can be elaborate ro it is split into two
	LastName     string   `json:"lastname"`     // second or last part of the name
	AuthProvider string   `json:"authprovider"` // e.g.Auth0, FireBase, KeyCloak
	Role         string   `json:"role"`         // Could be Admin, Contributor or Read-Only
	CreatedAt    string   `json:"createdat"`    // the date the user created vseg account access
	LastAccess   string   `json:"lastaccess"`   // Last login access to vseg for the user
	Realms       []string `json:"realms"`       // the realms for this user realm IDs
}

type Task struct {
	ID        string    `json:"id"`
	Text      string    `json:"text"`
	Completed bool      `json:"completed"`
	UID       string    `json:"uid"`
	Due       time.Time `json:"due"`
}

type Note struct {
	ID        string    `json:"id"`
	Content   string    `json:"content"`
	CreatedAt time.Time `json:"created_at"`
	UID       string    `json:"uid"`
}

type Clock interface {
	Now() time.Time
}

type realClock struct{}

func (realClock) Now() time.Time {
	return time.Now()
}

func NewClock() Clock {
	return &realClock{}
}
