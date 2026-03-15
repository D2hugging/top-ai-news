import os
import yaml

LOCAL_LLM_URL = os.getenv("LOCAL_LLM_URL")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not LOCAL_LLM_URL and not GOOGLE_API_KEY:
    raise RuntimeError("please set GOOGLE_API_KEY or LOCAL_LLM_URL")

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.yaml")


def reload_config():
    with open(_CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    CONFIG.clear()
    CONFIG.update(data)


with open(_CONFIG_PATH) as f:
    CONFIG = yaml.safe_load(f)
