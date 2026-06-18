import json
import base64
from pathlib import Path
from nacl.public import PrivateKey, PublicKey
from nacl.signing import SigningKey, VerifyKey
import ipaddress
import sys, os

BASE_DIR = Path(__file__).parent

DEFAULT_CONFIG = {
    "username": None,
    "port": 2727,
    "pub_key": None,
    "priv_key": None,
    'tz': None
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

def get_signing_key():
    conf = load_config()
    return SigningKey(base64.b64decode(conf['signing_key']))

def add_contact(Type="client", un=None, ip=None, port=None):
    try:
        if Type in ['client', 'server']:
            text ={'client': '', 'server': 'server with '}
            username = un or input('please, enter username: ')
            Ip = ip or input(f'please, enter ipv4 of {text[Type]}your contact: ')
            while not is_ipv4(Ip):
                Ip = input(f'please, enter correct ipv4 of {text[Type]}your contact: ')
            try:
                Port = port or input(f'please, enter port for {text[Type]}your contact(default 2727): ') or 2727
            except ValueError:
                pass
        
            save_contact({username: {'ip': Ip,
                                    'port': Port,
                                    'type': Type}})
        else:
            print('please, write add <type of connection(client/server)>')
    except:
        print('something went wrong')

def is_ipv4(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.version == 4
    except ValueError:
        return False
    
def beep():
    wav = BASE_DIR / "notification.wav"
    if not wav.exists():
        return
    try:
        if sys.platform == 'win32':
            import winsound
            winsound.PlaySound(str(wav), winsound.SND_FILENAME | winsound.SND_ASYNC)
        else:
            import subprocess
            subprocess.Popen(['aplay', '-q', str(wav)])
    except Exception:
        pass