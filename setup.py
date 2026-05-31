from setuptools import setup

setup(
    name="termess",
    py_modules=["client", "connections"],
    entry_points={
        "console_scripts": [
            "termess=client:run",
        ],
    },
)
