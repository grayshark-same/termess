from setuptools import setup

setup(
    name="termess",
    py_modules=["client", "connections", 'storage', 'server'],
    install_requires=[
        "websockets",
        "prompt_toolkit",
        "pynacl",
    ],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)