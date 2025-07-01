#!/bin/bash

function setup() {
        echo "Setting up the virtual environment..."
        if [ -d ".venv" ]; then
            echo "Virtual environment already exists. Skipping creation."
        else
            uv venv .venv --python 3.12
            source .venv/bin/activate
            uv pip install -r requirements.txt
            echo "Virtual environment created."
        fi
}

function clean() {
	echo "Cleaning up the virtual environment..."
	if [ -d ".venv" ]; then
		rm -rf .venv
		echo "Virtual environment removed."
	else
		echo "No virtual environment found to clean."
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

function run() {
	if [ -f wui.py ]; then
		echo "Running the web UI..."
		source .venv/bin/activate
		streamlit run wui.py --server.port 9702
			#--server.enableCORS false \
			#--server.enableXsrfProtection false \
			#--server.baseUrlPath / 
	else
		echo "No wui.py found. Cannot run the web UI."
	fi
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

UTIL=$(basename $0)

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
	"run")
		shift
		run "$@"
		exit 0
		;;
    -h | --help)
        usage
        exit 0
        ;;
    *)
		echo $UTIL " : Unknown command :" $1
        exit 1
        ;;
esac
