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

Enter your username, port (default: 2727), and timezone (UTC offset). This generates your encryption keys.

For P2P mode, make sure your port is open:
```bash
sudo ufw allow 2727
```

## Commands

| Command | Description |
|---|---|
| `termess init [username] [port] [timezone]` | Set up username, port, timezone and generate keys |
| `termess start` | Open termess (shows unread notifications) |
| `termess chat <username>` | Chat with contact |
| `termess add client <username> <ip> [port]` | Add P2P contact |
| `termess add server <username> <ip> [port]` | Add relay server contact |
| `termess remove <username>` | Remove contact |
| `termess contacts` | Show contacts |
| `termess ip` | Show your external IP |
| `termess update` | Update termess |
| `termess server [port]` | Start a relay server |

### In chat

| Command | Description |
|---|---|
| `/chat <username>` | Start chat with contact |
| `/quit` | Exit chat |

## Connection modes

### P2P
Both users run `termess chat <username>`. The first becomes the listener, the second connects automatically. Requires at least one side to have a real external IP (not behind CGNAT).

### Relay server
Add a contact with type `server` pointing to a running relay server. Both users connect to the server — it routes messages between them. Works behind any NAT. Messages are still encrypted end-to-end (keys are exchanged through the server but never stored in plaintext).

To run your own relay server:
```
termess server 2727
```

## How it works

- Keys are generated locally on `termess init`
- On connect, each client registers its public key with the server
- Before chatting, clients fetch each other's public key from the server and perform X25519 key exchange
- All messages are encrypted with NaCl Box (XSalsa20-Poly1305) — the server only sees ciphertext
- Offline messages are queued on the server and delivered when the recipient reconnects
