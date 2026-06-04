import json
import base64
from pathlib import Path
from nacl.public import PrivateKey, PublicKey

BASE_DIR = Path(__file__).parent

DEFAULT_CONFIG = {
    "username": None,
    "port": 2727,
    "pub_key": None,
    "priv_key": None,
}

def save_config(config: dict):
    with open(BASE_DIR / "config.json", "w") as f:
        json.dump(config, f, indent=2)

def load_config():
    if not (BASE_DIR / "config.json").exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open(BASE_DIR / "config.json", "r") as f:
        return json.load(f)

def save_contact(contact: dict):
    contacts = contact
    if (BASE_DIR / "contacts.json").exists():
        contacts = load_contacts()
        contacts.update(contact)
    with open(BASE_DIR / "contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

def remove_contact(username: str):
    contacts = load_contacts()
    if username in contacts:
        del contacts[username]
        with open(BASE_DIR / "contacts.json", "w") as f:
            json.dump(contacts, f, indent=2)
    else:
        print(f"{username} not found")

def load_contacts():
    try:
        with open(BASE_DIR / "contacts.json", "r") as f:
            return json.load(f)
    except:
        return {}

def get_keys():
    conf = load_config()
    priv_key = PrivateKey(base64.b64decode(conf['priv_key']))
    pub_key = PublicKey(base64.b64decode(conf['pub_key']))
    return (pub_key, priv_key)
