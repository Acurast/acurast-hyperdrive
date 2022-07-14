import yaml
import os

CONFIG_PATH = os.getenv("CONFIG_PATH")

if CONFIG_PATH is None:
    print("A 'CONFIG_PATH' must be provided.")
    exit(1)

with open(CONFIG_PATH.strip(), "r") as file:
    deployment = yaml.safe_load(file)

    PRIVATE_KEY = os.getenv("PRIVATE_KEY")
    if PRIVATE_KEY is not None:
        deployment["pytezos"]["private_key"] = PRIVATE_KEY
