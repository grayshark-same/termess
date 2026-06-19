from setuptools import setup

setup(
    name="termess",
    version="1.0.0",
    py_modules=["client", "connections", 'storage', 'server', 'not_collector'],
    install_requires=[
        "websockets",
        "prompt_toolkit",
        "pynacl",
        "plyer",
        "aiosqlite",
    ],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)