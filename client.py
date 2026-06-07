import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter 
import json
from pathlib import Path
import argparse
import websockets
from connections import listen, connect, chat
import sys 
from nacl.public import PrivateKey, PublicKey, Box
import ipaddress
import base64
import time
from storage import *
import urllib.request
from datetime import datetime, timezone, timedelta


first_message = 'welcome_to_termess'
menu = ''



    
def contacts_for_completer():
    try:
        contacts = dict.fromkeys(tuple(load_contacts()))
        return contacts
    except:
        return None


def is_ipv4(ip_str):
    try:
        ip_obj = ipaddress.ip_address(ip_str)
        return ip_obj.version == 4
    except ValueError:
        return False

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
    
    remove = subparsers.add_parser("remove", aliases=["rm"], help="add <username> <ip>")
    remove.add_argument("username", default=None, nargs="?")

    add = subparsers.add_parser("add", help="add <username> <ip>")
    add.add_argument("username", default=None, nargs="?")
    add.add_argument("ip", default=None, nargs="?")
    add.add_argument("port", default=None, nargs="?")
    add.add_argument("pubkey", default=None, nargs="?")

    subparsers.add_parser("contacts", help="show contacts")
    subparsers.add_parser("test")
    subparsers.add_parser("update")

    subparsers.add_parser("ip", help="show your ip")

    init = subparsers.add_parser("init")
    init.add_argument("username", nargs="?", default=None)
    init.add_argument("port", nargs="?", default=None)
    init.add_argument("timezone", nargs="?", default=None)
    
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
    elif args.command == "update":
        import subprocess
        subprocess.run([
            str(Path(sys.executable).parent / "pip"),
            "install", "--force-reinstall",
            "git+https://github.com/grayshark-same/termess.git"
        ])
    elif args.command in ["remove", 'rm'] :
        try:
            username = args.username if args.username else input('please, enter username: ')
            remove_contact(username)
        except:
            pass
    elif args.command == "add":
        try:
            username = args.username if args.username else input('please, enter username: ')
            ip = args.ip if args.ip else input('please, enter ipv4 of your contact: ')
            while not is_ipv4(ip):
                ip = input('please, enter correct ipv4 of your contact: ')
                
            port = 2727
            try:
                port_input = args.port if args.port else input(f'please, enter port for your contact(default {port}): ')
                if port_input:
                    port = int(port_input)
            except ValueError:
                pass
            pub_key = args.pubkey 
           
            save_contact({username: {'ip': ip,
                                    'port': port,
                                    'pub_key': pub_key}})
        except:
            print('something went wrong')
    elif args.command == "ip":
        ip = urllib.request.urlopen('https://ifconfig.me').read().decode()
        print(ip)        
    elif args.command == "contacts":
        print(load_contacts())
    elif args.command == "test":
        print(int(time.time()))
    elif args.command == "init":
        username = args.username if args.username else input('please, enter your username: ')
        port = 2727
        try:
            port = int(args.port if args.port else input(f'please, enter port for termess(default {port}): '))
        except:
            pass
        try:
            tz = int(args.timezone if args.timezone else input(f'please, enter your timezone (UTC+-X): '))
        except:
            tz = 0
        # tz = timezone(timedelta(hours=hours))
        priv_key = PrivateKey.generate()
        pub_key = priv_key.public_key
        pub_key_str = base64.b64encode(bytes(pub_key)).decode()
        priv_key_str = base64.b64encode(bytes(priv_key)).decode()
        save_config({'username': username, 'port': port, 'pub_key': pub_key_str, "priv_key": priv_key_str, 'tz': tz})
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
    