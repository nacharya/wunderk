import json
import sys
import os
import pprint
from loguru import logger
from pathlib import Path


class Config:
    def __init__(self, filename):
        self.filename = filename
        with open(filename, "r") as f:
            self.jfile = json.load(f)

    def getv(self, name):
        return self.jfile[name]

    def setv(self, name, value):
        self.jfile[name] = value

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.jfile, f, indent=4)

    def json(self):
        return self.jfile

    def show(self):
        pprint.pprint(self.jfile)


def ConfigInit(name):
    filename = "/app/config/wunderk/wui.json"
    if not os.path.exists(filename):
        filename = os.path.expanduser("~/.config/wui/wui.json")
        if not os.path.exists(os.path.expanduser(filename)):
            os.makedirs(os.path.expanduser("~/.config/wui"), exist_ok=True)
            os.system("cp wui.json ~/.config/wui/wui.json")
    else:
        filename = os.path.expanduser(filename)
    cfg = Config(filename)
    keys = cfg.getv("keys")
    keys["OpenAI"] = os.getenv("OPENAI_API_KEY")
    keys["Google"] = os.getenv("GOOGLE_API_KEY")
    keys["Anthropic"] = os.getenv("ANTHROPIC_API_KEY")
    cfg.setv("keys", keys)
    loglevel = cfg.getv("loglevel")
    logger.add(sys.stderr, format="{time} {level} {message}", level=loglevel)
    logger.add(f"{name}.log")
    return cfg


if __name__ == "__main__":
    cfg = ConfigInit()
    config = cfg.json()
    QDRANT_URL = f"http://{config['qdrant']['host']}:{config['qdrant']['port']}"
    print("QDRANT_URL: ", QDRANT_URL)
