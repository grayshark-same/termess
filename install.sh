#!/bin/bash

echo "Installing termess..."

install_python() {
    if command -v apt-get &> /dev/null; then
        sudo apt-get update && sudo apt-get install -y python3 python3-pip
    elif command -v pacman &> /dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3 python3-pip
    else
        echo "Unsupported distro. Install Python manually: https://python.org"
        exit 1
    fi
}

if ! command -v python3 &> /dev/null; then
    echo "Python not found, installing..."
    install_python
fi

if ! command -v pip3 &> /dev/null; then
    install_python
fi

pip3 install git+https://github.com/grayshark-same/termess.git

export PATH="$HOME/.local/bin:$PATH"
if ! grep -q '.local/bin' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

echo "Done! Run: termess init"
