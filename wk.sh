#!/bin/bash

function setup() {
        echo "Setting up the virtual environment..."
        if [ -d "${HOME}/.nvenv" ]; then
            echo "Virtual environment already exists. Skipping creation."
        else
            uv venv "${HOME}"/.nvenv --python 3.12
            source "${HOME}"/.nvenv/bin/activate
            uv pip install -r wui/requirements.txt
            echo "Virtual environment created."
        fi
	echo "Creating networks for containers"
	docker network create --driver bridge wundernet || echo "Network wundernet already exists."
	docker network ls | grep wundernet || echo "Failed to create or find the network."

}

function clean() {
	echo "Cleaning up the virtual environment..."
	if [ -d "${HOME}/.nvenv" ]; then
		rm -rf "${HOME}/.nvenv"
		echo "Virtual environment removed."
	else
		echo "No virtual environment found to clean."
	fi
	if docker network ls | grep -q wundernet; then
		docker network rm wundernet || echo "Failed to remove the network."
	else
		echo "No wundernet found to clean."
	fi
}

function deptree() {
	echo "Generating dependency tree..."
	if [ -f pyproject.toml ]; then
		uv tree
	else
		echo "No pyproject.toml found. Cannot generate dependency tree."
	fi
}

function start() {
	echo "Starting "
	docker-compose -f docker-compose.yml up -d
}

function stop() {
	echo "Stopping "
	docker-compose -f docker-compose.yml down
}

function shell() {
	if [ -z "$1" ]; then
		echo "No container name provided. Usage: $0 shell <container_name>"
		exit 1
	fi
	ctr="$1"
	echo "Starting a shell in the container $ctr"
	docker exec -it "$ctr" /bin/bash
}

function llm_cmd() {
	echo "LLM command area"
	if [ -z "$1" ]; then
		echo "No LLM command provided. Usage: $0 llm <command>"
		exit 1
	fi
	# Placeholder for LLM commands
	echo "Executing LLM command: $1"
	case "$1" in
	    "list")
		docker exec -ti wunderk-ollama /usr/bin/ollama list
		;;
	    "pull")
		if [ -z "$2" ]; then
			echo "No model name provided. Usage: $0 llm pull <model_name>"
			exit 1
		fi
		docker exec -ti wunderk-ollama /usr/bin/ollama pull "$2"
		;;
	    "*")
		echo "Unknown LLM command: $1"
		echo "Available commands: list, pull <model_name>"
		exit 1
		;;
	esac
}


usage() {
cat << EOF
$UTIL COMMAND

Commands are:

setup
	- Create the venv and all the packages needed

clean
	- Cleanup the venv used locally via uv 

deptree
	- Current status of uv and venv

-h, --help	- Show this help screen

EOF
}

UTIL=$(basename "${0}")

if [ $# -eq 0 ]; then
	usage
	exit 0
fi


case $1 in
	"setup")
		shift
		setup "$@"
		exit 0
		;;
	"clean")
		shift
		clean "$@"
		exit 0
		;;
	"deptree")
		shift
		deptree "$@"
		exit 0
		;;
	"start")
		shift
		start "$@"
		exit 0
		;;
	"stop")
		shift
		stop "$@"
		exit 0
		;;
	"shell")
		shift
		shell "$@"
		exit 0
		;;
	"llm")
		shift
		echo "LLM area"
		llm_cmd "$@"
		exit 0
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		echo "$UTIL" " : Unknown command :" "$1"
		exit 1
		;;
esac
