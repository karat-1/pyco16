import json
import os

from engine.core.engine_core_funcs import resource_path

CONFIG_LOC = resource_path("resources/config")

# Add Config containers below
config = {}

for file in os.listdir(CONFIG_LOC):
    if ".py" in file:
        continue
    f = open(CONFIG_LOC + "/" + file, "r")
    config[file.split(".")[0]] = json.load(f)
    f.close()
