#!/bin/bash

VERSION=${1:-main}
echo "Installing termess ${VERSION}..."

install_python() {
    if command -v apt-get &> /dev/null; then
        [ "$EUID" -eq 0 ] && apt-get install -y python3 python3-pip python3-venv || sudo apt-get install -y python3 python3-pip python3-venv
    elif command -v pacman &> /dev/null; then
        [ "$EUID" -eq 0 ] && pacman -Sy --noconfirm python python-pip || sudo pacman -Sy --noconfirm python python-pip
    elif command -v dnf &> /dev/null; then
        [ "$EUID" -eq 0 ] && dnf install -y python3 python3-pip || sudo dnf install -y python3 python3-pip
    else
        echo "Unsupported distro. Install Python manually: https://python.org"
        exit 1
    fi
}

if ! command -v python3 &> /dev/null; then
    echo "Python not found, installing..."
    install_python
fi

if command -v apt-get &> /dev/null; then
    [ "$EUID" -eq 0 ] && apt-get install -y python3-venv || sudo apt-get install -y python3-venv
fi

python3 -m venv ~/.termess-venv
~/.termess-venv/bin/pip install git+https://github.com/grayshark-same/termess.git@$VERSION

mkdir -p ~/.local/bin
ln -sf ~/.termess-venv/bin/termess ~/.local/bin/termess

if ! grep -q '.local/bin' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

export PATH="$HOME/.local/bin:$PATH"

echo "Done! Run: termess init"
