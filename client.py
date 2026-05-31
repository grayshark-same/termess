import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter 
import json
from pathlib import Path


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
    with open("contacts.json", "r") as f:
        return json.load(f)

def contacts_for_completer():
    contacts = tuple(load_contacts())
    return contacts


contacts = None

completer = NestedCompleter.from_nested_dict({
    "/message": contacts,
    "/peer": {
        "add": contacts,
        "remove": contacts,
    },
    "/menu": None,
    "/help": None,
    "/reg": None
})

async def main():
    print(first_message)
    session = PromptSession(completer=completer)
    while True:
        text = await session.prompt_async(">> ") #like input()
        if text.startswith('/reg'):
            username = input('please, enter your username: ')
            save_config({'username': username})
            print(f'your username {username}')
        elif text.startswith('/help'):
            print(f'there should be guide, but im so lazy')
        elif text.startswith('/menu'):
            pass
        elif text.startswith('/message'):
            try: 
                _, group, contact = text.split()
                print(group, contact)
            except ValueError: 
                print("please, write: /message <contact>")
        elif text.startswith('/peer'):
            try: 
                state = text.split()[1]
                if state == 'add':
                    try:
                        contact, ip = text.split()[2:4]
                        save_contact({contact : ip})
                        
                    except ValueError: 
                        print("please, write: /peer add <contact> <ip>")
                    
            except IndexError: 
                print("please, write: /peer <state>")
        elif text == "/test":
            # global contacts
            # contacts = {'aaa':None}
            print(contacts_for_completer())
        
            

        


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('\n termess stopped')