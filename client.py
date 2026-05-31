import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter 
import json
from pathlib import Path
from setuptools import setup
import argparse




first_message = 'welcome_to_termess'
menu = ''
DEFAULT_CONFIG = {
    "username": None,
    }



def save_config(config: dict):
    with open("config.json", "w") as f:
        json.dump(config, f, indent=2)

def load_config():
    if not Path("config.json").exists():
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    with open("config.json", "r") as f:
        return json.load(f)
    
def save_contact(contact: dict):
    contacts = contact
    if Path("contacts.json").exists():
        contacts = load_contacts()
        contacts.update(contact)
    with open("contacts.json", "w") as f:
        json.dump(contacts, f, indent=2)

def load_contacts():
    try:
        with open("contacts.json", "r") as f:
            return json.load(f)
    except:
        return None
def contacts_for_completer():
    contacts = dict.fromkeys(tuple(load_contacts()))
    return contacts

contacts = None

completer = NestedCompleter.from_nested_dict({
    "/message_to": contacts_for_completer(),
    "/quit": None
})

async def main(username=None):
    print(first_message)
    session = PromptSession(completer=completer)
    print(username)
    while True:
        text = await session.prompt_async(">> ") #like input()
        if username:
            user = username
            username = None
            
        elif text.startswith('/message_to'):
            print('a')
            try:
                user = text.split()[1]
                print(user)
            except IndexError:
                print("please, write: /message_to <username>")
        elif text.startswith('/quit'):
            print('\n termess stopped')
            break
        #     username = input('please, enter your username: ')
        #     save_config({'username': username})
        #     print(f'your username {username}')
        # elif text.startswith('/help'):
        #     print(f'there should be guide, but im so lazy')
        # elif text.startswith('/menu'):
        #     pass
        # elif text.startswith('/message'):
        #     try: 
        #         _, group, contact = text.split()
        #         print(group, contact)
        #     except ValueError: 
        #         print("please, write: /message <contact>")
        # elif text.startswith('/peer'):
        #     try: 
        #         state = text.split()[1]
        #         if state == 'add':
        #             try:
        #                 contact, ip = text.split()[2:4]
        #                 save_contact({contact : ip})
                        
        #             except ValueError: 
        #                 print("please, write: /peer add <contact> <ip>")
                    
        #     except IndexError: 
        #         print("please, write: /peer <state>")
        elif text == "/test":
            # global contacts
            # contacts = {'aaa':None}
            pass
        
            

        

def run():
    parser = argparse.ArgumentParser(prog="termess")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("start", help="start")
    message = subparsers.add_parser("message", help="message")
    message.add_argument("username", help=f'it can be one of your contact {load_contacts()}')
    
    add = subparsers.add_parser("add", help="add <username> <ip>")
    add.add_argument("username")
    add.add_argument("ip")

    subparsers.add_parser("contacts", help="show contacts")
    subparsers.add_parser("test")

    args = parser.parse_args()
    print(args.command)
    if args.command == "message" or args.command == "start":
        username = args.username if args.command == "message" else None
        # print(username)
        try:
            asyncio.run(main(username=username))
        except KeyboardInterrupt:
            print('\n termess stopped')
    elif args.command == "add":
        save_contact({args.username: args.ip})
        print(f"добавлен {args.username} -> {args.ip}")
    elif args.command == "contacts":
        print(load_contacts())
    elif args.command == "test":
        print(contacts_for_completer())