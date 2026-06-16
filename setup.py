from setuptools import setup

setup(
    name="termess",
    version="0.1.0",
    py_modules=["client", "connections", 'storage', 'server', 'not_collector'],
    install_requires=[
        "websockets",
        "prompt_toolkit",
        "pynacl",
        "plyer",
    ],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)