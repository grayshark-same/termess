# termess

Terminal messenger with P2P and relay server support, E2E encryption (NaCl/X25519).

## Installation

**Linux (Debian/Ubuntu, Arch, Fedora)**
```bash
curl -sSL https://raw.githubusercontent.com/grayshark-same/termess/main/install.sh | bash
source ~/.bashrc
```

**Windows**
```powershell
Invoke-RestMethod "https://raw.githubusercontent.com/grayshark-same/termess/main/install.ps1" -OutFile install.ps1; .\install.ps1
```

## Setup

```
termess init
```

Enter your username, port (default: 2727), and timezone (UTC offset). This generates your encryption keys and sets up the notification daemon to autostart.

For P2P mode, make sure your port is open:
```bash
sudo ufw allow 2727
```

## Commands

| Command | Description |
|---|---|
| `termess init [username] [port] [timezone]` | Set up username, port, timezone and generate keys |
| `termess start` | Open termess (shows unread message counts) |
| `termess chat <username>` | Open chat with contact |
| `termess add client <username> <ip> [port]` | Add P2P contact |
| `termess add server <username> <ip> [port]` | Add relay server contact |
| `termess remove <username>` | Remove contact |
| `termess contacts` | Show contacts |
| `termess ip` | Show your external IP |
| `termess update` | Update termess |

### Server management

| Command | Description |
|---|---|
| `termess server start [port]` | Start relay server in background |
| `termess server stop` | Stop relay server |
| `termess server restart [port]` | Restart relay server |
| `termess server logs` | Show last 50 lines of server log |

### In chat

| Command | Description |
|---|---|
| `/chat <username>` | Start chat with contact |
| `/quit` | Exit chat |

## Notifications

termess runs a background daemon (`not_collector.py`) that checks for new messages every 60 seconds and shows a system notification. It is set up automatically on `termess init`.

To restart the daemon manually:

**Windows**
```powershell
Get-WmiObject Win32_Process -Filter "name='pythonw.exe'" | Stop-Process -Force
Start-Process pythonw "C:\path\to\not_collector.py" -WindowStyle Hidden
```

**Linux**
```bash
systemctl --user restart termess
```

Custom notification sound: place `notification.wav` next to the termess files.

## Connection modes

### P2P
Both users run `termess chat <username>`. The first becomes the listener, the second connects automatically. Requires at least one side to have a real external IP (not behind CGNAT).

### Relay server
Add a contact with type `server` pointing to a running relay server. Both users connect to the server — it routes messages between them. Works behind any NAT.

To run your own relay server:
```
termess server start 2727
```

## How it works

- Keys are generated locally on `termess init` and preserved on re-init
- On connect, each client registers its public key with the server
- Before chatting, clients fetch each other's public key and perform X25519 key exchange
- All messages are encrypted with NaCl Box (XSalsa20-Poly1305) — the server only sees ciphertext
- Offline messages are queued on the server and delivered when the recipient reconnects
