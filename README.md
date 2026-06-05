# termess

Terminal messenger with P2P connection and E2E encryption (NaCl/X25519).

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

Enter your username and port (default: 2727). This generates your encryption keys.

Make sure port `2727` (or your custom port) is open in your firewall:
```bash
sudo ufw allow 2727
```

## Commands

| Command | Description |
|---|---|
| `termess init [username] [port]` | Set up username, port and generate keys |
| `termess start` | Open termess |
| `termess chat <username>` | Chat with contact |
| `termess add <username> <ip> [port]` | Add contact |
| `termess remove <username>` | Remove contact |
| `termess contacts` | Show contacts |
| `termess ip` | Show your external IP |
| `termess update` | Update termess |

### In chat

| Command | Description |
|---|---|
| `/chat <username>` | Start chat with contact |
| `/quit` | Exit chat |

## How it works

Both users run `termess chat <username>`. The first one becomes the server and waits — the second connects automatically. Keys are exchanged automatically on connect, all messages are encrypted end-to-end.

Requires port `2727` (or your custom port) to be open on the listening side.
