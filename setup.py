from setuptools import setup

setup(
    name="termess",
    py_modules=["client", "connections"],
    install_requires=[
        "websockets",
        "prompt_toolkit",
    ],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)