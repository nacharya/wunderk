# MCP specific code
import json
import os

from loguru import logger


class MCPInstance:
    def __init__(self, name, instance):
        self.name = name
        try:
            self.parse(instance)
        except ValueError as e:
            logger.error(f"Error parsing MCP instance {name}: {e}")
            raise

    def parse(self, instance):
        if "type" not in instance:
            if "url" or "serverUrl" in instance:
                self.type = "sse"
            else:
                self.type = "stdio"
        else:
            self.type = instance["type"]

        if self.type == "stdio":
            if "command" not in instance:
                raise ValueError(f"Missing 'command' for stdio instance {self.name}")
            else:
                self.command = instance["command"]
            if "args" in instance:
                self.args = instance["args"]
            else:
                self.args = []
            if "env" in instance:
                self.env = instance["env"]
            if "timeout" in instance:
                self.timeout = instance["timeout"]
            else:
                self.timeout = 3000  # Default timeout in milliseconds
        elif self.type == "sse" or "http" or "streamable-http":
            self.command = None
            self.args = []
            self.env = {}
            self.url = None
            self.headers = {}
            self.timeout = 3000  # Default timeout in milliseconds
            self.sse_read_timeout = 5000  # Default SSE read timeout in milliseconds
            if "url" in instance:
                self.url = instance["url"]
            elif "serverUrl" in instance:
                self.url = instance["serverUrl"]

            if "headers" in instance:
                self.headers = instance["headers"]
            else:
                self.headers = {}
            if "timeout" in instance:
                self.timeout = instance["timeout"]
            else:
                self.timeout = 3000  # Default timeout in milliseconds
            if "sse_read_timeout" in instance:
                self.sse_read_timeout = instance["sse_read_timeout"]
            else:
                self.sse_read_timeout = 5000

            if "transport" in instance:
                self.transport = instance["transport"]

        if instance.get("iconPath"):
            self.iconPath = instance["iconPath"]

    def log(self):
        logger.debug(f"Instance Name: {self.name}")
        logger.debug(f"Instance Type: {self.type}")
        if self.type == "stdio":
            logger.debug(f"Command: {self.command}")
            logger.debug(f"Arguments: {self.args}")
            logger.debug(f"Environment: {self.env}")
            logger.debug(f"Timeout: {self.timeout} ms")
        elif self.type in ["sse", "http", "streamable-http"]:
            logger.debug(f"URL: {self.url}")
            logger.debug(f"Headers: {self.headers}")
            logger.debug(f"Timeout: {self.timeout} ms")
            logger.debug(f"SSE Read Timeout: {self.sse_read_timeout} ms")
            if hasattr(self, "transport"):
                logger.debug(f"Transport: {self.transport}")


class MCPConfig:
    def __init__(self, filename):
        if filename.startswith("~"):
            filename = os.path.expanduser(filename)
        self.filename = filename
        self.config = self.load_config()
        self.validate_config()
        self.mcp_servers = [
            MCPInstance(name, instance)
            for name, instance in self.config.get("mcpServers", {}).items()
        ]

    def json(self):
        return self.config

    def load_config(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError(
                f"Configuration file {self.filename} does not exist."
            )
        with open(self.filename, "r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON format in {self.filename}: {e}")

    def validate_config(self):
        required_keys = ["mcpServers", "nativeMCPServers"]
        logger.debug(f"{self.config.keys()}")
        for key in required_keys:
            if not self.config.get(key):
                raise KeyError(
                    f"Missing required key: {key} in configuration file {self.filename}"
                )

    def get_mcp_names(self):
        mlist = list(self.config.get("mcpServers", {}).keys())
        logger.debug(f"Available MCP instances: {mlist}")
        return mlist

    def get_mcp_instance(self, name):
        for instance in self.mcp_servers:
            if instance.name == name:
                return instance
        raise ValueError(f"MCP instance with name {name} not found.")
