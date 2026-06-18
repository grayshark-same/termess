import asyncio
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import NestedCompleter 
import json
from pathlib import Path
import argparse
import websockets
from connections import listen, connect, connect_server, chat
import sys 
from nacl.public import PrivateKey, PublicKey, Box
from nacl.signing import SigningKey, VerifyKey
from nacl.encoding import Base64Encoder
import ipaddress
import base64
import time
from storage import *
import urllib.request
from datetime import datetime, timezone, timedelta
from prompt_toolkit.patch_stdout import patch_stdout
from connections import *
import os

first_message = 'welcome_to_termess'
menu = ''



    
def contacts_for_completer():
    try:
        contacts = dict.fromkeys(tuple(load_contacts()))
        return contacts
    except:
        return None


contacts = None

completer = NestedCompleter.from_nested_dict({
    "/chat": contacts_for_completer(),
    "/add": {'client':None, 'server':None},
    "/quit": None
})

async def main(username=None):
    print(first_message)
    notifications = await get_notifications()
    if notifications:
        for sender, count in notifications.items():
            print(f"  {sender}: {count} new messages")
    session = PromptSession(completer=completer)
    print(f'trying to connect to {username}...') if username else None
    if username:
        try:
            user = username
            contact = load_contacts()[user]
            host = contact["ip"]
            port = int(contact["port"])
            if contact.get("type") == "server":
                await connect_server(host, port, user)
            else:
                await connect(host, port, user)
        except IndexError:
            print('username is incorrect, please, write: /message_to <username>')
        username = None

    with patch_stdout():
        while True:
            text = await session.prompt_async(">> ") #like input()

            if text.startswith('/chat'):
                try:
                    user = text.split()[1]
                    contact = load_contacts()[user]
                    host = contact["ip"]
                    port = int(contact["port"])
                    if contact.get("type") == "server":
                        await connect_server(host, port, user)
                    else:
                        await connect(host, port, user)
                except IndexError:
                    print("please, write: /message_to <username>")
            elif text.startswith('/quit'):
                print('\n termess stopped')
                break
            elif text.startswith("/add"):
                splitted = text.split()
                add_contact(Type=splitted[1])
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

    add = subparsers.add_parser("add", help="add <type of connection(client/server)> <username> <ip> <port>")
    add.add_argument("type_of_connection", choices=["server", "client"], help='type of connection(client/server)')
    add.add_argument("username", default=None, nargs="?")
    add.add_argument("ip", default=None, nargs="?")
    add.add_argument("port", default=None, nargs="?")

    subparsers.add_parser("contacts", help="show contacts")
    subparsers.add_parser("test")
    subparsers.add_parser("update")
    subparsers.add_parser("version", help="show version")
    subparsers.add_parser("ip", help="show your ip")
    subparsers.add_parser("notifications", aliases=["not"], help="show your notifications")

    init = subparsers.add_parser("init")
    init.add_argument("username", nargs="?", default=None)
    init.add_argument("port", nargs="?", default=None)
    init.add_argument("timezone", nargs="?", default=None)
    
    listen_cmd = subparsers.add_parser("listen")
    listen_cmd.add_argument("port", type=int, default=load_config()["port"], nargs="?")

    connect_cmd = subparsers.add_parser("connect")
    connect_cmd.add_argument("username")
    connect_cmd.add_argument("port", type=int, default=load_config()["port"], nargs="?")
    
    
    server_cmd = subparsers.add_parser("server", help="start server")
    server_cmd.add_argument("action", nargs="?", choices=["start", "stop", "restart", "logs"], default="start")
    server_cmd.add_argument("port", type=int, default=None, nargs="?")

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
    elif args.command == ["not", 'notifications']:
        result = None
        notifications = get_notifications()
        for name, count in notifications.items():
            result = str(result) + f'{name}: {count}\n'
        text = result or 'you have no notifications'
        print(text)
    elif args.command == "add":
        add_contact(Type=args.type_of_connection, un=args.username, ip=args.ip, port=args.port)
    elif args.command == "version":
        from importlib.metadata import version
        print(version("termess"))
    elif args.command == "ip":
        ip = urllib.request.urlopen('https://ifconfig.me').read().decode()
        print(ip)        
    elif args.command == "contacts":
        print(load_contacts())
    elif args.command == "test":
        notifs = asyncio.run(get_notifications())
        print(notifs)
        for name, count in notifs.items():
            print(count)
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
        existing = load_config()
        if existing.get("pub_key") and existing.get("priv_key"):
            pub_key_str = existing["pub_key"]
            priv_key_str = existing["priv_key"]
        else:
            priv_key = PrivateKey.generate()
            pub_key = priv_key.public_key
            pub_key_str = base64.b64encode(bytes(pub_key)).decode()
            priv_key_str = base64.b64encode(bytes(priv_key)).decode()
        if existing.get("signing_key"):
            signing_key_str = existing["signing_key"]
        else:
            signing_key = SigningKey.generate()
            signing_key_str = base64.b64encode(bytes(signing_key)).decode()
        save_config({'username': username, 'port': port, 'pub_key': pub_key_str, "priv_key": priv_key_str, 'tz': tz, 'signing_key': signing_key_str})
        import subprocess
        script = str(BASE_DIR / "not_collector.py")
        if sys.platform == "win32":
            pythonw = str(Path(sys.executable).parent / "pythonw.exe")
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "termess-daemon", 0, winreg.REG_SZ, f'"{pythonw}" "{script}"')
            winreg.CloseKey(key)
        else:
            service = f"""[Unit]
Description=termess daemon

[Service]
ExecStart={sys.executable} {script}
Restart=always

[Install]
WantedBy=default.target
"""
            service_path = Path.home() / ".config/systemd/user/termess.service"
            service_path.parent.mkdir(parents=True, exist_ok=True)
            service_path.write_text(service)
            subprocess.run(["systemctl", "--user", "enable", "--now", "termess"])
        print("autostart enabled")
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
    elif args.command == "server":
        import subprocess, signal
        pid_file = BASE_DIR / "server.pid"
        log_file = BASE_DIR / "server.log"

        def server_stop():
            if not pid_file.exists():
                print("server is not running")
                return False
            pid = int(pid_file.read_text())
            try:
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/PID", str(pid)], capture_output=True)
                else:
                    os.kill(pid, signal.SIGTERM)
                pid_file.unlink()
                print("server stopped")
                return True
            except (ProcessLookupError, OSError):
                pid_file.unlink(missing_ok=True)
                print("server was not running")
                return False

        action = args.action or "start"

        if action == "stop":
            server_stop()
        elif action == "logs":
            if log_file.exists():
                lines = log_file.read_text().splitlines()
                print("\n".join(lines[-50:]))
            else:
                print("no logs yet")
        elif action in ("start", "restart"):
            if action == "restart":
                server_stop()
            port = args.port or 2727
            server_script = str(BASE_DIR / "server.py")
            with open(log_file, "a") as log:
                if sys.platform == "win32":
                    proc = subprocess.Popen(
                        [sys.executable, server_script, str(port)],
                        stdout=log, stderr=log,
                        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
                    )
                else:
                    proc = subprocess.Popen(
                        [sys.executable, server_script, str(port)],
                        stdout=log, stderr=log,
                        start_new_session=True
                    )
            pid_file.write_text(str(proc.pid))
            print(f"server started (pid {proc.pid}), port {port}")
    