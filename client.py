import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter 
import json
from pathlib import Path
import argparse
import websockets
from connections import listen, connect, chat
BASE_DIR = Path(__file__).parent




first_message = 'welcome_to_termess'
menu = ''
DEFAULT_CONFIG = {
    "username": None,
    "port": 2727
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

def load_contacts():
    try:
        with open(BASE_DIR / "contacts.json", "r") as f:
            return json.load(f)
    except:
        return {}
    
def contacts_for_completer():
    try:
        contacts = dict.fromkeys(tuple(load_contacts()))
        return contacts
    except:
        return None



contacts = None

completer = NestedCompleter.from_nested_dict({
    "/chat": contacts_for_completer(),
    "/quit": None
})

async def main(username=None):
    print(first_message)
    session = PromptSession(completer=completer)
    print(f'trying to connect to {username}...') if username else None
    if username:
        try:
            user = username
            host = load_contacts()[user]["ip"]
            port = int(load_contacts()[user]["port"])
            await connect(host, port, user)
        except IndexError:
            print('username is incorrect, please, write: /message_to <username>')
        username = None
        
    while True:
        text = await session.prompt_async(">> ") #like input()
    
        if text.startswith('/chat'):
            try:
                user = text.split()[1]
                host = load_contacts()[user]["ip"]
                port = int(load_contacts()[user]["port"])
                await connect(host, port, user)
            except IndexError:
                print("please, write: /message_to <username>")
        elif text.startswith('/quit'):
            print('\n termess stopped')
            break
        elif text == "/test":
            # global contacts
            # contacts = {'aaa':None}
            pass
        
            

        

def run():
    parser = argparse.ArgumentParser(prog="termess")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("start", help="start")

    chat = subparsers.add_parser("chat", help="open chat")
    chat.add_argument("username",default=None, help=f'it can be one of your contact {list(load_contacts())}')
    
    add = subparsers.add_parser("add", help="add <username> <ip>")
    add.add_argument("username")
    add.add_argument("ip")
    add.add_argument("port")

    subparsers.add_parser("contacts", help="show contacts")
    subparsers.add_parser("test")

    init = subparsers.add_parser("init")
    init.add_argument("username", nargs="?", default=None)
    init.add_argument("port", nargs="?", default=None)
    
    listen_cmd = subparsers.add_parser("listen")
    listen_cmd.add_argument("port", type=int, default=load_config()["port"], nargs="?")

    connect_cmd = subparsers.add_parser("connect")
    connect_cmd.add_argument("username")
    connect_cmd.add_argument("port", type=int, default=load_config()["port"], nargs="?")
    
    args = parser.parse_args()
    # print(args.command)
    if args.command == "chat" or args.command == "start":
        username = args.username if args.command == "chat" else None
        # print(username)
        try:
            asyncio.run(main(username=username))
        except KeyboardInterrupt:
            print('\n termess stopped')
    elif args.command == "add":
        try:
            save_contact({args.username: {'ip': args.ip,
                                    'port': args.port}})
        except:
            pass
    elif args.command == "contacts":
        print(load_contacts())
    elif args.command == "test":
        print(load_contacts()[args.username]["ip"])
    elif args.command == "init":
        username = args.username if args.username else input('please, enter your username: ')
        port = 2727
        try:
            port = int(args.port if args.port else input(f'please, enter port for termess(default {port}): '))
        except:
            pass
        save_config({'username': username, 'port': port})
    elif args.command == "listen":
        username = load_config().get("username", "unknown")
        try:
            asyncio.run(listen(args.port, username))
        except KeyboardInterrupt:
            print('\ntermess stopped')
    elif args.command == "connect":
        try:
            username = args.username
            host = load_contacts()[username]["ip"]
            port = args.port if args.port else load_contacts()[args.username]["port"]
            asyncio.run(connect(host=host, port=port, username=username))
            print('connecting')
        except ValueError as e:
            print(e)
    