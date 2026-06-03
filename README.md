# termess

Terminal messenger with P2P connection.

## Installation

**Linux (Debian/Ubuntu, Arch, Fedora)**
```bash
curl -sSL https://raw.githubusercontent.com/grayshark-same/termess/main/install.sh | bash
```

**Windows**
```powershell
irm https://raw.githubusercontent.com/grayshark-same/termess/main/install.ps1 | iex
```

## Setup

```
termess init
```

Enter your username and port (default: 2727).

## Commands

| Command | Description |
|---|---|
| `termess start` | Open termess |
| `termess init [username] [port]` | Set up username and port |
| `termess add <username> <ip> <port>` | Add contact |
| `termess contacts` | Show contacts |
| `termess chat <username>` | Chat with contact |

### In chat

| Command | Description |
|---|---|
| `/chat <username>` | Start chat with contact |
| `/quit` | Exit chat |

## How it works

Both users run `termess chat <username>`. The first one to run becomes the server and waits — the second one connects automatically.

Requires port `2727` (or your custom port) to be open on the listening side.
